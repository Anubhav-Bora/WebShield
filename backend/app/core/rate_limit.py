"""
Rate limiting utilities using Redis.

Implements token bucket algorithm for rate limiting.
"""
import redis.asyncio as redis
from app.core.config import settings


async def check_rate_limit(
    redis_client: redis.Redis,
    provider_id: str,
    max_requests: int = None,
    window_seconds: int = None
) -> tuple[bool, dict]:
    """
    Check if a provider has exceeded rate limit.
    
    Uses token bucket algorithm:
    - Each provider gets max_requests tokens per window_seconds
    - Each request consumes 1 token
    - Tokens refill after window expires
    
    Args:
        redis_client: Redis connection
        provider_id: Provider UUID
        max_requests: Max requests allowed (default from settings)
        window_seconds: Time window in seconds (default from settings)
    
    Returns:
        Tuple of (allowed: bool, info: dict)
        info contains: remaining_requests, reset_at, limit
    """
    if max_requests is None:
        max_requests = settings.RATE_LIMIT_MAX_REQUESTS
    if window_seconds is None:
        window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
    
    # Create rate limit key
    rate_limit_key = f"rate_limit:{provider_id}"
    
    # Get current count
    current = await redis_client.get(rate_limit_key)
    current_count = int(current) if current else 0
    
    # Check if limit exceeded
    if current_count >= max_requests:
        # Get TTL to know when limit resets
        ttl = await redis_client.ttl(rate_limit_key)
        return False, {
            "remaining_requests": 0,
            "reset_at": ttl if ttl > 0 else window_seconds,
            "limit": max_requests
        }
    
    # Increment counter
    new_count = current_count + 1
    await redis_client.setex(rate_limit_key, window_seconds, new_count)
    
    # Return success with remaining requests
    return True, {
        "remaining_requests": max_requests - new_count,
        "reset_at": window_seconds,
        "limit": max_requests
    }
