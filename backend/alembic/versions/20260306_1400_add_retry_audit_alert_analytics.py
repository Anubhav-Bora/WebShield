"""Add webhook retry, audit log, alert rules, and analytics tables.

Revision ID: add_retry_audit_alert_analytics
Revises: add_source_field
Create Date: 2026-03-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_retry_audit_alert_analytics'
down_revision = 'add_source_field'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create webhook_retries table
    op.create_table(
        'webhook_retries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('webhook_event_id', sa.UUID(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('next_retry_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.String(5000), nullable=True),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['webhook_event_id'], ['webhook_events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_webhook_retries_webhook_event_id', 'webhook_retries', ['webhook_event_id'])
    op.create_index('ix_webhook_retries_next_retry_at', 'webhook_retries', ['next_retry_at'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='success'),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('condition', sa.String(100), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('window_minutes', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alert_rules_user_id', 'alert_rules', ['user_id'])
    
    # Create alert_notifications table
    op.create_table(
        'alert_notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('alert_rule_id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['alert_rule_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alert_notifications_alert_rule_id', 'alert_notifications', ['alert_rule_id'])
    
    # Create alert_history table
    op.create_table(
        'alert_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('alert_rule_id', sa.UUID(), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('message', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['alert_rule_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alert_history_alert_rule_id', 'alert_history', ['alert_rule_id'])
    op.create_index('ix_alert_history_created_at', 'alert_history', ['created_at'])
    
    # Create webhook_analytics table
    op.create_table(
        'webhook_analytics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('provider_id', sa.UUID(), nullable=False),
        sa.Column('hour', sa.DateTime(), nullable=False),
        sa.Column('total_webhooks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_webhooks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_webhooks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pending_webhooks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('p50_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('p95_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('p99_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_webhook_analytics_provider_id', 'webhook_analytics', ['provider_id'])
    op.create_index('ix_webhook_analytics_hour', 'webhook_analytics', ['hour'])
    
    # Create security_analytics table
    op.create_table(
        'security_analytics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('hour', sa.DateTime(), nullable=False),
        sa.Column('invalid_signatures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('replay_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rate_limit_violations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timestamp_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_security_events', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_security_analytics_hour', 'security_analytics', ['hour'])


def downgrade() -> None:
    op.drop_index('ix_security_analytics_hour', table_name='security_analytics')
    op.drop_table('security_analytics')
    op.drop_index('ix_webhook_analytics_hour', table_name='webhook_analytics')
    op.drop_index('ix_webhook_analytics_provider_id', table_name='webhook_analytics')
    op.drop_table('webhook_analytics')
    op.drop_index('ix_alert_history_created_at', table_name='alert_history')
    op.drop_index('ix_alert_history_alert_rule_id', table_name='alert_history')
    op.drop_table('alert_history')
    op.drop_index('ix_alert_notifications_alert_rule_id', table_name='alert_notifications')
    op.drop_table('alert_notifications')
    op.drop_index('ix_alert_rules_user_id', table_name='alert_rules')
    op.drop_table('alert_rules')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_webhook_retries_next_retry_at', table_name='webhook_retries')
    op.drop_index('ix_webhook_retries_webhook_event_id', table_name='webhook_retries')
    op.drop_table('webhook_retries')
