"""
Seed webhook events with realistic data for testing and demonstration.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.provider import Provider
from app.db.models.webhook_event import WebhookEvent
from app.core.payload_integrity import calculate_payload_hash


    # ...existing code...
                }
            },
            "type": "customer.subscription.created"
        }
    ],
    "shopify": [
        {
            "id": 1234567890,
            "email": "customer@example.com",
            "created_at": "2026-03-06T10:00:00Z",
            "updated_at": "2026-03-06T10:00:00Z",
            "first_name": "John",
            "last_name": "Doe",
            "orders_count": 5,
            "total_spent": "150.00",
            "currency": "USD",
            "phone": "+1234567890",
            "tags": "vip,repeat-customer",
            "note": "Preferred customer"
        },
        {
            "id": 9876543210,
            "email": "shop@example.com",
            "created_at": "2026-03-05T15:30:00Z",
            "updated_at": "2026-03-06T09:15:00Z",
            "first_name": "Jane",
            "last_name": "Smith",
            "orders_count": 12,
            "total_spent": "450.50",
            "currency": "USD",
            "phone": "+9876543210",
            "tags": "vip,wholesale",
            "note": "Wholesale account"
        }
    ],
    "github": [
        {
            "action": "opened",
            "number": 42,
            "pull_request": {
                "id": 1234567890,
                "title": "Add payload integrity verification",
                "user": {
                    "login": "developer",
                    "id": 12345
                },
                "created_at": "2026-03-06T10:00:00Z",
                "updated_at": "2026-03-06T10:00:00Z",
                "state": "open",
                "additions": 150,
                "deletions": 25
            },
            "repository": {
                "id": 987654321,
                "name": "webhook-gateway",
                "full_name": "company/webhook-gateway",
                "private": False
            }
        },
        {
            "action": "synchronize",
            "number": 42,
            "pull_request": {
                "id": 1234567890,
                "title": "Add payload integrity verification",
                "user": {
                    "login": "developer",
                    "id": 12345
                },
                "created_at": "2026-03-06T10:00:00Z",
                "updated_at": "2026-03-06T11:30:00Z",
                "state": "open",
                "additions": 200,
                "deletions": 40
            },
            "repository": {
                "id": 987654321,
                "name": "webhook-gateway",
                "full_name": "company/webhook-gateway",
                "private": False
            }
        }
    ]
}


async def seed_webhooks():
    """Seed the database with sample webhook events."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get existing providers
        from sqlalchemy import select
        result = await session.execute(select(Provider))
        providers = result.scalars().all()
        
        if not providers:
            print("❌ No providers found. Please create providers first.")
            await engine.dispose()
            return
        
        # Create webhook events for each provider
        webhook_count = 0
        now = datetime.utcnow()
        
        for provider in providers:
            provider_name = provider.name.lower()
            
            if provider_name not in SAMPLE_PAYLOADS:
                print(f"⏭️  Skipping {provider_name} - no sample data available")
                continue
            
            payloads = SAMPLE_PAYLOADS[provider_name]
            
            for i, payload in enumerate(payloads):
                # Create webhook event
                webhook_event = WebhookEvent(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    request_id=f"req_{uuid.uuid4().hex[:12]}",
                    source=provider_name,
                    payload=payload,
                    payload_hash=calculate_payload_hash(payload),
                    headers={
                        "X-Signature": f"sha256={uuid.uuid4().hex[:32]}",
                        "X-Timestamp": (now - timedelta(minutes=i*5)).isoformat(),
                        "X-Request-ID": f"req_{uuid.uuid4().hex[:12]}",
                        "Content-Type": "application/json",
                        "User-Agent": f"{provider_name}/webhook-v1"
                    },
                    signature_valid=True,
                    forwarded=i % 2 == 0,  # Alternate between forwarded and pending
                    response_status=200 if i % 2 == 0 else None,
                    received_at=now - timedelta(minutes=i*5)
                )
                
                session.add(webhook_event)
                webhook_count += 1
        
        # Commit all changes
        await session.commit()
        print(f"✅ Seeded {webhook_count} webhook events")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🌱 Seeding webhook events...")
    asyncio.run(seed_webhooks())
    print("✨ Done!")
