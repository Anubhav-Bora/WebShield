"""
Webhook ingestion routes.

Handles incoming webhooks from external providers with signature verification.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import json
import uuid

from app.db.session import get_db
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.core.security import verify_hmac_signature
from app.core.rate_limit import check_rate_limit
from app.core.forwarding import forward_webhook
from app.core.security_logger import log_security_event
from app.core.config import settings
from app.schemas.webhook import WebhookRequest, WebhookResponse
import asyncio


router = APIRouter()


@router.post("/{provider_name}", response_model=WebhookResponse, tags=["Webhooks"])
async def receive_webhook(
    provider_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive and process webhook from external provider.
    
    Steps:
    1. Extract signature and timestamp from headers
    2. Verify HMAC signature
    3. Validate timestamp (not too old)
    4. Store webhook event in database
    5. Return success response
    
    Args:
        provider_name: Name of the provider (e.g., 'stripe', 'github')
        request: FastAPI request object
        db: Database session
    
    Returns:
        WebhookResponse with status and webhook ID
    """
    
    # Get client IP address
    client_ip = request.client.host if request.client else "unknown"
    
    # Extract headers
    signature = request.headers.get("X-Signature")
    timestamp = request.headers.get("X-Timestamp")
    
    if not signature or not timestamp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Signature or X-Timestamp header"
        )
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Query provider to get secret key
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    # Check rate limit
    from app.main import redis_client

    allowed, rate_info = await check_rate_limit(
        redis_client,
        str(provider.id)
    )

    if not allowed:
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "rate_limit_exceeded",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"limit": rate_info["limit"], "reset_at": rate_info["reset_at"]}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Reset in {rate_info['reset_at']} seconds"
        )

    # Verify HMAC signature
    if not verify_hmac_signature(body, provider.secret_key, signature):
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "invalid_signature",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"signature": signature[:20] + "..."}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    # Validate timestamp
    try:
        webhook_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "invalid_timestamp",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"timestamp": timestamp}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp format"
        )

    now = datetime.now(webhook_timestamp.tzinfo)
    time_diff = (now - webhook_timestamp).total_seconds()

    if time_diff > settings.REPLAY_PROTECTION_WINDOW_SECONDS:
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "timestamp_too_old",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"time_diff": time_diff, "max_allowed": settings.REPLAY_PROTECTION_WINDOW_SECONDS}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook timestamp too old (replay protection)"
        )

    if time_diff < 0:
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "timestamp_in_future",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"time_diff": time_diff}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook timestamp is in the future"
        )
    
    # Check for replay attacks using Redis
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Request-ID header"
        )

    # Import redis_client from main
    from app.main import redis_client

    # Check if request_id already exists in Redis
    replay_key = f"webhook:{provider_name}:{request_id}"
    if await redis_client.exists(replay_key):
        # Log security event
        await log_security_event(
            db,
            provider_name,
            "replay_attempt",
            client_ip,
            request_id=request_id,
            details={"replay_key": replay_key}
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Webhook already processed (replay detected)"
        )

    # Store request_id in Redis with TTL = REPLAY_PROTECTION_WINDOW_SECONDS
    await redis_client.setex(
        replay_key,
        settings.REPLAY_PROTECTION_WINDOW_SECONDS,
        "processed"
    )
    
    # Parse webhook payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Store webhook event in database
    webhook_event = WebhookEvent(
        id=uuid.uuid4(),
        provider_id=provider.id,
        request_id=request_id,
        payload=payload,
        headers=dict(request.headers),
        signature_valid=True,
        forwarded=False,
        received_at=datetime.utcnow()
    )
    
    db.add(webhook_event)
    await db.commit()
    await db.refresh(webhook_event)
    
    # Forward webhook to internal service (async, don't wait)
    asyncio.create_task(
        forward_webhook(webhook_event, provider.forwarding_url, db)
    )
    
    return WebhookResponse(
        status="accepted",
        message="Webhook received and queued for processing",
        webhook_id=str(webhook_event.id)
    )
