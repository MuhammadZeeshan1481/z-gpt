"""
Rate Limiting Middleware
Provides in-memory rate limiting per API key
"""
from fastapi import Request, HTTPException, status
from typing import Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Rate limit storage: {api_key: [(timestamp, count), ...]}
# Format: {"api_key": [(datetime, request_count), ...]}
rate_limit_store: Dict[str, list] = defaultdict(list)

# Tier-based rate limits (requests per minute)
RATE_LIMITS = {
    "free": 10,
    "pro": 60,
    "enterprise": 300,
}

def get_rate_limit(tier: str) -> int:
    """Get rate limit for a specific tier"""
    return RATE_LIMITS.get(tier, 10)

def clean_old_requests(api_key: str, window_minutes: int = 1):
    """Remove requests older than the time window"""
    cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
    rate_limit_store[api_key] = [
        (timestamp, count) for timestamp, count in rate_limit_store[api_key]
        if timestamp > cutoff_time
    ]

def check_rate_limit(api_key: str, tier: str = "free") -> Tuple[bool, dict]:
    """
    Check if the API key has exceeded the rate limit
    
    Args:
        api_key: The API key to check
        tier: The tier of the API key (free, pro, enterprise)
        
    Returns:
        Tuple of (is_allowed: bool, rate_info: dict)
    """
    # Clean old requests
    clean_old_requests(api_key)
    
    # Get rate limit for tier
    limit = get_rate_limit(tier)
    
    # Count requests in the last minute
    current_count = sum(count for _, count in rate_limit_store[api_key])
    
    # Check if limit exceeded
    is_allowed = current_count < limit
    
    # Add current request if allowed
    if is_allowed:
        rate_limit_store[api_key].append((datetime.now(), 1))
        current_count += 1
    
    rate_info = {
        "limit": limit,
        "remaining": max(0, limit - current_count),
        "used": current_count,
        "tier": tier,
        "reset_in_seconds": 60
    }
    
    return is_allowed, rate_info

async def rate_limit_middleware(request: Request, api_key_info: dict):
    """
    Rate limiting middleware
    
    Args:
        request: The request object
        api_key_info: Dictionary with API key information
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    api_key = api_key_info.get("api_key", "unknown")
    tier = api_key_info.get("tier", "free")
    
    is_allowed, rate_info = check_rate_limit(api_key, tier)
    
    # Add rate limit headers to request state
    request.state.rate_limit_info = rate_info
    
    if not is_allowed:
        logger.warning(
            f"Rate limit exceeded for API key: {api_key[:10]}... "
            f"(tier: {tier}, limit: {rate_info['limit']}/min)"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "limit": rate_info["limit"],
                "tier": tier,
                "reset_in_seconds": 60,
                "message": f"You have exceeded the rate limit of {rate_info['limit']} requests per minute for the {tier} tier."
            }
        )
    
    logger.debug(
        f"Rate limit check passed: {api_key[:10]}... "
        f"({rate_info['used']}/{rate_info['limit']})"
    )

def get_rate_limit_stats() -> dict:
    """Get current rate limit statistics"""
    stats = {}
    for api_key, requests in rate_limit_store.items():
        clean_old_requests(api_key)
        total = sum(count for _, count in requests)
        stats[api_key[:10] + "..."] = {
            "requests_last_minute": total,
            "last_request": max((ts for ts, _ in requests), default=None)
        }
    return stats
