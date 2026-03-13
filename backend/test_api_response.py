import asyncio
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models.user import User
from sqlalchemy import select
import uuid

    # ...existing code...
        return None

# Test the endpoint
async def test():
    token = await get_token()
    if not token:
        print("No demo user found")
        return
    
    print(f"Token: {token[:50]}...")
    
    # Make request
    response = client.get(
        "http://localhost:8000/admin/analytics/webhooks?days=7",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response length: {len(response.text)}")
    
    data = response.json()
    print(f"Data points: {len(data)}")
    
    if data:
        print(f"\nFirst point keys: {list(data[0].keys())}")
        print(f"First point: {json.dumps(data[0], indent=2)}")

asyncio.run(test())
