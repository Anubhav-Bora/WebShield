"""Add payload_hash field to webhook_events for integrity verification.

Revision ID: add_payload_hash
Revises: add_retry_audit_alert_analytics
Create Date: 2026-03-06 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_payload_hash'
down_revision = 'add_retry_audit_alert_analytics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add payload_hash column to webhook_events table
    op.add_column(
        'webhook_events',
        sa.Column(
            'payload_hash',
            sa.String(64),
            nullable=True,
            comment='SHA256 hash of payload for integrity verification'
        )
    )
    # Create index for payload_hash for efficient lookups
    op.create_index('ix_webhook_events_payload_hash', 'webhook_events', ['payload_hash'])


def downgrade() -> None:
    # Drop index first
    op.drop_index('ix_webhook_events_payload_hash', table_name='webhook_events')
    # Drop column
    op.drop_column('webhook_events', 'payload_hash')
