"""Add user_id to providers table for per-user provider isolation

Revision ID: add_user_id_to_providers
Revises: add_payload_hash
Create Date: 2026-03-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_id_to_providers'
down_revision = 'add_payload_hash'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the user_id column (nullable initially to populate existing rows)
    op.add_column('providers', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Set all existing providers to the first admin user (or attacker_test user)
    # This is a one-time migration to handle existing data
    op.execute("""
        UPDATE providers 
        SET user_id = (SELECT id FROM users LIMIT 1)
        WHERE user_id IS NULL
    """)
    
    # Now make user_id NOT NULL
    op.alter_column('providers', 'user_id', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_providers_user_id',
        'providers',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add index for user_id
    op.create_index('ix_providers_user_id', 'providers', ['user_id'])


def downgrade() -> None:
    # Drop the index
    op.drop_index('ix_providers_user_id', 'providers')
    
    # Drop the foreign key
    op.drop_constraint('fk_providers_user_id', 'providers', type_='foreignkey')
    
    # Remove the user_id column
    op.drop_column('providers', 'user_id')
