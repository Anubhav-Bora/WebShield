"""
Webhook forwarding utilities.

Forwards validated webhooks to internal services with retry logic.
"""
import httpx
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.webhook_event import WebhookEvent
from app.core.config import settings


async def forward_webhook(
    webhook_event: WebhookEvent,
    forwarding_url: str,
    db: AsyncSession,
    max_retries: int = 3
) -> bool:
    """
    Forward webhook to internal service with retry logic.
    
    Args:
        webhook_event: The webhook event to forward
        forwarding_url: URL of internal service
        db: Database session
        max_retries: Number of retry attempts
    
    Returns:
        True if successful, False otherwise
    """
    async with httpx.AsyncClient(timeout=settings.FORWARDING_TIMEOUT_SECONDS) as client:
        for attempt in range(max_retries):
            try:
                # Forward the webhook payload
                response = await client.post(
                    forwarding_url,
                    json=webhook_event.payload,
                    headers={
                        "X-Webhook-ID": str(webhook_event.id),
                        "X-Request-ID": webhook_event.request_id,
                        "Content-Type": "application/json"
                    }
                )
                
                # Check if successful (2xx status code)
                if 200 <= response.status_code < 300:
                    # Update database
                    webhook_event.forwarded = True
                    webhook_event.response_status = response.status_code
                    webhook_event.response_body = response.text
                    webhook_event.forwarded_at = datetime.utcnow()
                    await db.commit()
                    return True
                
                # If 4xx error, don't retry (client error)
                if 400 <= response.status_code < 500:
                    webhook_event.response_status = response.status_code
                    webhook_event.response_body = response.text
                    webhook_event.error_message = f"Client error: {response.text}"
                    webhook_event.forwarded_at = datetime.utcnow()
                    await db.commit()
                    return False
                
            except httpx.TimeoutException:
                webhook_event.error_message = f"Timeout on attempt {attempt + 1}/{max_retries}"
            except httpx.RequestError as e:
                webhook_event.error_message = f"Request error: {str(e)}"
            except Exception as e:
                webhook_event.error_message = f"Unexpected error: {str(e)}"
            
            # If last attempt, save error and return
            if attempt == max_retries - 1:
                webhook_event.forwarded_at = datetime.utcnow()
                await db.commit()
                return False
    
    return False
