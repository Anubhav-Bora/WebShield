"""
Rate limiting utilities using Redis.

Implements token bucket algorithm for rate limiting with atomic operations.
"""
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def check_rate_limit(
    redis_client: redis.Redis,
    provider_id: str,
    max_requests: int = None,
    window_seconds: int = None
) -> tuple[bool, dict]:
    """
    Check if a provider has exceeded rate limit using atomic Redis operations.
    
    Uses token bucket algorithm with Lua script for atomicity:
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
    
    # Lua script for atomic rate limit check and increment
    # This prevents race conditions between check and set
    # Uses a fixed window approach with proper TTL handling
    lua_script = """
    local key = KEYS[1]
    local max_requests = tonumber(ARGV[1])
    local window_seconds = tonumber(ARGV[2])
    
    local current = redis.call('GET', key)
    local current_count = current and tonumber(current) or 0
    
    -- If we've already hit the limit, reject
    if current_count >= max_requests then
        local ttl = redis.call('TTL', key)
        -- TTL returns -1 if key exists but has no expiry, -2 if key doesn't exist
        -- In both cases, use window_seconds as the reset time
        local reset_time = ttl > 0 and ttl or window_seconds
        return {0, reset_time}
    end
    
    -- Increment counter
    local new_count = current_count + 1
    
    -- Always use SETEX to preserve the time window
    -- If this is the first request (current_count==0), use full window_seconds
    -- For subsequent requests, get remaining TTL and apply it
    local ttl = redis.call('TTL', key)
    local remaining_ttl = ttl > 0 and ttl or window_seconds
    
    redis.call('SETEX', key, remaining_ttl, new_count)
    
    -- Return: allowed=1, remaining_requests
    return {1, max_requests - new_count}
    """
    
    try:
        result = await redis_client.eval(
            lua_script,
            1,
            rate_limit_key,
            max_requests,
            window_seconds
        )
        
        allowed = result[0] == 1
        
        if allowed:
            remaining = result[1]
            reset_at = window_seconds
            logger.info(f"✓ Rate limit check PASSED for {provider_id}: {remaining} requests remaining (limit: {max_requests})")
        else:
            remaining = 0
            reset_at = result[1]
            logger.warning(f"✗ Rate limit EXCEEDED for {provider_id}: reset in {reset_at}s (limit: {max_requests})")
        
        return allowed, {
            "remaining_requests": remaining,
            "reset_at": reset_at,
            "limit": max_requests
        }
    except Exception as e:
        # If Redis fails, allow request but log error
        # This prevents Redis outage from blocking webhooks
        logger.error(f"✗ Rate limit check FAILED: {str(e)}")
        return True, {
            "remaining_requests": max_requests,
            "reset_at": window_seconds,
            "limit": max_requests
        }
