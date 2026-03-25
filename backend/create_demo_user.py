"""
Create demo user and seed providers for testing
Run: python create_demo_user.py
"""
import asyncio
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.provider import Provider
from app.core.auth import get_password_hash
from sqlalchemy import select


async def create_demo_user_with_seed_data():
    async with AsyncSessionLocal() as session:
        # Check if user exists - if so, just reuse it
        result = await session.execute(select(User).where(User.username == "demo"))
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✓ Demo user already exists")
            print(f"  Username: demo")
            print(f"  Password: demo123")
            print(f"  Email: demo@webshield.com")
            # Update existing user's providers if needed
            user_id = existing.id
        else:
            # Create demo user
            user_id = uuid.uuid4()
            demo_user = User(
                id=user_id,
                email="demo@webshield.com",
                username="demo",
                full_name="Demo User",
                hashed_password=get_password_hash("demo123"),
                is_active=True
            )
            
            session.add(demo_user)
            await session.flush()
        
        # Create/update seed providers for demo user
        seed_providers = [
            {
                "name": "stripe",
                "secret_key": "whsec_test_stripe_secret_key_12345",
                "forwarding_url": "http://localhost:9001/webhooks/stripe"
            },
            {
                "name": "github",
                "secret_key": "whsec_test_github_secret_key_67890",
                "forwarding_url": "http://localhost:9001/webhooks/github"
            },
            {
                "name": "shopify",
                "secret_key": "whsec_test_shopify_secret_key_abcde",
                "forwarding_url": "http://localhost:9001/webhooks/shopify"
            },
            {
                "name": "twilio",
                "secret_key": "whsec_test_twilio_secret_key_fghij",
                "forwarding_url": "http://localhost:9001/webhooks/twilio"
            }
        ]
        
        for provider_data in seed_providers:
            # Check if provider already exists
            existing_provider = await session.execute(
                select(Provider).where(Provider.name == provider_data["name"])
            )
            existing_p = existing_provider.scalar_one_or_none()
            
            if existing_p:
                # Update existing provider to belong to demo user
                existing_p.user_id = user_id
            else:
                # Create new provider
                provider = Provider(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    name=provider_data["name"],
                    secret_key=provider_data["secret_key"],
                    forwarding_url=provider_data["forwarding_url"],
                    is_active=True
                )
                session.add(provider)
        
        await session.commit()
        
        print("✅ Demo user configured successfully!")
        print(f"  Username: demo")
        print(f"  Password: demo123")
        print(f"  Email: demo@webshield.com")
        print(f"\n  Seed Providers Available:")
        for p in seed_providers:
            print(f"    - {p['name']}")


if __name__ == "__main__":
    asyncio.run(create_demo_user_with_seed_data())
