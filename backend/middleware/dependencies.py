"""
FastAPI Dependencies for authentication and rate limiting
"""
from fastapi import Depends, Request
from backend.middleware.auth import verify_api_key, api_key_header
from backend.middleware.rate_limit import rate_limit_middleware
from backend.config.settings import REQUIRE_API_KEY
from typing import Optional

async def get_api_key_optional(api_key: Optional[str] = Depends(api_key_header)) -> Optional[dict]:
    """
    Optional API key dependency - returns None if no key provided
    """
    if not api_key:
        return None
    return await verify_api_key(api_key)

async def get_api_key_required(api_key: str = Depends(api_key_header)) -> dict:
    """
    Required API key dependency - raises error if no key provided
    """
    return await verify_api_key(api_key)

async def verify_and_rate_limit(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> dict:
    """
    Combined dependency for API key verification and rate limiting
    
    - If REQUIRE_API_KEY is True, API key is required
    - If REQUIRE_API_KEY is False, API key is optional (but rate limiting still applies)
    - Rate limiting is applied based on tier (or default to free tier if no key)
    """
    # Verify API key if required or if provided
    if REQUIRE_API_KEY:
        key_info = await verify_api_key(api_key)
    elif api_key:
        key_info = await verify_api_key(api_key)
    else:
        # No API key required and none provided - use anonymous with free tier
        key_info = {
            "api_key": "anonymous",
            "name": "Anonymous",
            "tier": "free"
        }
    
    # Store API key info in request state for metrics
    request.state.api_key_info = key_info
    
    # Apply rate limiting
    await rate_limit_middleware(request, key_info)
    
    return key_info
