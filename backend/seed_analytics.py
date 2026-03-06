"""
Seed script to populate analytics, audit logs, and alert rules with sample data.
Run this after running seed_data.py to populate the new tables.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.audit_log import AuditLog
from app.db.models.alert_rule import AlertRule
from app.db.models.analytics import WebhookAnalytics, SecurityAnalytics
from app.db.models.user import User
from app.db.models.provider import Provider


async def seed_analytics():
    """Seed analytics, audit logs, and alert rules."""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        print("🌱 Seeding analytics data...")
        
        # Get demo user
        from sqlalchemy import select
        stmt = select(User).where(User.username == "demo")
        result = await db.execute(stmt)
        demo_user = result.scalars().first()
        
        if not demo_user:
            print("❌ Demo user not found. Run create_demo_user.py first.")
            return
        
        # Get providers
        stmt = select(Provider)
        result = await db.execute(stmt)
        providers = result.scalars().all()
        
        if not providers:
            print("❌ No providers found. Run seed_data.py first.")
            return
        
        # Seed audit logs
        print("📝 Seeding audit logs...")
        audit_logs = []
        actions = ["create_provider", "update_provider", "export_logs", "view_webhooks"]
        for i in range(20):
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=demo_user.id,
                action=actions[i % len(actions)],
                resource_type="provider" if i % 2 == 0 else "webhook",
                resource_id=str(providers[i % len(providers)].id) if i % 2 == 0 else None,
                ip_address=f"192.168.1.{100 + i}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                changes={"field": "value"} if i % 3 == 0 else None,
                status="success" if i % 5 != 0 else "failure",
                error_message="Connection timeout" if i % 5 == 0 else None,
                created_at=datetime.utcnow() - timedelta(hours=i)
            )
            audit_logs.append(audit_log)
            db.add(audit_log)
        
        await db.commit()
        print(f"✓ Created {len(audit_logs)} audit logs")
        
        # Seed alert rules
        print("📢 Seeding alert rules...")
        alert_rules = [
            AlertRule(
                id=uuid.uuid4(),
                user_id=demo_user.id,
                name="High Failure Rate",
                condition="failure_rate_high",
                threshold=10.0,
                window_minutes=5,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            AlertRule(
                id=uuid.uuid4(),
                user_id=demo_user.id,
                name="High Latency",
                condition="latency_high",
                threshold=1000.0,
                window_minutes=5,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            AlertRule(
                id=uuid.uuid4(),
                user_id=demo_user.id,
                name="Rate Limit Exceeded",
                condition="rate_limit_exceeded",
                threshold=5.0,
                window_minutes=15,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        
        for rule in alert_rules:
            db.add(rule)
        
        await db.commit()
        print(f"✓ Created {len(alert_rules)} alert rules")
        
        # Seed webhook analytics
        print("📊 Seeding webhook analytics...")
        webhook_analytics = []
        now = datetime.utcnow()
        
        for provider in providers[:3]:  # Create analytics for first 3 providers
            for hours_ago in range(24):  # Last 24 hours
                hour = now - timedelta(hours=hours_ago)
                hour = hour.replace(minute=0, second=0, microsecond=0)
                
                total = 50 + (hours_ago * 5)
                successful = int(total * 0.95)
                failed = total - successful
                
                analytics = WebhookAnalytics(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    hour=hour,
                    total_webhooks=total,
                    successful_webhooks=successful,
                    failed_webhooks=failed,
                    pending_webhooks=0,
                    success_rate=95.0 + (hours_ago % 5),
                    avg_latency_ms=150.0 + (hours_ago * 10),
                    p50_latency_ms=100.0 + (hours_ago * 5),
                    p95_latency_ms=300.0 + (hours_ago * 15),
                    p99_latency_ms=500.0 + (hours_ago * 20),
                    created_at=datetime.utcnow()
                )
                webhook_analytics.append(analytics)
                db.add(analytics)
        
        await db.commit()
        print(f"✓ Created {len(webhook_analytics)} webhook analytics records")
        
        # Seed security analytics
        print("🔒 Seeding security analytics...")
        security_analytics = []
        
        for hours_ago in range(24):  # Last 24 hours
            hour = now - timedelta(hours=hours_ago)
            hour = hour.replace(minute=0, second=0, microsecond=0)
            
            analytics = SecurityAnalytics(
                id=uuid.uuid4(),
                hour=hour,
                invalid_signatures=2 + (hours_ago % 3),
                replay_attempts=1 + (hours_ago % 2),
                rate_limit_violations=0 + (hours_ago % 2),
                timestamp_errors=0,
                total_security_events=3 + (hours_ago % 5),
                created_at=datetime.utcnow()
            )
            security_analytics.append(analytics)
            db.add(analytics)
        
        await db.commit()
        print(f"✓ Created {len(security_analytics)} security analytics records")
        
        print("\n✅ Analytics seeding complete!")
        print(f"   - Audit logs: {len(audit_logs)}")
        print(f"   - Alert rules: {len(alert_rules)}")
        print(f"   - Webhook analytics: {len(webhook_analytics)}")
        print(f"   - Security analytics: {len(security_analytics)}")


if __name__ == "__main__":
    asyncio.run(seed_analytics())
