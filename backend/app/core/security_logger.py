"""
Security event logging utilities.

Logs security violations for monitoring and alerting.
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.security_log import SecurityLog
import uuid


async def log_security_event(
    db: AsyncSession,
    provider_name: str,
    event_type: str,
    ip_address: str,
    request_id: str = None,
    details: dict = None
) -> SecurityLog:
    """
    Log a security event to the database.
    
    Args:
        db: Database session
        provider_name: Name of the provider
        event_type: Type of security event (e.g., "invalid_signature", "rate_limit_exceeded")
        ip_address: Source IP address
        request_id: Request ID if available
        details: Additional context (dict)
    
    Returns:
        Created SecurityLog entry
    """
    security_log = SecurityLog(
        id=uuid.uuid4(),
        provider_name=provider_name,
        event_type=event_type,
        ip_address=ip_address,
        request_id=request_id,
        details=details or {},
        created_at=datetime.utcnow()
    )
    
    db.add(security_log)
    await db.commit()
    
    return security_log
