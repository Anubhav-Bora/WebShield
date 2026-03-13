"""
Seed security logs with realistic security events for testing and demonstration.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.security_log import SecurityLog


# Sample security events
SECURITY_EVENTS = [
    {
        "event_type": "invalid_signature",
        "details": {
            "signature": "sha256_abc123...",
            "expected": "sha256_xyz789...",
            "provider": "stripe"
        }
    },
    {
        "event_type": "rate_limit_exceeded",
        "details": {
            "limit": 100,
            "reset_at": 300,
            "provider": "shopify"
        }
    },
    {
        "event_type": "replay_attempt",
        "details": {
            "replay_key": "webhook:github:req_abc123",
            "first_seen": "2026-03-06T10:00:00Z",
            "provider": "github"
        }
    },
    {
        "event_type": "timestamp_too_old",
        "details": {
            "time_diff": 3600,
            "max_allowed": 300,
            "provider": "stripe"
        }
    },
    {
        "event_type": "payload_too_large",
        "details": {
            "size": 5242880,
            "max_allowed": 1048576,
            "provider": "shopify"
        }
    },
    {
        "event_type": "payload_tampering_detected",
        "details": {
            "webhook_id": str(uuid.uuid4()),
            "expected_hash": "abc123def456...",
            "actual_hash": "xyz789uvw012...",
            "changes": {
                "added_fields": ["malicious_field"],
                "removed_fields": [],
                "modified_fields": [
                    {
                        "field": "amount",
                        "original": 100,
                        "current": 1000
                    }
                ],
                "is_tampered": True
            }
        }
    }
]


async def seed_security_logs():
    """Seed the database with sample security events."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        now = datetime.utcnow()
        log_count = 0
        
        # Create multiple instances of each event type
        for i in range(3):  # 3 instances of each event
            for event_template in SECURITY_EVENTS:
                security_log = SecurityLog(
                    id=uuid.uuid4(),
                    provider_name=event_template["details"].get("provider", "unknown"),
                    event_type=event_template["event_type"],
                    ip_address=f"192.168.1.{100 + i}",
                    request_id=f"req_{uuid.uuid4().hex[:12]}",
                    details=event_template["details"],
                    created_at=now - timedelta(hours=i*2)
                )
                
                session.add(security_log)
                log_count += 1
        
        # Commit all changes
        await session.commit()
        print(f"✅ Seeded {log_count} security events")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🌱 Seeding security logs...")
    asyncio.run(seed_security_logs())
    print("✨ Done!")
