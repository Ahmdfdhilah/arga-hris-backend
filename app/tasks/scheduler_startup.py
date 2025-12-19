"""
Scheduler startup logic untuk initialize dan register semua jobs.
Dipanggil pada FastAPI startup event.
"""

import logging
from typing import Optional
from datetime import datetime

from app.config.redis import redis_client
from app.config.database import get_db_context
from app.core.scheduler.manager import init_scheduler
from app.modules.scheduled_jobs.repositories.job_execution_repository import (
    JobExecutionRepository,
)
from app.modules.scheduled_jobs.services.job_management_service import (
    JobManagementService,
)

from app.modules.scheduled_jobs.jobs.auto_create_daily_attendance import (
    AutoCreateDailyAttendanceJob,
)
from app.modules.scheduled_jobs.jobs.mark_invalid_no_checkout import (
    MarkInvalidNoCheckoutJob,
)
from app.modules.scheduled_jobs.jobs.process_assignments import ProcessAssignmentsJob
from app.modules.scheduled_jobs.jobs.cleanup_temporary_roles import (
    CleanupTemporaryRolesJob,
)

logger = logging.getLogger(__name__)


async def setup_scheduler():
    """
    Setup dan start scheduler dengan semua registered jobs.
    Dipanggil pada FastAPI startup.
    """
    try:
        logger.info("Initializing scheduler...")

        await redis_client.ping()
        logger.info("Redis connection established untuk scheduler")

        # Initialize scheduler manager
        scheduler = init_scheduler(redis_client)

        # Setup log callback untuk save execution logs ke database
        async def log_execution_callback(
            job_id: str,
            started_at: datetime,
            finished_at: datetime,
            duration_seconds: float,
            success: bool,
            message: Optional[str] = None,
            error_trace: Optional[str] = None,
            result_data: Optional[dict] = None,
        ) -> None:
            """Callback untuk save job execution log ke database"""
            try:
                async with get_db_context() as db:
                    repo = JobExecutionRepository(db)
                    service = JobManagementService(repo)
                    await service.log_job_execution(
                        job_id=job_id,
                        started_at=started_at,
                        finished_at=finished_at,
                        duration_seconds=duration_seconds,
                        success=success,
                        message=message,
                        error_trace=error_trace,
                        result_data=result_data,
                    )
            except Exception as e:
                logger.error(f"Failed to log job execution: {e}")

        scheduler.set_log_callback(log_execution_callback)

        # Register semua jobs
        jobs_to_register = [
            AutoCreateDailyAttendanceJob(),
            MarkInvalidNoCheckoutJob(),
            ProcessAssignmentsJob(),
            CleanupTemporaryRolesJob(),
        ]

        scheduler.register_multiple(jobs_to_register)

        # Start scheduler
        scheduler.start()

        logger.info(
            f"Scheduler started successfully dengan {len(jobs_to_register)} jobs"
        )

        return scheduler

    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}", exc_info=True)
        raise


async def shutdown_scheduler():
    """
    Shutdown scheduler dengan graceful stop.
    Dipanggil pada FastAPI shutdown.
    """
    try:
        from app.core.scheduler.manager import get_scheduler

        scheduler = get_scheduler()
        if scheduler:
            logger.info("Shutting down scheduler...")
            scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown complete")
    except Exception as e:
        logger.error(f"Error during scheduler shutdown: {e}")
