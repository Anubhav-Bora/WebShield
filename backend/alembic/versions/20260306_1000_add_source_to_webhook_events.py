"""add source field to webhook events

Revision ID: add_source_field
Revises: 3f8d9e2a1b4c
Create Date: 2026-03-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_source_field'
down_revision = '3f8d9e2a1b4c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source column with default value
    op.add_column('webhook_events', sa.Column('source', sa.String(255), nullable=True))
    # Set default for existing rows
    op.execute("UPDATE webhook_events SET source = 'Unknown' WHERE source IS NULL")
    # Make it non-nullable
    op.alter_column('webhook_events', 'source', nullable=False)


def downgrade() -> None:
    op.drop_column('webhook_events', 'source')
