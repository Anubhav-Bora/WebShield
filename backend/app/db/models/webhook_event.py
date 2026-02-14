"""
WebhookEvent model - audit log for all incoming webhook requests.

Stores:
- The webhook payload and headers
- Verification results
- Forwarding status
- Timing information
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class WebhookEvent(Base):
    """
    Audit log for webhook requests.
    
    Every webhook attempt (valid or invalid) is logged here.
    """
    __tablename__ = "webhook_events"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique event identifier"
    )
    
    # Foreign key to provider
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Which provider sent this webhook"
    )
    
    # Idempotency key from webhook headers
    # Used for replay protection - must be unique
    request_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,  # Critical for replay protection lookups
        comment="Unique request ID for idempotency"
    )
    
    # The actual webhook payload (stored as JSONB for efficient querying)
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Webhook payload (JSON)"
    )
    
    # Request headers (useful for debugging)
    headers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Request headers (JSON)"
    )
    
    # Security verification result
    signature_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Whether HMAC signature was valid"
    )
    
    # Forwarding status
    forwarded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether webhook was forwarded to internal service"
    )
    
    # HTTP status code from internal service (if forwarded)
    forwarding_status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP status code from forwarding attempt"
    )
    
    # Error message if something went wrong
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if processing failed"
    )
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,  # Indexed for time-range queries in analytics
        comment="When webhook was received"
    )
    
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When webhook processing completed"
    )
    
    # Relationship to provider (optional, for easier querying)
    # provider = relationship("Provider", back_populates="webhook_events")
    
    def __repr__(self) -> str:
        return f"<WebhookEvent(id='{self.id}', provider_id='{self.provider_id}', valid={self.signature_valid})>"


# Composite index for provider-specific time-range queries
# Example: "Show me all Stripe webhooks from the last 24 hours"
Index(
    "ix_webhook_events_provider_received",
    WebhookEvent.provider_id,
    WebhookEvent.received_at
)
