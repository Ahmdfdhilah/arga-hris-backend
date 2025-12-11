"""
Redis distributed lock untuk mencegah duplicate job execution
ketika running multiple instances.
"""

import redis.asyncio as aioredis
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class RedisLock:
    """
    Distributed lock menggunakan Redis untuk single-execution guarantee.
    """

    def __init__(self, redis_client: aioredis.Redis, lock_prefix: str = "scheduler_lock"):
        self.redis = redis_client
        self.lock_prefix = lock_prefix

    def _get_lock_key(self, job_id: str) -> str:
        """Generate Redis key untuk lock"""
        return f"{self.lock_prefix}:{job_id}"

    async def acquire(
        self,
        job_id: str,
        timeout_seconds: int = 300,
        blocking_timeout: int = 5
    ) -> bool:
        """
        Acquire lock untuk job.
        
        Args:
            job_id: ID job yang akan di-lock
            timeout_seconds: TTL lock di Redis (default 5 menit)
            blocking_timeout: Timeout untuk acquire lock (default 5 detik)
            
        Returns:
            True jika berhasil acquire lock, False jika gagal
        """
        lock_key = self._get_lock_key(job_id)
        
        try:
            # SET NX EX: Set if Not eXists with EXpiration
            # Handle both decode_responses=True and False
            result = await self.redis.set(
                lock_key,
                "locked",
                nx=True,
                ex=timeout_seconds
            )
            
            # Result bisa True, 1, "OK", atau None tergantung decode_responses
            if result:
                logger.info(f"Lock acquired untuk job: {job_id}")
                return True
            else:
                logger.warning(
                    f"Gagal acquire lock untuk job: {job_id}. "
                    "Job mungkin sedang dijalankan instance lain."
                )
                return False
                
        except Exception as e:
            logger.error(f"Error saat acquire lock untuk {job_id}: {e}")
            return False

    async def release(self, job_id: str) -> bool:
        """
        Release lock untuk job.
        
        Args:
            job_id: ID job yang akan di-release
            
        Returns:
            True jika berhasil release
        """
        lock_key = self._get_lock_key(job_id)
        
        try:
            result = await self.redis.delete(lock_key)
            if result:
                logger.info(f"Lock released untuk job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error saat release lock untuk {job_id}: {e}")
            return False

    async def is_locked(self, job_id: str) -> bool:
        """
        Check apakah job sedang di-lock.
        
        Args:
            job_id: ID job yang akan dicek
            
        Returns:
            True jika sedang locked
        """
        lock_key = self._get_lock_key(job_id)
        exists = await self.redis.exists(lock_key)
        return bool(exists)

    async def extend_lock(self, job_id: str, additional_seconds: int = 60) -> bool:
        """
        Extend TTL lock jika job masih berjalan.
        
        Args:
            job_id: ID job
            additional_seconds: Tambahan waktu dalam detik
            
        Returns:
            True jika berhasil extend
        """
        lock_key = self._get_lock_key(job_id)
        
        try:
            ttl = await self.redis.ttl(lock_key)
            if ttl > 0:
                await self.redis.expire(lock_key, ttl + additional_seconds)
                logger.info(f"Lock extended untuk job: {job_id} (+{additional_seconds}s)")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saat extend lock untuk {job_id}: {e}")
            return False


async def with_redis_lock(
    redis_client: aioredis.Redis,
    job_id: str,
    func: Callable,
    timeout_seconds: int = 300
) -> Optional[dict]:
    """
    Context manager-like helper untuk execute function dengan Redis lock.
    
    Args:
        redis_client: Redis client instance
        job_id: ID job untuk locking
        func: Async function yang akan dijalankan
        timeout_seconds: Lock timeout
        
    Returns:
        Result dari func atau None jika gagal acquire lock
    """
    lock = RedisLock(redis_client)
    
    if not await lock.acquire(job_id, timeout_seconds=timeout_seconds):
        logger.warning(f"Skip execution job {job_id} karena sudah ada instance lain yang menjalankan")
        return None
    
    try:
        result = await func()
        return result
    finally:
        await lock.release(job_id)
