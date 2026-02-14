"""
SecurityLog model - tracks security violations and suspicious activity.

Logs:
- Invalid signatures
- Replay attempts
- Rate limit violations
- Invalid timestamps
- Other security events
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SecurityLog(Base):
    """
    Security event log for monitoring and alerting.
    
    Used to detect patterns of attacks and suspicious behavior.
    """
    __tablename__ = "security_logs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique log entry identifier"
    )
    
    # Provider name (may not exist in providers table if invalid request)
    provider_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,  # For filtering by provider
        comment="Provider name from request"
    )
    
    # Type of security violation
    # Values: "invalid_signature", "replay_attempt", "rate_limit_exceeded", "invalid_timestamp"
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,  # For grouping by violation type
        comment="Type of security event"
    )
    
    # Source IP address (for blocking/analysis)
    ip_address: Mapped[str] = mapped_column(
        String(45),  # IPv6 max length
        nullable=False,
        index=True,  # For IP-based queries (adaptive rate limiting)
        comment="Source IP address"
    )
    
    # Request ID if available
    request_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Request ID if available"
    )
    
    # Additional context (headers, error details, etc.)
    details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Additional event details (JSON)"
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,  # For time-range queries
        comment="When this event occurred"
    )
    
    def __repr__(self) -> str:
        return f"<SecurityLog(type='{self.event_type}', provider='{self.provider_name}', ip='{self.ip_address}')>"


# Composite index for IP-based time-range queries
# Example: "Show me all violations from this IP in the last hour"
Index(
    "ix_security_logs_ip_created",
    SecurityLog.ip_address,
    SecurityLog.created_at
)

# Composite index for provider-specific event analysis
Index(
    "ix_security_logs_provider_type_created",
    SecurityLog.provider_name,
    SecurityLog.event_type,
    SecurityLog.created_at
)
