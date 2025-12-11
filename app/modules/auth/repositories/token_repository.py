"""
Token Repository for Redis Operations

Handles token blacklist and token-related operations in Redis.
"""

import time
from typing import  List, Dict
from redis.asyncio import Redis
from jose import jwt


class TokenRepository:
    """Repository for token blacklist management in Redis"""

    def __init__(self, redis: Redis):
        """
        Initialize TokenRepository

        Args:
            redis: Redis client instance
        """
        self.redis = redis

    async def blacklist_token(self, token: str) -> bool:
        """
        Blacklist a token in Redis with TTL = remaining token lifetime

        Args:
            token: JWT token string

        Returns:
            True if blacklisted successfully, False if token already expired
        """
        try:
            # Decode token without verification (we're blacklisting anyway)
            payload = jwt.get_unverified_claims(token)

            jti = payload.get("jti")
            exp = payload.get("exp")

            if not jti or not exp:
                return False

            # Calculate remaining TTL
            current_time = int(time.time())
            remaining_ttl = exp - current_time

            # Only blacklist if token hasn't expired yet
            if remaining_ttl > 0:
                key = f"blacklist:{jti}"
                await self.redis.setex(key, remaining_ttl, "1")
                return True

            # Token already expired, no need to blacklist
            return False

        except Exception:
            return False

    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if a token is blacklisted

        Args:
            jti: Token JTI (unique identifier)

        Returns:
            True if blacklisted, False otherwise
        """
        key = f"blacklist:{jti}"
        result = await self.redis.exists(key)
        return result > 0

    async def revoke_all_user_tokens(
        self,
        user_id: str,
        max_token_lifetime: int = 900  # 15 minutes default
    ) -> bool:
        """
        Revoke all tokens for a specific user
        Useful for: password change, account compromised, etc.

        Args:
            user_id: User ID
            max_token_lifetime: Maximum token lifetime in seconds

        Returns:
            True if revoked successfully
        """
        key = f"user_revoked:{user_id}"
        await self.redis.setex(key, max_token_lifetime, "1")
        return True

    async def is_user_revoked(self, user_id: str) -> bool:
        """
        Check if all user tokens are revoked

        Args:
            user_id: User ID

        Returns:
            True if user is revoked, False otherwise
        """
        key = f"user_revoked:{user_id}"
        result = await self.redis.exists(key)
        return result > 0

    async def unrevoke_user(self, user_id: str) -> bool:
        """
        Remove user-level revocation
        Call this after user resets password or resolves security issue

        Args:
            user_id: User ID

        Returns:
            True if unrevoked successfully
        """
        key = f"user_revoked:{user_id}"
        result = await self.redis.delete(key)
        return result > 0

    async def get_blacklist_stats(self) -> Dict[str, int]:
        """
        Get statistics about blacklisted tokens
        Useful for monitoring

        Returns:
            Dict with blacklist statistics
        """
        blacklist_count = 0
        revoked_users_count = 0

        # Count blacklisted tokens
        async for key in self.redis.scan_iter(match="blacklist:*"):
            blacklist_count += 1

        # Count revoked users
        async for key in self.redis.scan_iter(match="user_revoked:*"):
            revoked_users_count += 1

        return {
            "blacklisted_tokens": blacklist_count,
            "revoked_users": revoked_users_count,
        }

    async def cleanup_expired_blacklist(self) -> int:
        """
        Manual cleanup of expired blacklist entries
        Note: Redis auto-expires with TTL, this is just for manual cleanup if needed

        Returns:
            Number of entries cleaned up
        """
        deleted_count = 0
        current_time = int(time.time())

        async for key in self.redis.scan_iter(match="blacklist:*"):
            ttl = await self.redis.ttl(key)
            if ttl < 0:  # Key exists but no TTL (shouldn't happen)
                await self.redis.delete(key)
                deleted_count += 1

        return deleted_count

    async def batch_check_blacklist(self, jtis: List[str]) -> Dict[str, bool]:
        """
        Check multiple tokens at once for blacklist status
        Efficient for batch operations

        Args:
            jtis: List of token JTIs

        Returns:
            Dict mapping JTI to blacklist status
        """
        if not jtis:
            return {}

        keys = [f"blacklist:{jti}" for jti in jtis]
        results = await self.redis.mget(keys)

        return {jti: bool(result) for jti, result in zip(jtis, results)}
