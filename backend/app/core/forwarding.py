"""
Webhook forwarding utilities.

Forwards validated webhooks to internal services with retry logic.
"""
import httpx
import json
import asyncio
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.webhook_event import WebhookEvent
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def forward_webhook(
    webhook_id: UUID,
    webhook_payload: dict,
    webhook_request_id: str,
    forwarding_url: str,
    db_url: str,
    max_retries: int = 3
) -> bool:
    """
    Forward webhook to internal service with retry logic and exponential backoff.
    
    Args:
        webhook_id: The webhook event ID
        webhook_payload: The webhook payload to forward
        webhook_request_id: The request ID for tracking
        forwarding_url: URL of internal service
        db_url: Database URL for creating new session
        max_retries: Number of retry attempts
    
    Returns:
        True if successful, False otherwise
    """
    # Create a new database session for this async task
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with httpx.AsyncClient(timeout=settings.FORWARDING_TIMEOUT_SECONDS) as client:
            for attempt in range(max_retries):
                try:
                    # Forward the webhook payload
                    response = await client.post(
                        forwarding_url,
                        json=webhook_payload,
                        headers={
                            "X-Webhook-ID": str(webhook_id),
                            "X-Request-ID": webhook_request_id,
                            "Content-Type": "application/json"
                        }
                    )
                    
                    # Create new session for database update
                    async with async_session() as session:
                        from sqlalchemy import select
                        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_id)
                        result = await session.execute(stmt)
                        webhook_event = result.scalars().first()
                        
                        if not webhook_event:
                            logger.error(f"Webhook {webhook_id} not found in database")
                            return False
                        
                        # Check if successful (2xx status code)
                        if 200 <= response.status_code < 300:
                            webhook_event.forwarded = True
                            webhook_event.response_status = response.status_code
                            webhook_event.response_body = response.text[:1000]  # Limit response body
                            webhook_event.forwarded_at = datetime.utcnow()
                            await session.commit()
                            logger.info(f"Webhook {webhook_id} forwarded successfully")
                            return True
                        
                        # If 4xx error, don't retry (client error)
                        if 400 <= response.status_code < 500:
                            webhook_event.response_status = response.status_code
                            webhook_event.response_body = response.text[:1000]
                            webhook_event.error_message = f"Client error: {response.status_code}"
                            webhook_event.forwarded_at = datetime.utcnow()
                            await session.commit()
                            logger.warning(f"Webhook {webhook_id} client error: {response.status_code}")
                            return False
                        
                        # 5xx error - retry with exponential backoff
                        if attempt < max_retries - 1:
                            backoff = 2 ** attempt  # 1s, 2s, 4s
                            logger.warning(f"Webhook {webhook_id} server error {response.status_code}, retrying in {backoff}s")
                            await asyncio.sleep(backoff)
                            continue
                        
                        # Last attempt failed
                        webhook_event.response_status = response.status_code
                        webhook_event.response_body = response.text[:1000]
                        webhook_event.error_message = f"Server error after {max_retries} attempts"
                        webhook_event.forwarded_at = datetime.utcnow()
                        await session.commit()
                        return False
                    
                except httpx.TimeoutException as e:
                    logger.warning(f"Webhook {webhook_id} timeout on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    async with async_session() as session:
                        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_id)
                        result = await session.execute(stmt)
                        webhook_event = result.scalars().first()
                        if webhook_event:
                            webhook_event.error_message = f"Timeout after {max_retries} attempts"
                            webhook_event.forwarded_at = datetime.utcnow()
                            await session.commit()
                    return False
                    
                except httpx.RequestError as e:
                    logger.warning(f"Webhook {webhook_id} request error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    async with async_session() as session:
                        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_id)
                        result = await session.execute(stmt)
                        webhook_event = result.scalars().first()
                        if webhook_event:
                            webhook_event.error_message = f"Request error: {str(e)[:100]}"
                            webhook_event.forwarded_at = datetime.utcnow()
                            await session.commit()
                    return False
                    
                except Exception as e:
                    logger.error(f"Webhook {webhook_id} unexpected error: {str(e)}")
                    async with async_session() as session:
                        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_id)
                        result = await session.execute(stmt)
                        webhook_event = result.scalars().first()
                        if webhook_event:
                            webhook_event.error_message = f"Unexpected error: {str(e)[:100]}"
                            webhook_event.forwarded_at = datetime.utcnow()
                            await session.commit()
                    return False
        
        return False
        
    finally:
        await engine.dispose()
