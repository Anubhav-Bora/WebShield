"""
SimulationSession and AttackResult models for security simulation tracking.

Stores simulation runs and their outcomes for audit and trust-building purposes.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SimulationSession(Base):
    """
    Represents a security simulation testing session.
    
    Tracks when a user runs attack simulations to demonstrate security.
    """
    __tablename__ = "simulation_sessions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique session identifier"
    )
    
    # User who ran the simulation
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who executed the simulation"
    )
    
    # Provider being tested
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Provider being tested"
    )
    
    # Session metadata
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Title/description of simulation session"
    )
    
    total_attacks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Total number of attacks in this session"
    )
    
    attacks_blocked: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Number of attacks successfully blocked"
    )
    
    attacks_allowed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Number of attacks that got through (should be 0)"
    )
    
    # Success status
    is_successful: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether all attacks were blocked (success = attacks_blocked == total_attacks)"
    )
    
    # Additional metadata
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User notes about the simulation"
    )
    
    metadata_: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        comment="Additional metadata (user agent, IP, etc)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When simulation started"
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When simulation completed"
    )
    
    # Relationships
    attack_results = relationship(
        "AttackResult",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class AttackResult(Base):
    """
    Results of a single attack simulation.
    
    Tracks what attack was performed, whether it was blocked,
    and detailed response information.
    """
    __tablename__ = "attack_results"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique attack result identifier"
    )
    
    # Foreign key to simulation session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Which simulation session this attack belongs to"
    )
    
    # Security log created by the attack (if blocked)
    security_log_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("security_logs.id", ondelete="SET NULL"),
        nullable=True,
        comment="Link to actual security log if attack was blocked"
    )
    
    # Webhook event created (if attack passed through)
    webhook_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("webhook_events.id", ondelete="SET NULL"),
        nullable=True,
        comment="Link to webhook event if somehow attack got through"
    )
    
    # Attack details
    attack_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of attack (invalid_signature, replay, etc)"
    )
    
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable description of the attack"
    )
    
    # Attack results
    was_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Whether the attack was successfully blocked"
    )
    
    block_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Why the attack was blocked (from HTTP status)"
    )
    
    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP status code of the response"
    )
    
    response_body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Response body from the attack"
    )
    
    # Request details (for debugging)
    headers_sent: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        comment="Headers that were sent with the attack"
    )
    
    # Educational content
    educational_insight: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Educational explanation of what this attack demonstrates"
    )
    
    security_principle: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Security principle being tested (e.g., 'Authentication', 'Integrity')"
    )
    
    # Timestamps
    executed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When this attack was executed"
    )
    
    # Relationship back to session
    session = relationship(
        "SimulationSession",
        back_populates="attack_results"
    )
    
    # Indices for common queries
    __table_args__ = (
        Index("idx_attack_results_session_type", "session_id", "attack_type"),
        Index("idx_attack_results_blocked", "was_blocked"),
        Index("idx_attack_results_created", "executed_at"),
    )
