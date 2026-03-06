"""
Analytics calculation and aggregation logic.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.db.models.webhook_event import WebhookEvent
from app.db.models.security_log import SecurityLog
from app.db.models.analytics import WebhookAnalytics, SecurityAnalytics
from app.db.models.provider import Provider

logger = logging.getLogger(__name__)


async def calculate_webhook_analytics_for_hour(
    db: AsyncSession,
    provider_id: uuid.UUID,
    hour: datetime
) -> WebhookAnalytics:
    """
    Calculate webhook analytics for a specific hour.
    
    Args:
        db: Database session
        provider_id: Provider to calculate for
        hour: Hour to calculate (e.g., 2026-03-06 10:00:00)
    
    Returns:
        WebhookAnalytics record or None if failed
    """
    try:
        hour_start = hour.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        # Get all webhooks for this hour
        stmt = select(WebhookEvent).where(
            WebhookEvent.provider_id == provider_id,
            WebhookEvent.received_at >= hour_start,
            WebhookEvent.received_at < hour_end
        )
        result = await db.execute(stmt)
        webhooks = result.scalars().all()
        
        total = len(webhooks)
        successful = sum(1 for w in webhooks if w.forwarded and w.response_status and 200 <= w.response_status < 300)
        failed = sum(1 for w in webhooks if w.forwarded and w.response_status and w.response_status >= 400)
        pending = sum(1 for w in webhooks if not w.forwarded)
        
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        # Calculate latencies
        latencies = []
        for w in webhooks:
            if w.forwarded_at and w.received_at:
                latency_ms = (w.forwarded_at - w.received_at).total_seconds() * 1000
                latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        # Calculate percentiles
        latencies_sorted = sorted(latencies) if latencies else []
        p50_idx = int(len(latencies_sorted) * 0.50)
        p95_idx = int(len(latencies_sorted) * 0.95)
        p99_idx = int(len(latencies_sorted) * 0.99)
        
        p50_latency = latencies_sorted[p50_idx] if p50_idx < len(latencies_sorted) else 0.0
        p95_latency = latencies_sorted[p95_idx] if p95_idx < len(latencies_sorted) else 0.0
        p99_latency = latencies_sorted[p99_idx] if p99_idx < len(latencies_sorted) else 0.0
        
        # Check if record already exists
        stmt = select(WebhookAnalytics).where(
            WebhookAnalytics.provider_id == provider_id,
            WebhookAnalytics.hour == hour_start
        )
        result = await db.execute(stmt)
        analytics = result.scalar_one_or_none()
        
        if analytics:
            # Update existing record
            analytics.total_webhooks = total
            analytics.successful_webhooks = successful
            analytics.failed_webhooks = failed
            analytics.pending_webhooks = pending
            analytics.success_rate = success_rate
            analytics.avg_latency_ms = avg_latency
            analytics.p50_latency_ms = p50_latency
            analytics.p95_latency_ms = p95_latency
            analytics.p99_latency_ms = p99_latency
        else:
            # Create new record
            analytics = WebhookAnalytics(
                id=uuid.uuid4(),
                provider_id=provider_id,
                hour=hour_start,
                total_webhooks=total,
                successful_webhooks=successful,
                failed_webhooks=failed,
                pending_webhooks=pending,
                success_rate=success_rate,
                avg_latency_ms=avg_latency,
                p50_latency_ms=p50_latency,
                p95_latency_ms=p95_latency,
                p99_latency_ms=p99_latency
            )
            db.add(analytics)
        
        await db.commit()
        await db.refresh(analytics)
        
        logger.info(f"Calculated analytics for provider {provider_id} hour {hour_start}")
        return analytics
    except Exception as e:
        logger.error(f"Failed to calculate webhook analytics: {str(e)}")
        await db.rollback()
        return None


async def calculate_security_analytics_for_hour(
    db: AsyncSession,
    hour: datetime
) -> SecurityAnalytics:
    """
    Calculate security analytics for a specific hour.
    
    Args:
        db: Database session
        hour: Hour to calculate (e.g., 2026-03-06 10:00:00)
    
    Returns:
        SecurityAnalytics record or None if failed
    """
    try:
        hour_start = hour.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        # Count security events by type
        stmt = select(SecurityLog).where(
            SecurityLog.created_at >= hour_start,
            SecurityLog.created_at < hour_end
        )
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        invalid_signatures = sum(1 for l in logs if l.event_type == "invalid_signature")
        replay_attempts = sum(1 for l in logs if l.event_type == "replay_attempt")
        rate_limit_violations = sum(1 for l in logs if l.event_type == "rate_limit_exceeded")
        timestamp_errors = sum(1 for l in logs if l.event_type in ["timestamp_too_old", "timestamp_in_future"])
        total = len(logs)
        
        # Check if record already exists
        stmt = select(SecurityAnalytics).where(
            SecurityAnalytics.hour == hour_start
        )
        result = await db.execute(stmt)
        analytics = result.scalar_one_or_none()
        
        if analytics:
            # Update existing record
            analytics.invalid_signatures = invalid_signatures
            analytics.replay_attempts = replay_attempts
            analytics.rate_limit_violations = rate_limit_violations
            analytics.timestamp_errors = timestamp_errors
            analytics.total_security_events = total
        else:
            # Create new record
            analytics = SecurityAnalytics(
                id=uuid.uuid4(),
                hour=hour_start,
                invalid_signatures=invalid_signatures,
                replay_attempts=replay_attempts,
                rate_limit_violations=rate_limit_violations,
                timestamp_errors=timestamp_errors,
                total_security_events=total
            )
            db.add(analytics)
        
        await db.commit()
        await db.refresh(analytics)
        
        logger.info(f"Calculated security analytics for hour {hour_start}")
        return analytics
    except Exception as e:
        logger.error(f"Failed to calculate security analytics: {str(e)}")
        await db.rollback()
        return None


async def aggregate_analytics(db: AsyncSession) -> None:
    """
    Aggregate analytics for the previous hour.
    
    This should be called periodically (e.g., every hour) by a background job.
    
    Args:
        db: Database session
    """
    # Calculate for the previous hour
    now = datetime.utcnow()
    previous_hour = now - timedelta(hours=1)
    
    logger.info(f"Aggregating analytics for hour {previous_hour}")
    
    # Get all providers
    stmt = select(Provider)
    result = await db.execute(stmt)
    providers = result.scalars().all()
    
    # Calculate webhook analytics for each provider
    for provider in providers:
        try:
            await calculate_webhook_analytics_for_hour(db, provider.id, previous_hour)
        except Exception as e:
            logger.error(f"Error calculating webhook analytics for provider {provider.id}: {str(e)}")
    
    # Calculate security analytics
    try:
        await calculate_security_analytics_for_hour(db, previous_hour)
    except Exception as e:
        logger.error(f"Error calculating security analytics: {str(e)}")
    
    logger.info("Analytics aggregation complete")


async def cleanup_old_analytics(db: AsyncSession, days_to_keep: int = 90) -> None:
    """
    Delete analytics older than specified days.
    
    Args:
        db: Database session
        days_to_keep: Number of days of analytics to keep
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    # Delete old webhook analytics
    stmt = select(WebhookAnalytics).where(WebhookAnalytics.hour < cutoff_date)
    result = await db.execute(stmt)
    old_records = result.scalars().all()
    
    for record in old_records:
        await db.delete(record)
    
    # Delete old security analytics
    stmt = select(SecurityAnalytics).where(SecurityAnalytics.hour < cutoff_date)
    result = await db.execute(stmt)
    old_records = result.scalars().all()
    
    for record in old_records:
        await db.delete(record)
    
    await db.commit()
    
    logger.info(f"Cleaned up analytics older than {days_to_keep} days")
