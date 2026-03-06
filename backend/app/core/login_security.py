"""
Login security utilities - brute force protection, account lockout, etc.
"""
import redis.asyncio as redis
from app.core.config import settings


async def check_login_attempts(
    redis_client: redis.Redis,
    username: str,
    client_ip: str
) -> tuple[bool, dict]:
    """
    Check if login attempts exceed rate limit.
    
    Args:
        redis_client: Redis connection
        username: Username attempting to login
        client_ip: Client IP address
    
    Returns:
        Tuple of (allowed: bool, info: dict)
        - allowed: True if login attempt is allowed
        - info: Contains remaining_attempts, reset_at (seconds)
    """
    # Create keys for both username and IP tracking
    username_key = f"login_attempts:username:{username}"
    ip_key = f"login_attempts:ip:{client_ip}"
    
    # Check username-based limit
    username_attempts = await redis_client.incr(username_key)
    if username_attempts == 1:
        await redis_client.expire(username_key, settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    
    # Check IP-based limit
    ip_attempts = await redis_client.incr(ip_key)
    if ip_attempts == 1:
        await redis_client.expire(ip_key, settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    
    # Get TTL for response
    username_ttl = await redis_client.ttl(username_key)
    ip_ttl = await redis_client.ttl(ip_key)
    
    # Check if either limit exceeded
    if username_attempts > settings.LOGIN_RATE_LIMIT_ATTEMPTS:
        return False, {
            "limit": settings.LOGIN_RATE_LIMIT_ATTEMPTS,
            "reset_at": username_ttl,
            "reason": "too_many_attempts_for_username"
        }
    
    if ip_attempts > settings.LOGIN_RATE_LIMIT_ATTEMPTS * 3:  # 3x more lenient for IP
        return False, {
            "limit": settings.LOGIN_RATE_LIMIT_ATTEMPTS * 3,
            "reset_at": ip_ttl,
            "reason": "too_many_attempts_from_ip"
        }
    
    return True, {
        "remaining_attempts": settings.LOGIN_RATE_LIMIT_ATTEMPTS - username_attempts,
        "reset_at": username_ttl
    }


async def reset_login_attempts(
    redis_client: redis.Redis,
    username: str,
    client_ip: str
) -> None:
    """
    Reset login attempts after successful login.
    
    Args:
        redis_client: Redis connection
        username: Username that successfully logged in
        client_ip: Client IP address
    """
    username_key = f"login_attempts:username:{username}"
    ip_key = f"login_attempts:ip:{client_ip}"
    
    await redis_client.delete(username_key)
    await redis_client.delete(ip_key)
