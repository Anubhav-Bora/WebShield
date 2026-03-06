"""
Webhook retry model - tracks retry attempts with exponential backoff.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class WebhookRetry(Base):
    """
    Tracks retry attempts for failed webhooks with exponential backoff.
    
    Example:
    - Attempt 1: delay 1 second
    - Attempt 2: delay 2 seconds
    - Attempt 3: delay 4 seconds
    - Attempt 4: delay 8 seconds
    - Attempt 5: delay 16 seconds
    """
    __tablename__ = "webhook_retries"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique retry record ID"
    )
    
    webhook_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("webhook_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to webhook event"
    )
    
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Retry attempt number (1, 2, 3, etc.)"
    )
    
    next_retry_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="When to attempt next retry"
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        comment="pending, delivered, failed, dead_lettered"
    )
    
    response_status: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP status code from last attempt"
    )
    
    response_body: Mapped[str] = mapped_column(
        String(5000),
        nullable=True,
        comment="Response body from last attempt"
    )
    
    error_message: Mapped[str] = mapped_column(
        String(1000),
        nullable=True,
        comment="Error message if retry failed"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this retry record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When this retry record was last updated"
    )
    
    def __repr__(self) -> str:
        return f"<WebhookRetry(webhook_id={self.webhook_event_id}, attempt={self.attempt_number}, status={self.status})>"
