"""
Create demo user for testing
Run: python create_demo_user.py
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.auth import get_password_hash


async def create_demo_user():
    async with AsyncSessionLocal() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "demo"))
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✓ Demo user already exists")
            print(f"  Username: demo")
            print(f"  Password: demo123")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@webshield.com",
            username="demo",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        
        session.add(demo_user)
        await session.commit()
        
        print("✅ Demo user created successfully!")
        print(f"  Username: demo")
        print(f"  Password: demo123")
        print(f"  Email: demo@webshield.com")


if __name__ == "__main__":
    asyncio.run(create_demo_user())
