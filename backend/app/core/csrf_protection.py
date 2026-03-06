"""
CSRF protection utilities.

Implements CSRF token generation and validation.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.core.config import settings


async def generate_csrf_token(redis_client: redis.Redis, session_id: str) -> str:
    """
    Generate a CSRF token for a session.
    
    Args:
        redis_client: Redis connection
        session_id: Session identifier
    
    Returns:
        CSRF token string
    """
    # Generate random token
    token = secrets.token_urlsafe(32)
    
    # Store in Redis with TTL (1 hour)
    csrf_key = f"csrf_token:{session_id}"
    await redis_client.setex(csrf_key, 3600, token)
    
    return token


async def verify_csrf_token(redis_client: redis.Redis, session_id: str, token: str) -> bool:
    """
    Verify a CSRF token.
    
    Args:
        redis_client: Redis connection
        session_id: Session identifier
        token: Token to verify
    
    Returns:
        True if token is valid, False otherwise
    """
    csrf_key = f"csrf_token:{session_id}"
    stored_token = await redis_client.get(csrf_key)
    
    if not stored_token:
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(stored_token, token)


async def invalidate_csrf_token(redis_client: redis.Redis, session_id: str) -> None:
    """
    Invalidate a CSRF token after use.
    
    Args:
        redis_client: Redis connection
        session_id: Session identifier
    """
    csrf_key = f"csrf_token:{session_id}"
    await redis_client.delete(csrf_key)
