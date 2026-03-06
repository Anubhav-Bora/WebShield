"""
Audit logging utilities for tracking admin actions.
"""
import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_audit_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    action: str,
    resource_type: str,
    resource_id: str = None,
    ip_address: str = "unknown",
    user_agent: str = None,
    changes: dict = None,
    status: str = "success",
    error_message: str = None
) -> AuditLog:
    """
    Log an audit event.
    
    Args:
        db: Database session
        user_id: User who performed the action
        action: Action performed (create_provider, update_provider, etc.)
        resource_type: Type of resource (provider, webhook, etc.)
        resource_id: ID of the resource affected
        ip_address: Client IP address
        user_agent: User agent string
        changes: What changed (before/after)
        status: success or failure
        error_message: Error message if failed
    
    Returns:
        Created AuditLog record or None if failed
    """
    try:
        audit_log = AuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            status=status,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        log_level = logging.INFO if status == "success" else logging.WARNING
        logger.log(
            log_level,
            f"[AUDIT] User {user_id} performed {action} on {resource_type} {resource_id} - {status}"
        )
        
        return audit_log
    except Exception as e:
        logger.error(f"Failed to log audit event: {str(e)}")
        await db.rollback()
        # Don't raise - audit logging shouldn't break the main operation
        return None


async def log_provider_created(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider_id: uuid.UUID,
    provider_name: str,
    ip_address: str,
    user_agent: str = None
) -> AuditLog:
    """Log provider creation."""
    return await log_audit_event(
        db,
        user_id,
        "create_provider",
        "provider",
        str(provider_id),
        ip_address,
        user_agent,
        {"name": provider_name}
    )


async def log_provider_updated(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider_id: uuid.UUID,
    provider_name: str,
    changes: dict,
    ip_address: str,
    user_agent: str = None
) -> AuditLog:
    """Log provider update."""
    return await log_audit_event(
        db,
        user_id,
        "update_provider",
        "provider",
        str(provider_id),
        ip_address,
        user_agent,
        changes
    )


async def log_provider_deleted(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider_id: uuid.UUID,
    provider_name: str,
    ip_address: str,
    user_agent: str = None
) -> AuditLog:
    """Log provider deletion."""
    return await log_audit_event(
        db,
        user_id,
        "delete_provider",
        "provider",
        str(provider_id),
        ip_address,
        user_agent,
        {"name": provider_name}
    )


async def log_export_action(
    db: AsyncSession,
    user_id: uuid.UUID,
    export_type: str,
    ip_address: str,
    user_agent: str = None,
    filters: dict = None
) -> AuditLog:
    """Log export action (CSV, PDF, etc.)."""
    return await log_audit_event(
        db,
        user_id,
        f"export_{export_type}",
        "export",
        None,
        ip_address,
        user_agent,
        filters
    )
