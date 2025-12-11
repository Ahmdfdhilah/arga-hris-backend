"""
Scheduler Manager untuk mengatur lifecycle scheduled jobs.
Menggunakan APScheduler dengan AsyncIOScheduler.
"""

from typing import List, Dict, Any, Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import redis.asyncio as aioredis
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.core.scheduler.redis_lock import with_redis_lock

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Manager untuk scheduled jobs dengan APScheduler.
    Menangani registration, start/stop, dan execution dengan Redis lock.
    """

    def __init__(self, redis_client: aioredis.Redis):
        """
        Initialize scheduler manager.
        
        Args:
            redis_client: Redis client untuk distributed locking
        """
        self.redis_client = redis_client
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            timezone='Asia/Jakarta'
        )
        self.registered_jobs: Dict[str, BaseScheduledJob] = {}
        self.log_callback: Optional[Callable] = None

    def set_log_callback(self, callback: Callable):
        """
        Set callback untuk logging job execution ke database.
        
        Args:
            callback: Async function untuk save log
        """
        self.log_callback = callback

    def register_job(self, job: BaseScheduledJob):
        """
        Register scheduled job.
        
        Args:
            job: Instance dari BaseScheduledJob
        """
        if not job.enabled:
            logger.info(f"Job {job.job_id} disabled, skip registration")
            return

        if job.job_id in self.registered_jobs:
            logger.warning(f"Job {job.job_id} sudah terdaftar, akan di-replace")

        self.registered_jobs[job.job_id] = job

        # Create wrapped execution function dengan Redis lock
        async def execute_with_lock():
            result = await with_redis_lock(
                redis_client=self.redis_client,
                job_id=job.job_id,
                func=lambda: job.run_with_logging(log_callback=self.log_callback),
                timeout_seconds=600  # 10 menit lock timeout
            )
            
            if result is None:
                logger.info(f"Job {job.job_id} di-skip (sudah ada instance lain yang menjalankan)")

        # Get schedule config dan add job ke scheduler
        schedule_config = job.get_schedule_config()
        schedule_config["func"] = execute_with_lock

        self.scheduler.add_job(**schedule_config)
        
        logger.info(
            f"Job registered: {job.job_id} - {job.description} "
            f"(cron: {job.cron or 'N/A'}, interval: {job.interval_seconds or 'N/A'}s)"
        )

    def register_multiple(self, jobs: List[BaseScheduledJob]):
        """
        Register multiple jobs sekaligus.
        
        Args:
            jobs: List of job instances
        """
        for job in jobs:
            try:
                self.register_job(job)
            except Exception as e:
                logger.error(f"Gagal register job {getattr(job, 'job_id', 'unknown')}: {e}")

    def start(self):
        """Start scheduler (non-blocking)"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info(f"Scheduler started dengan {len(self.registered_jobs)} jobs")
        else:
            logger.warning("Scheduler sudah running")

    def shutdown(self, wait: bool = True):
        """
        Shutdown scheduler.
        
        Args:
            wait: Wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler stopped")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status job dari scheduler.
        
        Args:
            job_id: ID job
            
        Returns:
            Dict dengan info job atau None jika tidak ditemukan
        """
        job = self.scheduler.get_job(job_id)
        if not job:
            return None

        registered_job = self.registered_jobs.get(job_id)
        
        return {
            "job_id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "enabled": registered_job.enabled if registered_job else True,
            "description": registered_job.description if registered_job else None,
        }

    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List semua registered jobs.
        
        Returns:
            List dict dengan info semua jobs
        """
        jobs = []
        for job_id in self.registered_jobs.keys():
            status = self.get_job_status(job_id)
            if status:
                jobs.append(status)
        return jobs

    async def trigger_job_manual(self, job_id: str) -> Dict[str, Any]:
        """
        Trigger job secara manual (untuk testing/admin).
        
        Args:
            job_id: ID job yang akan di-trigger
            
        Returns:
            Dict hasil eksekusi
        """
        job = self.registered_jobs.get(job_id)
        if not job:
            return {
                "success": False,
                "message": f"Job {job_id} tidak ditemukan",
            }

        logger.info(f"Manual trigger job: {job_id}")
        
        # Execute dengan lock
        result = await with_redis_lock(
            redis_client=self.redis_client,
            job_id=f"{job_id}_manual",
            func=lambda: job.run_with_logging(log_callback=self.log_callback),
            timeout_seconds=600
        )

        if result is None:
            return {
                "success": False,
                "message": f"Job {job_id} sedang dijalankan oleh instance lain",
            }

        return result

    def pause_job(self, job_id: str):
        """Pause job sementara"""
        self.scheduler.pause_job(job_id)
        logger.info(f"Job {job_id} di-pause")

    def resume_job(self, job_id: str):
        """Resume paused job"""
        self.scheduler.resume_job(job_id)
        logger.info(f"Job {job_id} di-resume")

    def remove_job(self, job_id: str):
        """Remove job dari scheduler"""
        if job_id in self.registered_jobs:
            del self.registered_jobs[job_id]
        self.scheduler.remove_job(job_id)
        logger.info(f"Job {job_id} dihapus dari scheduler")


# Global instance (akan di-initialize di startup)
_scheduler_instance: Optional[SchedulerManager] = None


def get_scheduler() -> Optional[SchedulerManager]:
    """Get global scheduler instance"""
    return _scheduler_instance


def init_scheduler(redis_client: aioredis.Redis) -> SchedulerManager:
    """
    Initialize global scheduler instance.
    
    Args:
        redis_client: Redis client instance
        
    Returns:
        Scheduler manager instance
    """
    global _scheduler_instance
    _scheduler_instance = SchedulerManager(redis_client)
    return _scheduler_instance
