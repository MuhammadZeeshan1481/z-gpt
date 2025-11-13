"""
API Key Authentication Middleware
Provides simple API key-based authentication for the Z-GPT API
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-memory API key store (for production, use a database)
# Format: {"api_key": {"name": "User Name", "tier": "free|pro|enterprise"}}
API_KEYS = {
    "dev-test-key-12345": {"name": "Development", "tier": "free"},
    "demo-key-67890": {"name": "Demo User", "tier": "pro"},
}

def load_api_keys_from_env():
    """Load additional API keys from environment variables"""
    import os
    from backend.config.settings import API_KEY
    
    if API_KEY and API_KEY.strip():
        # Add the configured API key as an admin key
        API_KEYS[API_KEY] = {"name": "Admin", "tier": "enterprise"}
        logger.info("Loaded admin API key from configuration")

# Load API keys on module import
load_api_keys_from_env()

async def verify_api_key(api_key: Optional[str] = None) -> dict:
    """
    Verify API key and return key information
    
    Args:
        api_key: API key from header
        
    Returns:
        dict: API key information including name and tier
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Include X-API-Key header in your request.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    key_info = API_KEYS.get(api_key)
    if not key_info:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.debug(f"API key verified for: {key_info['name']}")
    return {
        "api_key": api_key,
        "name": key_info["name"],
        "tier": key_info["tier"]
    }

def get_api_key_tier(api_key: str) -> str:
    """Get the tier for a given API key"""
    key_info = API_KEYS.get(api_key, {})
    return key_info.get("tier", "free")

def add_api_key(api_key: str, name: str, tier: str = "free") -> bool:
    """
    Add a new API key to the system
    
    Args:
        api_key: The API key string
        name: Name/description for the key
        tier: Tier level (free, pro, enterprise)
        
    Returns:
        bool: True if added successfully
    """
    if api_key in API_KEYS:
        logger.warning(f"Attempted to add duplicate API key: {name}")
        return False
    
    API_KEYS[api_key] = {"name": name, "tier": tier}
    logger.info(f"Added new API key for: {name} (tier: {tier})")
    return True

def list_api_keys() -> dict:
    """
    List all API keys (masked) with their information
    
    Returns:
        dict: Dictionary of masked keys and their info
    """
    return {
        key[:10] + "..." if len(key) > 10 else key: info
        for key, info in API_KEYS.items()
    }
