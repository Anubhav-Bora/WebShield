"""
Advanced webhook routes - retry, dead letter queue, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.models.webhook_retry import WebhookRetry
from app.db.models.user import User
from app.core.auth import get_current_active_user
from app.schemas.webhook_retry import WebhookRetryResponse, DeadLetterQueueResponse

router = APIRouter()


@router.get("/webhooks/{webhook_id}/retries", response_model=List[WebhookRetryResponse])
async def get_webhook_retries(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get retry history for a webhook. Requires authentication."""
    stmt = select(WebhookRetry).where(
        WebhookRetry.webhook_event_id == webhook_id
    ).order_by(WebhookRetry.attempt_number)
    
    result = await db.execute(stmt)
    retries = result.scalars().all()
    
    return [WebhookRetryResponse.from_orm(r) for r in retries]


@router.get("/dead-letter-queue", response_model=List[DeadLetterQueueResponse])
async def get_dead_letter_queue(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get permanently failed webhooks (dead letter queue). Requires authentication."""
    stmt = select(WebhookRetry).where(
        WebhookRetry.status == "dead_lettered"
    ).order_by(
        WebhookRetry.created_at.desc()
    ).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    retries = result.scalars().all()
    
    return [DeadLetterQueueResponse.from_orm(r) for r in retries]


@router.post("/dead-letter-queue/{retry_id}/retry")
async def retry_dead_lettered_webhook(
    retry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retry a dead-lettered webhook. Requires authentication."""
    stmt = select(WebhookRetry).where(WebhookRetry.id == retry_id)
    result = await db.execute(stmt)
    retry = result.scalar_one_or_none()
    
    if not retry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retry record not found"
        )
    
    if retry.status != "dead_lettered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only dead-lettered webhooks can be retried"
        )
    
    # Reset to pending for retry
    retry.status = "pending"
    retry.attempt_number = 1
    retry.next_retry_at = __import__('datetime').datetime.utcnow()
    retry.error_message = None
    
    await db.commit()
    
    return {
        "status": "accepted",
        "message": "Webhook queued for retry",
        "retry_id": str(retry.id)
    }
