"""
Redis client management
"""
import redis.asyncio as redis
from typing import Optional
from .settings import get_settings

settings = get_settings()

redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global redis_client
    
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        print("Redis client connected")
    
    return redis_client


async def close_redis_client():
    """Close Redis connection"""
    global redis_client
    
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
        print("Redis client closed")
