"""
Alert rule model - defines conditions for triggering alerts.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AlertRule(Base):
    """
    Defines alert rules for monitoring webhook health.
    
    Example rules:
    - Alert if failure rate > 5% in last 5 minutes
    - Alert if average latency > 5 seconds in last 10 minutes
    - Alert if rate limit violations > 10 in last 5 minutes
    """
    __tablename__ = "alert_rules"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique alert rule ID"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this alert rule"
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Alert rule name (e.g., 'High failure rate')"
    )
    
    condition: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Condition type: failure_rate_high, latency_high, rate_limit_exceeded"
    )
    
    threshold: Mapped[float] = mapped_column(
        nullable=False,
        comment="Threshold value (e.g., 0.05 for 5% failure rate)"
    )
    
    window_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Time window in minutes to evaluate metric"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this alert rule is active"
    )
    
    last_triggered_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="When this alert was last triggered"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this alert rule was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When this alert rule was last updated"
    )
    
    def __repr__(self) -> str:
        return f"<AlertRule(name={self.name}, condition={self.condition}, threshold={self.threshold})>"


class AlertNotification(Base):
    """
    Notification channels for alert rules.
    
    Example channels:
    - Email: {"email": "user@example.com"}
    - Slack: {"slack_webhook": "https://hooks.slack.com/..."}
    - Discord: {"discord_webhook": "https://discord.com/api/webhooks/..."}
    """
    __tablename__ = "alert_notifications"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique notification channel ID"
    )
    
    alert_rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to alert rule"
    )
    
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Notification channel: email, slack, discord, webhook"
    )
    
    config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Channel configuration (email, webhook URL, etc.)"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this notification channel is active"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this notification channel was created"
    )
    
    def __repr__(self) -> str:
        return f"<AlertNotification(alert_rule_id={self.alert_rule_id}, channel={self.channel})>"


class AlertHistory(Base):
    """
    History of triggered alerts for auditing.
    """
    __tablename__ = "alert_history"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique alert history ID"
    )
    
    alert_rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to alert rule"
    )
    
    metric_value: Mapped[float] = mapped_column(
        nullable=False,
        comment="The metric value that triggered the alert"
    )
    
    threshold: Mapped[float] = mapped_column(
        nullable=False,
        comment="The threshold that was exceeded"
    )
    
    message: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Alert message"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When the alert was triggered"
    )
    
    def __repr__(self) -> str:
        return f"<AlertHistory(alert_rule_id={self.alert_rule_id}, metric={self.metric_value})>"
