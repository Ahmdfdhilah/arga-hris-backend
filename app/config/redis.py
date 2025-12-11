import redis.asyncio as redis
from typing import AsyncGenerator
from app.config.settings import settings

# Create Redis client
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)


# Dependency
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Redis client dependency"""
    try:
        yield redis_client
    finally:
        pass  # Connection pool managed by redis client
