"""
Provider model - stores webhook provider configurations.

Each provider (Stripe, GitHub, etc.) has:
- A unique name per user
- A secret key for HMAC verification
- A forwarding URL where validated webhooks are sent
- Active/inactive status
- Belongs to a user
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Index, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Provider(Base):
    """
    Webhook provider configuration.
    
    Example providers: stripe, github, shopify
    Each user can have their own set of providers.
    """
    __tablename__ = "providers"
    
    # Primary key - using UUID for better security (non-sequential IDs)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique provider identifier"
    )
    
    # Foreign key to user - each provider belongs to a user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this provider"
    )
    
    # Provider name - must be unique globally, used in webhook URLs
    # Example: POST /webhooks/stripe
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,  # Indexed because we query by name on every webhook
        comment="Provider name (e.g., 'stripe', 'stripe-account-2', 'github')"
    )
    
    # Secret key for HMAC signature verification
    # This is the shared secret between the provider and our gateway
    secret_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="HMAC secret key for signature verification"
    )
    
    # Where to forward validated webhooks
    forwarding_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Internal service URL to forward validated webhooks"
    )
    
    # Enable/disable provider without deleting configuration
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this provider is currently active"
    )
    
    # Timestamps for audit trail
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this provider was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When this provider was last updated"
    )
    
    def __repr__(self) -> str:
        return f"<Provider(name='{self.name}', active={self.is_active})>"
