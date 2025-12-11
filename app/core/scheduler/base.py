"""
Base class untuk semua scheduled jobs.
Menyediakan interface generic dan logging otomatis.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class BaseScheduledJob(ABC):
    """
    Abstract base class untuk scheduled jobs.
    
    Attributes:
        job_id: Unique identifier untuk job
        description: Deskripsi job dalam Bahasa Indonesia
        cron: Cron expression (jika None, gunakan interval)
        interval_seconds: Interval dalam detik (jika cron None)
        enabled: Status aktif job (default True)
        max_retries: Maksimal retry jika gagal (default 3)
        retry_delay_seconds: Delay antar retry dalam detik (default 60)
    """

    job_id: str
    description: str
    cron: Optional[str] = None
    interval_seconds: Optional[int] = None
    enabled: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 60

    def __init__(self):
        if not hasattr(self, "job_id"):
            raise ValueError("Job harus memiliki job_id")
        if not hasattr(self, "description"):
            raise ValueError("Job harus memiliki description")
        if not self.cron and not self.interval_seconds:
            raise ValueError("Job harus memiliki cron atau interval_seconds")

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Method utama yang akan dijalankan oleh scheduler.
        
        Returns:
            Dict dengan keys:
                - success: bool
                - message: str
                - data: Optional[Any]
        
        Raises:
            Exception: Jika terjadi error dalam eksekusi
        """
        pass

    async def run_with_logging(
        self,
        log_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Wrapper untuk execute dengan logging dan error handling.
        
        Args:
            log_callback: Optional callback untuk save execution log ke database
            
        Returns:
            Dict hasil eksekusi
        """
        start_time = datetime.now()
        result = {
            "success": False,
            "message": "Job gagal dijalankan",
            "data": None,
            "error": None,
        }

        try:
            logger.info(f"Memulai job: {self.job_id} - {self.description}")
            
            execution_result = await self.execute()
            
            result.update(execution_result)
            result["success"] = True
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Job {self.job_id} selesai dalam {duration:.2f} detik. "
                f"Result: {result.get('message', 'Success')}"
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_trace = traceback.format_exc()
            
            result["success"] = False
            result["message"] = f"Job gagal: {str(e)}"
            result["error"] = error_trace
            
            logger.error(
                f"Job {self.job_id} gagal setelah {duration:.2f} detik. "
                f"Error: {str(e)}\n{error_trace}"
            )

        # Save log ke database jika callback disediakan
        if log_callback:
            try:
                await log_callback(
                    job_id=self.job_id,
                    started_at=start_time,
                    finished_at=end_time,
                    duration_seconds=duration,
                    success=result["success"],
                    message=result["message"],
                    error_trace=result.get("error"),
                    result_data=result.get("data"),
                )
            except Exception as log_error:
                logger.error(f"Gagal save job execution log: {log_error}")

        return result

    def get_schedule_config(self) -> Dict[str, Any]:
        """
        Get configuration untuk APScheduler.
        
        Returns:
            Dict dengan trigger configuration
        """
        if self.cron:
            from apscheduler.triggers.cron import CronTrigger
            # Parse cron expression
            parts = self.cron.split()
            if len(parts) != 5:
                raise ValueError(
                    f"Invalid cron expression: {self.cron}. "
                    "Format: minute hour day month day_of_week"
                )
            
            return {
                "trigger": CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                ),
                "id": self.job_id,
                "name": self.description,
                "replace_existing": True,
            }
        else:
            from apscheduler.triggers.interval import IntervalTrigger

            # interval_seconds is guaranteed to be not None due to __init__ validation
            assert self.interval_seconds is not None, "interval_seconds must be set when cron is not used"

            return {
                "trigger": IntervalTrigger(seconds=self.interval_seconds),
                "id": self.job_id,
                "name": self.description,
                "replace_existing": True,
            }
