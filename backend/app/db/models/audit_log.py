"""
Audit log model - tracks all admin actions for compliance.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AuditLog(Base):
    """
    Tracks all admin actions for compliance and security auditing.
    
    Example actions:
    - create_provider
    - update_provider
    - delete_provider
    - export_logs
    - etc.
    """
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique audit log ID"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )
    
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (create_provider, update_provider, etc.)"
    )
    
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of resource (provider, webhook, api_key, etc.)"
    )
    
    resource_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="ID of the resource affected"
    )
    
    changes: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="What changed (before/after values)"
    )
    
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="Client IP address"
    )
    
    user_agent: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="User agent string"
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
        comment="success or failure"
    )
    
    error_message: Mapped[str] = mapped_column(
        String(1000),
        nullable=True,
        comment="Error message if action failed"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When the action was performed"
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(user_id={self.user_id}, action={self.action}, resource={self.resource_type})>"
