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
import logging
import asyncio

from app.db.session import get_db
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.core.security import verify_hmac_signature
from app.core.rate_limit import check_rate_limit
from app.core.forwarding import forward_webhook
from app.core.security_logger import log_security_event
from app.core.payload_integrity import calculate_payload_hash, detect_payload_changes
from app.core.config import settings
from app.schemas.webhook import WebhookRequest, WebhookResponse

logger = logging.getLogger(__name__)


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
    
    # Validate payload size
    if len(body) > settings.MAX_PAYLOAD_SIZE_BYTES:
        await log_security_event(
            db,
            provider_name,
            "payload_too_large",
            client_ip,
            request_id=request.headers.get("X-Request-ID"),
            details={"size": len(body), "max_allowed": settings.MAX_PAYLOAD_SIZE_BYTES}
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload size exceeds maximum of {settings.MAX_PAYLOAD_SIZE_BYTES} bytes"
        )
    
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
    
    # Calculate payload hash for integrity verification
    payload_hash = calculate_payload_hash(payload)
    
    # Store webhook event in database
    webhook_event = WebhookEvent(
        id=uuid.uuid4(),
        provider_id=provider.id,
        request_id=request_id,
        source=provider.name,
        payload=payload,
        payload_hash=payload_hash,
        headers=dict(request.headers),
        signature_valid=True,
        forwarded=False,
        received_at=datetime.utcnow()
    )
    
    db.add(webhook_event)
    await db.commit()
    await db.refresh(webhook_event)
    
    # Calculate analytics for this hour
    from app.core.analytics_calculator import calculate_webhook_analytics_for_hour
    from app.core.websocket_manager import ws_manager
    try:
        await calculate_webhook_analytics_for_hour(db, provider.id, datetime.utcnow())
    except Exception as e:
        logger.error(f"Failed to calculate analytics: {str(e)}")
    
    # Broadcast webhook event via WebSocket to all connected users
    await ws_manager.broadcast_to_all({
        "type": "webhook_event",
        "data": {
            "webhook_id": str(webhook_event.id),
            "provider_name": provider.name,
            "status": "received",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": webhook_event.request_id
        }
    })
    
    # Forward webhook to internal service (async, don't wait)
    # Pass webhook data instead of session to avoid session closure issues
    asyncio.create_task(
        forward_webhook(
            webhook_event.id,
            webhook_event.payload,
            webhook_event.request_id,
            provider.forwarding_url,
            settings.DATABASE_URL
        )
    )
    
    return WebhookResponse(
        status="accepted",
        message="Webhook received and queued for processing",
        webhook_id=str(webhook_event.id)
    )


@router.post("/verify/{webhook_id}", tags=["Webhooks"])
async def verify_webhook_integrity(
    webhook_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify if a webhook payload has been tampered with.

    Compares the provided payload against the stored hash.

    Args:
        webhook_id: ID of the webhook event
        payload: Current payload to verify
        db: Database session

    Returns:
        Verification result with tampering details
    """
    try:
        webhook_uuid = uuid.UUID(webhook_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook ID format"
        )

    # Get webhook from database
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.id == webhook_uuid)
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    # Calculate current hash
    current_hash = calculate_payload_hash(payload)

    # Compare hashes
    is_valid = current_hash == webhook.payload_hash

    if not is_valid:
        # Log tampering attempt
        changes = detect_payload_changes(webhook.payload, payload)
        await log_security_event(
            db,
            webhook.source,
            "payload_tampering_detected",
            "verification_check",
            request_id=webhook.request_id,
            details={
                "webhook_id": webhook_id,
                "expected_hash": webhook.payload_hash,
                "actual_hash": current_hash,
                "changes": changes
            }
        )

    return {
        "webhook_id": webhook_id,
        "is_valid": is_valid,
        "expected_hash": webhook.payload_hash,
        "actual_hash": current_hash,
        "tampering_detected": not is_valid,
        "changes": detect_payload_changes(webhook.payload, payload) if not is_valid else None
    }
