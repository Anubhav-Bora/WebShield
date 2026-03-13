"""
Alert monitoring and triggering logic.
"""
import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.alert_rule import AlertRule, AlertHistory
from app.db.models.webhook_event import WebhookEvent
from app.db.models.security_log import SecurityLog

logger = logging.getLogger(__name__)


async def calculate_failure_rate(
    db: AsyncSession,
    provider_id: uuid.UUID = None,
    window_minutes: int = 5
) -> float:
    """
    Calculate webhook failure rate.
    
    Args:
        db: Database session
        provider_id: Optional provider to filter by
        window_minutes: Time window in minutes
    
    Returns:
        Failure rate as percentage (0-100)
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
    
    stmt = select(func.count(WebhookEvent.id)).where(
        WebhookEvent.received_at >= cutoff_time
    )
    if provider_id:
        stmt = stmt.where(WebhookEvent.provider_id == provider_id)
    
    result = await db.execute(stmt)
    total = result.scalar() or 0
    
    if total == 0:
        return 0.0
    
    # Count failed webhooks
    stmt = select(func.count(WebhookEvent.id)).where(
        WebhookEvent.received_at >= cutoff_time,
        WebhookEvent.forwarded == True,
        WebhookEvent.response_status >= 400
    )
    if provider_id:
        stmt = stmt.where(WebhookEvent.provider_id == provider_id)
    
    result = await db.execute(stmt)
    failed = result.scalar() or 0
    
    return (failed / total * 100) if total > 0 else 0.0


async def calculate_avg_latency(
    db: AsyncSession,
    provider_id: uuid.UUID = None,
    window_minutes: int = 5
) -> float:
    """
    Calculate average webhook latency.
    
    Args:
        db: Database session
        provider_id: Optional provider to filter by
        window_minutes: Time window in minutes
    
    Returns:
        Average latency in milliseconds
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
    
    stmt = select(func.avg(
        (WebhookEvent.forwarded_at - WebhookEvent.received_at).cast(float)
    )).where(
        WebhookEvent.received_at >= cutoff_time,
        WebhookEvent.forwarded_at.isnot(None)
    )
    if provider_id:
        stmt = stmt.where(WebhookEvent.provider_id == provider_id)
    
    result = await db.execute(stmt)
    avg_seconds = result.scalar() or 0.0
    
    return avg_seconds * 1000  # Convert to milliseconds


async def count_rate_limit_violations(
    db: AsyncSession,
    window_minutes: int = 5
) -> int:
    """
    Count rate limit violations.
    
    Args:
        db: Database session
        window_minutes: Time window in minutes
    
    Returns:
        Number of rate limit violations
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
    
    stmt = select(func.count(SecurityLog.id)).where(
        SecurityLog.created_at >= cutoff_time,
        SecurityLog.event_type == "rate_limit_exceeded"
    )
    
    result = await db.execute(stmt)
    return result.scalar() or 0


async def check_alert_rule(
    db: AsyncSession,
    alert_rule: AlertRule
) -> tuple[bool, float]:
    """
    Check if an alert rule should be triggered.
    
    Args:
        db: Database session
        alert_rule: Alert rule to check
    
    Returns:
        Tuple of (should_trigger, metric_value)
    """
    try:
        if alert_rule.condition == "failure_rate_high":
            metric = await calculate_failure_rate(db, window_minutes=alert_rule.window_minutes)
            should_trigger = metric > alert_rule.threshold
            
        elif alert_rule.condition == "latency_high":
            metric = await calculate_avg_latency(db, window_minutes=alert_rule.window_minutes)
            should_trigger = metric > alert_rule.threshold
            
        elif alert_rule.condition == "rate_limit_exceeded":
            metric = await count_rate_limit_violations(db, window_minutes=alert_rule.window_minutes)
            should_trigger = metric > alert_rule.threshold
            
        else:
            logger.warning(f"Unknown alert condition: {alert_rule.condition}")
            return False, 0.0
        
        return should_trigger, metric
        
    except Exception as e:
        logger.error(f"Error checking alert rule {alert_rule.id}: {str(e)}")
        return False, 0.0


async def trigger_alert(
    db: AsyncSession,
    alert_rule: AlertRule,
    metric_value: float
) -> AlertHistory:
    """
    Trigger an alert and create history record.
    
    Args:
        db: Database session
        alert_rule: Alert rule that triggered
        metric_value: The metric value that triggered the alert
    
    Returns:
        Created AlertHistory record
    """
    message = f"Alert '{alert_rule.name}' triggered: {metric_value:.2f} > {alert_rule.threshold}"
    
    alert_history = AlertHistory(
        id=uuid.uuid4(),
        alert_rule_id=alert_rule.id,
        metric_value=metric_value,
        threshold=alert_rule.threshold,
        message=message,
        created_at=datetime.utcnow()
    )
    
    db.add(alert_history)
    
    # Update last triggered time
    alert_rule.last_triggered_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(alert_history)
    
    logger.warning(f"[ALERT] {message}")
    
    return alert_history


async def process_alert_rules(db: AsyncSession) -> None:
    """
    Process all active alert rules and trigger if needed.
    
    This should be called periodically (e.g., every minute) by a background job.
    
    Args:
        db: Database session
    """
    # Get all active alert rules
    stmt = select(AlertRule).where(AlertRule.is_active == True)
    result = await db.execute(stmt)
    alert_rules = result.scalars().all()
    
    logger.info(f"Processing {len(alert_rules)} active alert rules")
    
    for alert_rule in alert_rules:
        should_trigger, metric_value = await check_alert_rule(db, alert_rule)
        
        if should_trigger:
            # Check if alert was recently triggered (avoid spam)
            if alert_rule.last_triggered_at:
                time_since_last = datetime.utcnow() - alert_rule.last_triggered_at
                if time_since_last < timedelta(minutes=15):
                    logger.debug(f"Alert {alert_rule.id} recently triggered, skipping")
                    continue
            
            # Trigger alert
            await trigger_alert(db, alert_rule, metric_value)
            
            # ...existing code...
