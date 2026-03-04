"""
Seed script to populate the database with example data
Run this to see the dashboard with realistic data
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.db.models.security_log import SecurityLog


async def clear_existing_data(session: AsyncSession):
    """Clear existing data"""
    print("🗑️  Clearing existing data...")
    
    # Delete in correct order (respecting foreign keys)
    await session.execute(text("DELETE FROM webhook_events"))
    await session.execute(text("DELETE FROM security_logs"))
    await session.execute(text("DELETE FROM providers"))
    await session.commit()
    
    print("✓ Existing data cleared")


async def seed_providers(session: AsyncSession):
    """Create sample providers"""
    print("📦 Creating sample providers...")
    
    providers_data = [
        {
            "name": "stripe",
            "forwarding_url": "https://api.example.com/webhooks/stripe",
            "secret_key": "whsec_stripe_test_key_12345",
            "is_active": True
        },
        {
            "name": "github",
            "forwarding_url": "https://api.example.com/webhooks/github",
            "secret_key": "ghp_github_webhook_secret_67890",
            "is_active": True
        },
        {
            "name": "shopify",
            "forwarding_url": "https://api.example.com/webhooks/shopify",
            "secret_key": "shpss_shopify_secret_abcdef",
            "is_active": True
        },
        {
            "name": "slack",
            "forwarding_url": "https://api.example.com/webhooks/slack",
            "secret_key": "slack_webhook_token_xyz123",
            "is_active": True
        },
        {
            "name": "twilio",
            "forwarding_url": "https://api.example.com/webhooks/twilio",
            "secret_key": "twilio_auth_token_qwerty",
            "is_active": False
        }
    ]
    
    providers = []
    for data in providers_data:
        provider = Provider(**data)
        session.add(provider)
        providers.append(provider)
    
    await session.commit()
    print(f"✓ Created {len(providers)} providers")
    return providers


async def seed_webhook_events(session: AsyncSession, providers: list):
    """Create sample webhook events"""
    print("🔗 Creating sample webhook events...")
    
    events = []
    now = datetime.utcnow()
    
    # Create events over the last 7 days
    for i in range(150):
        # Random time in the last 7 days
        days_ago = random.uniform(0, 7)
        received_at = now - timedelta(days=days_ago)
        
        # Pick random provider (weighted towards active ones)
        provider = random.choice([p for p in providers if p.is_active] * 3 + providers)
        
        # Pick status - 85% success, 10% failed, 5% pending
        rand = random.random()
        if rand < 0.85:
            signature_valid = True
            forwarded = True
            response_status = 200
            forwarded_at = received_at + timedelta(seconds=random.uniform(0.1, 2.0))
            error_message = None
        elif rand < 0.95:
            signature_valid = True
            forwarded = True
            response_status = 500
            forwarded_at = received_at + timedelta(seconds=random.uniform(0.1, 2.0))
            error_message = "Internal server error from downstream service"
        else:
            signature_valid = False
            forwarded = False
            response_status = None
            forwarded_at = None
            error_message = "Invalid HMAC signature"
        
        # Generate realistic payload based on provider
        payloads = {
            "stripe": {
                "id": f"evt_{random.randint(100000, 999999)}",
                "type": random.choice(["payment_intent.succeeded", "charge.succeeded", "customer.created"]),
                "amount": random.randint(1000, 50000),
                "currency": "usd"
            },
            "github": {
                "action": random.choice(["opened", "closed", "merged"]),
                "repository": {"name": "awesome-project", "full_name": "user/awesome-project"},
                "sender": {"login": f"user{random.randint(1, 100)}"}
            },
            "shopify": {
                "id": random.randint(1000000, 9999999),
                "order_number": random.randint(1000, 9999),
                "total_price": f"{random.randint(10, 500)}.00",
                "currency": "USD"
            },
            "slack": {
                "type": "message",
                "channel": "general",
                "user": f"U{random.randint(100000, 999999)}",
                "text": "Sample message"
            },
            "twilio": {
                "MessageSid": f"SM{random.randint(10000000, 99999999)}",
                "From": "+1234567890",
                "Body": "Sample SMS message"
            }
        }
        
        payload = payloads.get(provider.name, {"data": "sample"})
        
        # Create event
        event = WebhookEvent(
            provider_id=provider.id,
            request_id=f"req_{uuid.uuid4().hex[:16]}",
            payload=payload,
            headers={"Content-Type": "application/json", "User-Agent": f"{provider.name}-webhook/1.0"},
            signature_valid=signature_valid,
            forwarded=forwarded,
            response_status=response_status,
            response_body="OK" if response_status == 200 else None,
            error_message=error_message,
            received_at=received_at,
            forwarded_at=forwarded_at
        )
        
        session.add(event)
        events.append(event)
    
    await session.commit()
    print(f"✓ Created {len(events)} webhook events")
    return events


async def seed_security_logs(session: AsyncSession, providers: list):
    """Create sample security logs"""
    print("🛡️  Creating sample security logs...")
    
    event_types = ["rate_limit_exceeded", "invalid_signature", "replay_attempt", "invalid_timestamp"]
    
    logs = []
    now = datetime.utcnow()
    
    # Create security events over the last 7 days
    for i in range(50):
        days_ago = random.uniform(0, 7)
        created_at = now - timedelta(days=days_ago)
        
        provider = random.choice(providers)
        event_type = random.choice(event_types)
        
        # Generate details based on event type
        details_map = {
            "rate_limit_exceeded": {
                "limit": 100,
                "requests": 100 + random.randint(1, 50),
                "window": "1 minute"
            },
            "invalid_signature": {
                "expected": "valid_signature_hash",
                "received": "invalid_signature_hash",
                "algorithm": "HMAC-SHA256"
            },
            "replay_attempt": {
                "request_id": f"req_{uuid.uuid4().hex[:16]}",
                "original_timestamp": (created_at - timedelta(hours=random.randint(1, 24))).isoformat(),
                "reason": "Duplicate request ID detected"
            },
            "invalid_timestamp": {
                "timestamp": (created_at - timedelta(hours=random.randint(25, 100))).isoformat(),
                "max_age": "24 hours",
                "reason": "Timestamp too old"
            }
        }
        
        log = SecurityLog(
            provider_name=provider.name,
            event_type=event_type,
            ip_address=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            request_id=f"req_{uuid.uuid4().hex[:16]}" if random.random() > 0.3 else None,
            details=details_map[event_type],
            created_at=created_at
        )
        
        session.add(log)
        logs.append(log)
    
    await session.commit()
    print(f"✓ Created {len(logs)} security logs")
    return logs


async def main():
    """Main seed function"""
    print("\n🌱 Starting database seeding...")
    print("=" * 50)
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Seed providers
            providers = await seed_providers(session)
            
            # Seed webhook events
            await seed_webhook_events(session, providers)
            
            # Seed security logs
            await seed_security_logs(session, providers)
            
            print("=" * 50)
            print("✅ Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"  • {len(providers)} providers created")
            print(f"  • 150 webhook events created")
            print(f"  • 50 security logs created")
            print("\n🚀 Open http://localhost:3000/dashboard to see the data!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
