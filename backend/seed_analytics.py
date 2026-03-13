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
        
        import random
        
        for provider in providers[:3]:  # Create analytics for first 3 providers
            for days_ago in range(7):  # Last 7 days
                for hours_in_day in range(24):  # Each hour of the day
                    hour = now - timedelta(days=days_ago, hours=hours_in_day)
                    hour = hour.replace(minute=0, second=0, microsecond=0)
                    
                    # Add realistic variation based on time patterns
                    hour_of_day = hour.hour
                    
                    # Peak hours (9-17): more traffic
                    if 9 <= hour_of_day <= 17:
                        base_total = 120 + random.randint(-30, 50)
                        success_rate = 96.0 + random.uniform(-2, 2)
                    # Evening (18-22): moderate traffic
                    elif 18 <= hour_of_day <= 22:
                        base_total = 80 + random.randint(-20, 30)
                        success_rate = 94.5 + random.uniform(-2, 2)
                    # Night (23-8): low traffic
                    else:
                        base_total = 40 + random.randint(-10, 20)
                        success_rate = 97.0 + random.uniform(-1, 1)
                    
                    total = max(10, base_total)
                    successful = int(total * (success_rate / 100.0))
                    failed = total - successful
                    
                    # Latency varies with traffic
                    base_latency = 120 + (total / 5)
                    avg_latency = base_latency + random.randint(-30, 40)
                    
                    analytics = WebhookAnalytics(
                        id=uuid.uuid4(),
                        provider_id=provider.id,
                        hour=hour,
                        total_webhooks=total,
                        successful_webhooks=successful,
                        failed_webhooks=failed,
                        pending_webhooks=0,
                        success_rate=success_rate,
                        avg_latency_ms=avg_latency,
                        p50_latency_ms=avg_latency * 0.6,
                        p95_latency_ms=avg_latency * 1.7,
                        p99_latency_ms=avg_latency * 2.3,
                        created_at=datetime.utcnow()
                    )
                    webhook_analytics.append(analytics)
                    db.add(analytics)
        
        await db.commit()
        print(f"✓ Created {len(webhook_analytics)} webhook analytics records")
        
        # Seed security analytics
        print("🔒 Seeding security analytics...")
        security_analytics = []
        
        for days_ago in range(7):  # Last 7 days
            for hours_in_day in range(24):  # Each hour of the day
                hour = now - timedelta(days=days_ago, hours=hours_in_day)
                hour = hour.replace(minute=0, second=0, microsecond=0)
                
                # More security events during business hours
                hour_of_day = hour.hour
                if 9 <= hour_of_day <= 17:
                    base_events = 5 + (hours_in_day % 4)
                else:
                    base_events = 1 + (hours_in_day % 2)
                
                invalid_sigs = base_events + random.randint(-1, 2)
                replay_attempts = max(0, base_events // 2 + random.randint(-1, 1))
                rate_violations = max(0, base_events // 3 + random.randint(0, 1))
                
                analytics = SecurityAnalytics(
                    id=uuid.uuid4(),
                    hour=hour,
                    invalid_signatures=max(0, invalid_sigs),
                    replay_attempts=max(0, replay_attempts),
                    rate_limit_violations=max(0, rate_violations),
                    timestamp_errors=0,
                    total_security_events=max(0, invalid_sigs + replay_attempts + rate_violations),
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
