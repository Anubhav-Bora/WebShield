"""remove superuser field

Revision ID: 3f8d9e2a1b4c
Revises: 20260304_1200_add_users_table
Create Date: 2026-03-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f8d9e2a1b4c'
down_revision = 'add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove is_superuser column
    op.drop_column('users', 'is_superuser')


def downgrade() -> None:
    # Add back is_superuser column
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
