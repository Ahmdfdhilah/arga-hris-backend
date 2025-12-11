"""
Service untuk job management dan execution logging.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime

from app.modules.scheduled_jobs.repositories.job_execution_repository import JobExecutionRepository
from app.modules.scheduled_jobs.models.job_execution import JobExecution
from app.modules.scheduled_jobs.schemas.responses import (
    JobStatusResponse,
    JobExecutionResponse,
    JobTriggerResultResponse,
)
from app.core.scheduler.manager import get_scheduler
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.schemas import (
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)


class JobManagementService:
    """Service untuk managing scheduled jobs"""

    def __init__(self, job_execution_repo: JobExecutionRepository):
        self.job_execution_repo = job_execution_repo

    async def list_jobs(self) -> DataResponse[List[JobStatusResponse]]:
        """
        List semua registered jobs dengan status.

        Returns:
            DataResponse dengan list JobStatusResponse
        """
        scheduler = get_scheduler()
        if not scheduler:
            raise BadRequestException("Scheduler belum diinisialisasi")

        jobs = scheduler.list_jobs()

        jobs_data: List[JobStatusResponse] = [
            JobStatusResponse(**job) for job in jobs
        ]

        return create_success_response(
            message=f"Ditemukan {len(jobs_data)} scheduled jobs",
            data=jobs_data
        )

    async def get_job_status(self, job_id: str) -> DataResponse[JobStatusResponse]:
        """
        Get status detail suatu job.

        Args:
            job_id: ID job

        Returns:
            DataResponse dengan JobStatusResponse

        Raises:
            NotFoundException: Jika job tidak ditemukan
        """
        scheduler = get_scheduler()
        if not scheduler:
            raise BadRequestException("Scheduler belum diinisialisasi")

        job_status = scheduler.get_job_status(job_id)
        if not job_status:
            raise NotFoundException(f"Job dengan ID {job_id} tidak ditemukan")

        # Ambil execution history terakhir
        latest_execution = await self.job_execution_repo.get_latest_by_job_id(job_id)

        latest_execution_response = None
        if latest_execution:
            latest_execution_response = JobExecutionResponse.model_validate(
                latest_execution
            )

        response_data = JobStatusResponse(
            **job_status,
            latest_execution=latest_execution_response
        )

        return create_success_response(
            message="Detail job berhasil diambil",
            data=response_data
        )

    async def trigger_job_manual(
        self, job_id: str
    ) -> DataResponse[JobTriggerResultResponse]:
        """
        Trigger job secara manual.

        Args:
            job_id: ID job yang akan di-trigger

        Returns:
            DataResponse dengan JobTriggerResultResponse

        Raises:
            NotFoundException: Jika job tidak ditemukan
        """
        scheduler = get_scheduler()
        if not scheduler:
            raise BadRequestException("Scheduler belum diinisialisasi")

        # Cek apakah job ada
        if job_id not in scheduler.registered_jobs:
            raise NotFoundException(f"Job dengan ID {job_id} tidak ditemukan")

        # Execute job
        result = await scheduler.trigger_job_manual(job_id)

        response_data = JobTriggerResultResponse(
            job_id=job_id,
            success=result.get("success", False),
            result=result.get("data"),
        )

        return create_success_response(
            message=result.get("message", "Job berhasil dijalankan"),
            data=response_data
        )

    async def get_job_execution_history(
        self,
        job_id: str,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponse[JobExecutionResponse]:
        """
        Get execution history untuk suatu job.

        Args:
            job_id: ID job
            page: Nomor halaman
            limit: Jumlah items per halaman

        Returns:
            PaginatedResponse dengan list JobExecutionResponse
        """
        if page < 1:
            raise BadRequestException("Page harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        offset = (page - 1) * limit

        executions = await self.job_execution_repo.list_by_job_id(
            job_id=job_id,
            limit=limit,
            offset=offset
        )

        total_items = await self.job_execution_repo.count_by_job_id(job_id)

        executions_data: List[JobExecutionResponse] = [
            JobExecutionResponse.model_validate(execution)
            for execution in executions
        ]

        return create_paginated_response(
            message=f"History eksekusi job {job_id}",
            data=executions_data,
            page=page,
            limit=limit,
            total_items=total_items
        )

    async def get_recent_executions(
        self, hours: int = 24
    ) -> DataResponse[List[JobExecutionResponse]]:
        """
        Get recent execution logs dari semua jobs.

        Args:
            hours: Ambil logs dalam X jam terakhir

        Returns:
            DataResponse dengan list JobExecutionResponse
        """
        if hours < 1 or hours > 168:  # Max 7 hari
            raise BadRequestException("Hours harus antara 1 dan 168")

        executions = await self.job_execution_repo.list_recent(hours=hours)

        executions_data: List[JobExecutionResponse] = [
            JobExecutionResponse.model_validate(execution)
            for execution in executions
        ]

        return create_success_response(
            message=f"Ditemukan {len(executions_data)} eksekusi dalam {hours} jam terakhir",
            data=executions_data
        )

    async def log_job_execution(
        self,
        job_id: str,
        started_at: datetime,
        finished_at: datetime,
        duration_seconds: float,
        success: bool,
        message: Optional[str] = None,
        error_trace: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None
    ):
        """
        Save job execution log ke database.
        Dipanggil oleh scheduler manager via callback.
        
        Args:
            job_id: ID job
            started_at: Waktu mulai
            finished_at: Waktu selesai
            duration_seconds: Durasi eksekusi
            success: Status keberhasilan
            message: Pesan hasil
            error_trace: Stack trace jika error
            result_data: Data hasil eksekusi
        """
        log = JobExecution(
            job_id=job_id,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration_seconds,
            success=success,
            message=message,
            error_trace=error_trace,
            result_data=result_data,
        )
        
        await self.job_execution_repo.create(log)
