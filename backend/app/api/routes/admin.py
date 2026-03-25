"""
Admin API routes for provider management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid
from typing import List

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.db.models.security_log import SecurityLog
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse
from app.schemas.webhook import WebhookEventResponse
from app.schemas.security_log import SecurityLogResponse
from app.core.config import settings
from app.core.auth import get_current_user


router = APIRouter()


@router.get("/providers", response_model=List[ProviderResponse])
async def list_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all webhook providers for the current user."""
    stmt = select(Provider).where(Provider.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook provider for the current user."""
    # Check if provider already exists globally (name must be unique)
    stmt = select(Provider).where(Provider.name == provider_data.name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Provider name '{provider_data.name}' is already taken. Choose a different name."
        )
    
    # Create new provider
    provider = Provider(
        id=uuid.uuid4(),
        user_id=current_user.id,
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get provider by name for the current user."""
    stmt = select(Provider).where(
        (Provider.user_id == current_user.id) & 
        (Provider.name == provider_name)
    )
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a provider for the current user."""
    stmt = select(Provider).where(
        (Provider.user_id == current_user.id) & 
        (Provider.name == provider_name)
    )
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a provider for the current user."""
    stmt = select(Provider).where(
        (Provider.user_id == current_user.id) & 
        (Provider.name == provider_name)
    )
    result = await db.execute(stmt)
    provider = result.scalars().first()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )
    
    stmt = delete(Provider).where(
        (Provider.user_id == current_user.id) & 
        (Provider.name == provider_name)
    )
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


@router.get("/logs/export/csv")
async def export_security_logs_csv(
    event_type: str = Query(None),
    provider_name: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Export security logs as CSV with pagination."""
    from fastapi.responses import Response
    import csv
    import io
    import json
    
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
    writer.writerow(["ID", "Provider", "Event Type", "Client IP", "Request ID", "Details", "Created At"])
    
    for log in logs:
        details = json.dumps(log.details) if log.details else ""
        writer.writerow([
            str(log.id),
            log.provider_name,
            log.event_type,
            log.ip_address,
            log.request_id or "",
            details,
            log.created_at.isoformat()
        ])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=security_logs.csv"}
    )


# PDF Export endpoints
@router.get("/logs/export/pdf")
async def export_security_logs_pdf(
    event_type: str = Query(None),
    provider_name: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Export security logs as PDF."""
    from fastapi.responses import Response
    from app.core.pdf_export import generate_security_logs_pdf
    
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
    
    # Convert to dict for PDF generation
    logs_data = [
        {
            'id': str(log.id),
            'provider_name': log.provider_name,
            'event_type': log.event_type,
            'ip_address': log.ip_address,
            'request_id': log.request_id,
            'details': log.details,
            'created_at': log.created_at.isoformat()
        }
        for log in logs
    ]
    
    # Generate PDF
    pdf_buffer = generate_security_logs_pdf(logs_data)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=security_logs.pdf"}
    )


@router.get("/webhooks/export/pdf")
async def export_webhooks_pdf(
    provider_name: str = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Export webhook events as PDF."""
    from fastapi.responses import Response
    from app.core.pdf_export import generate_webhook_events_pdf
    
    stmt = select(WebhookEvent)
    
    if provider_name:
        provider_stmt = select(Provider).where(Provider.name == provider_name)
        provider_result = await db.execute(provider_stmt)
        provider = provider_result.scalars().first()
        if provider:
            stmt = stmt.where(WebhookEvent.provider_id == provider.id)
    
    stmt = stmt.order_by(WebhookEvent.received_at.desc()).limit(limit)
    result = await db.execute(stmt)
    webhooks = result.scalars().all()
    
    # Convert to dict for PDF generation
    webhooks_data = [
        {
            'id': str(webhook.id),
            'request_id': webhook.request_id,
            'source': webhook.source,
            'signature_valid': webhook.signature_valid,
            'forwarded': webhook.forwarded,
            'response_status': webhook.response_status,
            'received_at': webhook.received_at.isoformat()
        }
        for webhook in webhooks
    ]
    
    # Generate PDF
    pdf_buffer = generate_webhook_events_pdf(webhooks_data)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=webhook_events.pdf"}
    )



@router.get("/dashboard/export/pdf")
async def export_dashboard_pdf(db: AsyncSession = Depends(get_db)):
    """Export complete dashboard as PDF with all metrics and data."""
    from fastapi.responses import Response
    from app.core.pdf_export import generate_dashboard_pdf
    
    # Get providers count
    providers_stmt = select(Provider)
    providers_result = await db.execute(providers_stmt)
    providers = providers_result.scalars().all()
    providers_count = len(providers)
    
    # Get webhook stats
    webhooks_stmt = select(WebhookEvent)
    webhooks_result = await db.execute(webhooks_stmt)
    webhooks = webhooks_result.scalars().all()
    
    webhooks_total = len(webhooks)
    webhooks_successful = sum(1 for w in webhooks if w.forwarded and w.response_status and 200 <= w.response_status < 300)
    webhooks_failed = sum(1 for w in webhooks if w.forwarded and w.response_status and w.response_status >= 400)
    success_rate = (webhooks_successful / webhooks_total * 100) if webhooks_total > 0 else 0
    
    # Get security events
    security_stmt = select(SecurityLog)
    security_result = await db.execute(security_stmt)
    security_logs_data = security_result.scalars().all()
    security_events = len(security_logs_data)
    
    # Convert webhook events to dict
    webhook_events_data = [
        {
            'request_id': w.request_id,
            'source': w.source,
            'response_status': w.response_status,
            'received_at': w.received_at.isoformat() if w.received_at else None
        }
        for w in webhooks[:20]
    ]
    
    # Convert security logs to dict
    security_logs_dict = [
        {
            'event_type': log.event_type,
            'provider_name': log.provider_name,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat() if log.created_at else None
        }
        for log in security_logs_data[:20]
    ]
    
    # Get traffic sources
    traffic_sources = {}
    for webhook in webhooks:
        source = webhook.source or 'Unknown'
        traffic_sources[source] = traffic_sources.get(source, 0) + 1
    
    # Generate PDF
    pdf_buffer = generate_dashboard_pdf(
        providers_count=providers_count,
        webhooks_total=webhooks_total,
        webhooks_successful=webhooks_successful,
        webhooks_failed=webhooks_failed,
        success_rate=success_rate,
        security_events=security_events,
        webhook_events=webhook_events_data,
        security_logs=security_logs_dict,
        traffic_sources=traffic_sources
    )
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=dashboard_report.pdf"}
    )


@router.get("/webhooks/export/csv")
async def export_webhooks_csv(
    provider_name: str = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Export webhook events as CSV with payload and hash."""
    from fastapi.responses import Response
    import csv
    import io
    import json
    
    stmt = select(WebhookEvent)
    
    if provider_name:
        provider_stmt = select(Provider).where(Provider.name == provider_name)
        provider_result = await db.execute(provider_stmt)
        provider = provider_result.scalars().first()
        if provider:
            stmt = stmt.where(WebhookEvent.provider_id == provider.id)
    
    stmt = stmt.order_by(WebhookEvent.received_at.desc()).limit(limit)
    result = await db.execute(stmt)
    webhooks = result.scalars().all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Request ID", "Source", "Signature Valid", "Forwarded", "Response Status", "Payload Hash", "Payload", "Received At"])
    
    for webhook in webhooks:
        payload_json = json.dumps(webhook.payload) if webhook.payload else ""
        writer.writerow([
            str(webhook.id),
            webhook.request_id,
            webhook.source,
            "Yes" if webhook.signature_valid else "No",
            "Yes" if webhook.forwarded else "No",
            webhook.response_status or "Pending",
            webhook.payload_hash or "",
            payload_json,
            webhook.received_at.isoformat()
        ])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=webhook_events.csv"}
    )
