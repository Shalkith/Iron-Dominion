"""Redis client configuration."""
import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

# Create Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis():
    """Get Redis client instance."""
    return redis_client


async def set_cache(key: str, value: str, expire: int = None):
    """Set a value in Redis cache."""
    await redis_client.set(key, value, ex=expire)


async def get_cache(key: str) -> str | None:
    """Get a value from Redis cache."""
    return await redis_client.get(key)


async def delete_cache(key: str):
    """Delete a value from Redis cache."""
    await redis_client.delete(key)
