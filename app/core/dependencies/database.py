from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.config.database import get_db
from app.config.redis import get_redis

PostgresDB = Annotated[AsyncSession, Depends(get_db)]
RedisCache = Annotated[Redis, Depends(get_redis)]
