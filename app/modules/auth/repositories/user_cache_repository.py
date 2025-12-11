"""
User Cache Repository for Redis Operations

Caches user data to reduce database queries and improve performance.
"""

import json
from typing import Optional, Dict, Any
from redis.asyncio import Redis


class UserCacheRepository:
    """Repository for user data caching in Redis"""

    def __init__(self, redis: Redis):
        """
        Initialize UserCacheRepository

        Args:
            redis: Redis client instance
        """
        self.redis = redis
        self.default_ttl = 900  # 15 minutes (same as access token)

    async def cache_user_data(
        self,
        user_id: int,
        user_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache user data in Redis

        Args:
            user_id: User ID
            user_data: User data dictionary including roles and permissions
            ttl: TTL in seconds (default: 900 = 15 min)

        Returns:
            True if cached successfully
        """
        if ttl is None:
            ttl = self.default_ttl

        key = f"user_cache:{user_id}"
        await self.redis.setex(key, ttl, json.dumps(user_data))
        return True

    async def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached user data from Redis

        Args:
            user_id: User ID

        Returns:
            User data dict or None if not cached
        """
        key = f"user_cache:{user_id}"
        data = await self.redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def invalidate_user_cache(self, user_id: int) -> bool:
        """
        Invalidate (delete) cached user data
        Call this when user data changes (roles, permissions, profile, etc.)

        Args:
            user_id: User ID

        Returns:
            True if deleted successfully
        """
        key = f"user_cache:{user_id}"
        result = await self.redis.delete(key)
        return result > 0

    async def refresh_user_cache(
        self,
        user_id: int,
        user_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Refresh user cache with new data
        Alias for cache_user_data for semantic clarity

        Args:
            user_id: User ID
            user_data: User data dictionary
            ttl: TTL in seconds

        Returns:
            True if refreshed successfully
        """
        return await self.cache_user_data(user_id, user_data, ttl)

    async def get_cache_ttl(self, user_id: int) -> int:
        """
        Get remaining TTL for cached user data

        Args:
            user_id: User ID

        Returns:
            Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        key = f"user_cache:{user_id}"
        return await self.redis.ttl(key)

    async def cache_exists(self, user_id: int) -> bool:
        """
        Check if user cache exists

        Args:
            user_id: User ID

        Returns:
            True if cache exists, False otherwise
        """
        key = f"user_cache:{user_id}"
        result = await self.redis.exists(key)
        return result > 0

    async def get_cached_user_count(self) -> int:
        """
        Get count of cached users
        Useful for monitoring

        Returns:
            Number of cached users
        """
        count = 0
        async for key in self.redis.scan_iter(match="user_cache:*"):
            count += 1
        return count

    async def bulk_invalidate_users(self, user_ids: list[int]) -> int:
        """
        Invalidate cache for multiple users at once
        Useful for bulk operations

        Args:
            user_ids: List of user IDs

        Returns:
            Number of caches invalidated
        """
        if not user_ids:
            return 0

        keys = [f"user_cache:{user_id}" for user_id in user_ids]
        return await self.redis.delete(*keys)

    async def clear_all_user_cache(self) -> int:
        """
        Clear all user caches
        WARNING: Use with caution, only for maintenance/debugging

        Returns:
            Number of caches cleared
        """
        deleted_count = 0
        keys = []

        async for key in self.redis.scan_iter(match="user_cache:*"):
            keys.append(key)

        if keys:
            deleted_count = await self.redis.delete(*keys)

        return deleted_count
