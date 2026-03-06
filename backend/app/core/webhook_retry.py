"""
Webhook retry logic with exponential backoff.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.models.webhook_event import WebhookEvent
from app.db.models.webhook_retry import WebhookRetry
from app.core.forwarding import forward_webhook
from app.core.config import settings

logger = logging.getLogger(__name__)

# Exponential backoff delays in seconds
RETRY_DELAYS = [1, 2, 4, 8, 16]  # Total: 31 seconds
MAX_RETRIES = len(RETRY_DELAYS)


async def create_initial_retry(
    db: AsyncSession,
    webhook_event_id: uuid.UUID,
    error_message: str = None
) -> WebhookRetry:
    """
    Create initial retry record for a failed webhook.
    
    Args:
        db: Database session
        webhook_event_id: ID of the webhook event that failed
        error_message: Error message from the failure
    
    Returns:
        Created WebhookRetry record
    """
    retry = WebhookRetry(
        id=uuid.uuid4(),
        webhook_event_id=webhook_event_id,
        attempt_number=1,
        next_retry_at=datetime.utcnow() + timedelta(seconds=RETRY_DELAYS[0]),
        status="pending",
        error_message=error_message
    )
    
    db.add(retry)
    await db.commit()
    await db.refresh(retry)
    
    logger.info(f"Created initial retry for webhook {webhook_event_id}")
    return retry


async def create_next_retry(
    db: AsyncSession,
    webhook_event_id: uuid.UUID,
    attempt_number: int,
    response_status: int = None,
    response_body: str = None,
    error_message: str = None
) -> WebhookRetry:
    """
    Create next retry record with exponential backoff.
    
    Args:
        db: Database session
        webhook_event_id: ID of the webhook event
        attempt_number: Current attempt number
        response_status: HTTP status from last attempt
        response_body: Response body from last attempt
        error_message: Error message from last attempt
    
    Returns:
        Created WebhookRetry record or None if max retries exceeded
    """
    if attempt_number >= MAX_RETRIES:
        logger.warning(f"Max retries ({MAX_RETRIES}) exceeded for webhook {webhook_event_id}")
        return None
    
    # Calculate delay for next attempt
    delay_seconds = RETRY_DELAYS[attempt_number]
    
    retry = WebhookRetry(
        id=uuid.uuid4(),
        webhook_event_id=webhook_event_id,
        attempt_number=attempt_number + 1,
        next_retry_at=datetime.utcnow() + timedelta(seconds=delay_seconds),
        status="pending",
        response_status=response_status,
        response_body=response_body,
        error_message=error_message
    )
    
    db.add(retry)
    await db.commit()
    await db.refresh(retry)
    
    logger.info(
        f"Created retry {attempt_number + 1} for webhook {webhook_event_id}, "
        f"next attempt in {delay_seconds} seconds"
    )
    return retry


async def mark_as_delivered(
    db: AsyncSession,
    retry_id: uuid.UUID,
    response_status: int,
    response_body: str = None
) -> None:
    """
    Mark a retry as successfully delivered.
    
    Args:
        db: Database session
        retry_id: ID of the retry record
        response_status: HTTP status code
        response_body: Response body
    """
    stmt = select(WebhookRetry).where(WebhookRetry.id == retry_id)
    result = await db.execute(stmt)
    retry = result.scalar_one_or_none()
    
    if retry:
        retry.status = "delivered"
        retry.response_status = response_status
        retry.response_body = response_body
        retry.updated_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Webhook retry {retry_id} marked as delivered")


async def mark_as_dead_lettered(
    db: AsyncSession,
    retry_id: uuid.UUID,
    error_message: str = None
) -> None:
    """
    Mark a retry as dead-lettered (permanently failed).
    
    Args:
        db: Database session
        retry_id: ID of the retry record
        error_message: Reason for failure
    """
    stmt = select(WebhookRetry).where(WebhookRetry.id == retry_id)
    result = await db.execute(stmt)
    retry = result.scalar_one_or_none()
    
    if retry:
        retry.status = "dead_lettered"
        retry.error_message = error_message
        retry.updated_at = datetime.utcnow()
        await db.commit()
        
        logger.error(f"Webhook retry {retry_id} marked as dead-lettered: {error_message}")


async def get_pending_retries(db: AsyncSession) -> list[WebhookRetry]:
    """
    Get all pending retries that are ready to be attempted.
    
    Returns:
        List of WebhookRetry records ready for retry
    """
    stmt = select(WebhookRetry).where(
        WebhookRetry.status == "pending",
        WebhookRetry.next_retry_at <= datetime.utcnow()
    ).order_by(WebhookRetry.next_retry_at)
    
    result = await db.execute(stmt)
    return result.scalars().all()


async def process_pending_retries(db: AsyncSession, database_url: str) -> None:
    """
    Process all pending retries that are ready.
    
    This should be called periodically (e.g., every 10 seconds) by a background job.
    
    Args:
        db: Database session
        database_url: Database URL for creating new sessions in async tasks
    """
    pending_retries = await get_pending_retries(db)
    
    logger.info(f"Processing {len(pending_retries)} pending retries")
    
    for retry in pending_retries:
        try:
            # Get the webhook event
            stmt = select(WebhookEvent).where(WebhookEvent.id == retry.webhook_event_id)
            result = await db.execute(stmt)
            webhook = result.scalar_one_or_none()
            
            if not webhook:
                logger.error(f"Webhook {retry.webhook_event_id} not found")
                continue
            
            # Get the provider
            from app.db.models.provider import Provider
            stmt = select(Provider).where(Provider.id == webhook.provider_id)
            result = await db.execute(stmt)
            provider = result.scalar_one_or_none()
            
            if not provider:
                logger.error(f"Provider {webhook.provider_id} not found")
                continue
            
            # Attempt to forward webhook
            try:
                response = await forward_webhook(
                    webhook.id,
                    webhook.payload,
                    webhook.request_id,
                    provider.forwarding_url,
                    database_url
                )
                
                if response and response.get("status_code", 0) < 400:
                    # Success!
                    await mark_as_delivered(
                        db,
                        retry.id,
                        response.get("status_code"),
                        response.get("body")
                    )
                    logger.info(f"Webhook {webhook.id} delivered on retry {retry.attempt_number}")
                else:
                    # Still failing
                    if retry.attempt_number < MAX_RETRIES:
                        # Schedule next retry
                        await create_next_retry(
                            db,
                            webhook.id,
                            retry.attempt_number,
                            response.get("status_code") if response else None,
                            response.get("body") if response else None,
                            response.get("error") if response else "Unknown error"
                        )
                    else:
                        # Max retries exceeded
                        await mark_as_dead_lettered(
                            db,
                            retry.id,
                            f"Max retries ({MAX_RETRIES}) exceeded"
                        )
                        logger.error(f"Webhook {webhook.id} dead-lettered after {MAX_RETRIES} retries")
                        
            except Exception as e:
                logger.error(f"Error forwarding webhook {webhook.id}: {str(e)}")
                
                # Schedule next retry if not max retries
                if retry.attempt_number < MAX_RETRIES:
                    await create_next_retry(
                        db,
                        webhook.id,
                        retry.attempt_number,
                        error_message=str(e)
                    )
                else:
                    await mark_as_dead_lettered(
                        db,
                        retry.id,
                        f"Error: {str(e)}"
                    )
                    
        except Exception as e:
            logger.error(f"Error processing retry {retry.id}: {str(e)}")
