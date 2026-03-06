"""
Analytics model - pre-calculated metrics for fast queries.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class WebhookAnalytics(Base):
    """
    Pre-calculated webhook metrics for fast analytics queries.
    
    Aggregated hourly to avoid expensive calculations.
    """
    __tablename__ = "webhook_analytics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique analytics record ID"
    )
    
    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Provider this metric is for"
    )
    
    hour: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Hour this metric is for (e.g., 2026-03-06 10:00:00)"
    )
    
    total_webhooks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total webhooks received in this hour"
    )
    
    successful_webhooks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Webhooks successfully delivered"
    )
    
    failed_webhooks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Webhooks that failed"
    )
    
    pending_webhooks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Webhooks still pending"
    )
    
    success_rate: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Success rate percentage (0-100)"
    )
    
    avg_latency_ms: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Average latency in milliseconds"
    )
    
    p50_latency_ms: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="50th percentile latency"
    )
    
    p95_latency_ms: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="95th percentile latency"
    )
    
    p99_latency_ms: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="99th percentile latency"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this analytics record was created"
    )
    
    def __repr__(self) -> str:
        return f"<WebhookAnalytics(provider_id={self.provider_id}, hour={self.hour}, success_rate={self.success_rate}%)>"


class SecurityAnalytics(Base):
    """
    Pre-calculated security metrics for fast queries.
    """
    __tablename__ = "security_analytics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique security analytics record ID"
    )
    
    hour: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Hour this metric is for"
    )
    
    invalid_signatures: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Invalid signature attempts"
    )
    
    replay_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Replay attack attempts"
    )
    
    rate_limit_violations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Rate limit violations"
    )
    
    timestamp_errors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Timestamp validation errors"
    )
    
    total_security_events: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total security events"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this analytics record was created"
    )
    
    def __repr__(self) -> str:
        return f"<SecurityAnalytics(hour={self.hour}, total_events={self.total_security_events})>"
