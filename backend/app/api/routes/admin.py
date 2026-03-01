"""
Admin API routes for provider management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid
from typing import List

from app.db.session import get_db
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.db.models.security_log import SecurityLog
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse
from app.schemas.webhook import WebhookEventResponse
from app.schemas.security_log import SecurityLogResponse


router = APIRouter()


@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(db: AsyncSession = Depends(get_db)):
    """List all webhook providers."""
    stmt = select(Provider)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook provider."""
    # Check if provider already exists
    stmt = select(Provider).where(Provider.name == provider_data.name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Provider '{provider_data.name}' already exists"
        )
    
    # Create new provider
    provider = Provider(
        id=uuid.uuid4(),
        name=provider_data.name,
        secret_key=provider_data.secret_key,
        forwarding_url=provider_data.forwarding_url,
        is_active=True
    )
    
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    
    return provider


@router.get("/providers/{provider_name}", response_model=ProviderResponse)
async def get_provider(
    provider_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get provider by name."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    return provider


@router.put("/providers/{provider_name}", response_model=ProviderResponse)
async def update_provider(
    provider_name: str,
    provider_data: ProviderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a provider."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    # Update fields if provided
    if provider_data.secret_key:
        provider.secret_key = provider_data.secret_key
    if provider_data.forwarding_url:
        provider.forwarding_url = provider_data.forwarding_url
    if provider_data.is_active is not None:
        provider.is_active = provider_data.is_active
    
    await db.commit()
    await db.refresh(provider)
    
    return provider


@router.delete("/providers/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a provider."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    stmt = delete(Provider).where(Provider.name == provider_name)
    await db.execute(stmt)
    await db.commit()



@router.get("/providers/{provider_name}/stats")
async def get_provider_stats(
    provider_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get provider statistics."""
    stmt = select(Provider).where(Provider.name == provider_name)
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    # Get webhook stats for this provider
    stmt = select(WebhookEvent).where(WebhookEvent.provider_id == provider.id)
    result = await db.execute(stmt)
    webhooks = result.scalars().all()
    
    total = len(webhooks)
    successful = sum(1 for w in webhooks if w.forwarded and w.response_status and 200 <= w.response_status < 300)
    failed = sum(1 for w in webhooks if w.forwarded and w.response_status and w.response_status >= 400)
    
    last_webhook_at = max([w.received_at for w in webhooks], default=None)
    
    return {
        "total_webhooks": total,
        "successful_webhooks": successful,
        "failed_webhooks": failed,
        "last_webhook_at": last_webhook_at
    }


# Webhook endpoints
@router.get("/webhooks", response_model=List[WebhookEventResponse])
async def list_webhooks(
    provider_name: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List webhook events with optional filtering."""
    stmt = select(WebhookEvent)
    
    if provider_name:
        provider_stmt = select(Provider).where(Provider.name == provider_name)
        provider_result = await db.execute(provider_stmt)
        provider = provider_result.scalars().first()
        if provider:
            stmt = stmt.where(WebhookEvent.provider_id == provider.id)
    
    stmt = stmt.order_by(WebhookEvent.received_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    webhooks = result.scalars().all()
    return [WebhookEventResponse.from_orm(w) for w in webhooks]


@router.get("/webhooks/stats")
async def get_webhook_stats(
    provider_name: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook statistics."""
    stmt = select(WebhookEvent)
    
    if provider_name:
        provider_stmt = select(Provider).where(Provider.name == provider_name)
        provider_result = await db.execute(provider_stmt)
        provider = provider_result.scalars().first()
        if provider:
            stmt = stmt.where(WebhookEvent.provider_id == provider.id)
    
    result = await db.execute(stmt)
    webhooks = result.scalars().all()
    
    total = len(webhooks)
    successful = sum(1 for w in webhooks if w.forwarded and w.response_status and 200 <= w.response_status < 300)
    failed = sum(1 for w in webhooks if w.forwarded and w.response_status and w.response_status >= 400)
    pending = sum(1 for w in webhooks if not w.forwarded)
    
    avg_response_time = 0
    if successful > 0:
        response_times = [w.forwarded_at.timestamp() - w.received_at.timestamp() for w in webhooks if w.forwarded_at and w.received_at]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "pending": pending,
        "avg_response_time": avg_response_time
    }


@router.get("/webhooks/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get webhook event details."""
    try:
        webhook_uuid = uuid.UUID(webhook_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook ID format"
        )
    
    stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_uuid)
    result = await db.execute(stmt)
    webhook = result.scalars().first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{webhook_id}' not found"
        )
    
    return WebhookEventResponse.from_orm(webhook)


@router.post("/webhooks/{webhook_id}/retry")
async def retry_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed webhook."""
    from app.core.forwarding import forward_webhook
    import asyncio
    
    stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_id)
    result = await db.execute(stmt)
    webhook = result.scalars().first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{webhook_id}' not found"
        )
    
    # Get provider to get forwarding URL
    provider_stmt = select(Provider).where(Provider.id == webhook.provider_id)
    provider_result = await db.execute(provider_stmt)
    provider = provider_result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )
    
    # Reset forwarding status and retry
    webhook.forwarded = False
    webhook.response_status = None
    webhook.response_body = None
    webhook.error_message = None
    await db.commit()
    
    # Retry forwarding with new session
    asyncio.create_task(
        forward_webhook(
            webhook.id,
            webhook.payload,
            webhook.request_id,
            provider.forwarding_url,
            settings.DATABASE_URL
        )
    )
    
    return {
        "status": "accepted",
        "message": "Webhook retry initiated",
        "webhook_id": str(webhook.id)
    }


# Security log endpoints
@router.get("/logs/stats")
async def get_security_stats(db: AsyncSession = Depends(get_db)):
    """Get security statistics."""
    stmt = select(SecurityLog)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    total_events = len(logs)
    invalid_signatures = sum(1 for l in logs if l.event_type == "invalid_signature")
    rate_limit_events = sum(1 for l in logs if l.event_type == "rate_limit_exceeded")
    replay_attempts = sum(1 for l in logs if l.event_type == "replay_attempt")
    timestamp_errors = sum(1 for l in logs if l.event_type in ["timestamp_too_old", "timestamp_in_future"])
    
    # Count events by type
    events_by_type = {}
    for log in logs:
        events_by_type[log.event_type] = events_by_type.get(log.event_type, 0) + 1
    
    return {
        "total_events": total_events,
        "invalid_signatures": invalid_signatures,
        "rate_limit_events": rate_limit_events,
        "replay_attempts": replay_attempts,
        "timestamp_errors": timestamp_errors,
        "events_by_type": events_by_type
    }


@router.get("/logs", response_model=List[SecurityLogResponse])
async def list_security_logs(
    event_type: str = Query(None),
    provider_name: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List security logs with filtering."""
    stmt = select(SecurityLog)
    
    if event_type:
        stmt = stmt.where(SecurityLog.event_type == event_type)
    if provider_name:
        stmt = stmt.where(SecurityLog.provider_name == provider_name)
    if date_from:
        from datetime import datetime
        date_from_dt = datetime.fromisoformat(date_from)
        stmt = stmt.where(SecurityLog.created_at >= date_from_dt)
    if date_to:
        from datetime import datetime
        date_to_dt = datetime.fromisoformat(date_to)
        stmt = stmt.where(SecurityLog.created_at <= date_to_dt)
    
    stmt = stmt.order_by(SecurityLog.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/logs/{log_id}", response_model=SecurityLogResponse)
async def get_security_log(
    log_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get security log details."""
    stmt = select(SecurityLog).where(SecurityLog.id == log_id)
    result = await db.execute(stmt)
    log = result.scalars().first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security log '{log_id}' not found"
        )
    
    return log


@router.get("/logs/export")
async def export_security_logs(
    event_type: str = Query(None),
    provider_name: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Export security logs as CSV with pagination."""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    stmt = select(SecurityLog)
    
    if event_type:
        stmt = stmt.where(SecurityLog.event_type == event_type)
    if provider_name:
        stmt = stmt.where(SecurityLog.provider_name == provider_name)
    if date_from:
        from datetime import datetime
        date_from_dt = datetime.fromisoformat(date_from)
        stmt = stmt.where(SecurityLog.created_at >= date_from_dt)
    if date_to:
        from datetime import datetime
        date_to_dt = datetime.fromisoformat(date_to)
        stmt = stmt.where(SecurityLog.created_at <= date_to_dt)
    
    stmt = stmt.order_by(SecurityLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Provider", "Event Type", "Client IP", "Request ID", "Created At"])
    
    for log in logs:
        writer.writerow([
            str(log.id),
            log.provider_name,
            log.event_type,
            log.ip_address,
            log.request_id or "",
            log.created_at.isoformat()
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=security_logs.csv"}
    )
