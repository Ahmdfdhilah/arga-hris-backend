"""
Router untuk job management API (admin only).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.core.security.rbac import require_permission
from app.modules.scheduled_jobs.repositories.job_execution_repository import (
    JobExecutionRepository,
)
from app.modules.scheduled_jobs.services.job_management_service import (
    JobManagementService,
)
from app.modules.scheduled_jobs.schemas.requests import JobTriggerRequest
from app.modules.scheduled_jobs.schemas.responses import (
    JobStatusResponse,
    JobExecutionResponse,
    JobTriggerResultResponse,
)
from app.core.schemas import CurrentUser, DataResponse, PaginatedResponse


router = APIRouter(prefix="/scheduled-jobs", tags=["Scheduled Jobs"])


def get_job_management_service(
    db: AsyncSession = Depends(get_db),
) -> JobManagementService:
    """Dependency injection untuk JobManagementService"""
    job_execution_repo = JobExecutionRepository(db)
    return JobManagementService(job_execution_repo)


@router.get(
    "/executions/recent", response_model=DataResponse[List[JobExecutionResponse]]
)
@require_permission("scheduled_job.read")
async def get_recent_executions(
    hours: int = Query(
        24, ge=1, le=168, description="Ambil logs dalam X jam terakhir (max 7 hari)"
    ),
    service: JobManagementService = Depends(get_job_management_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[JobExecutionResponse]]:
    """
    Get recent execution logs dari semua jobs.

    **Permission required:** scheduled_job.read
    """
    return await service.get_recent_executions(hours=hours)


@router.get("", response_model=DataResponse[List[JobStatusResponse]])
@require_permission("scheduled_job.read")
async def list_jobs(
    service: JobManagementService = Depends(get_job_management_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[JobStatusResponse]]:
    """
    List semua registered scheduled jobs dengan status.

    **Permission required:** scheduled_job.read
    """
    return await service.list_jobs()


@router.get("/{job_id}/history", response_model=PaginatedResponse[JobExecutionResponse])
@require_permission("scheduled_job.read")
async def get_job_execution_history(
    job_id: str,
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah items per halaman"),
    service: JobManagementService = Depends(get_job_management_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[JobExecutionResponse]:
    """
    Get execution history untuk suatu job.

    **Permission required:** scheduled_job.read
    """
    return await service.get_job_execution_history(
        job_id=job_id, page=page, limit=limit
    )


@router.get("/{job_id}", response_model=DataResponse[JobStatusResponse])
@require_permission("scheduled_job.read")
async def get_job_status(
    job_id: str,
    service: JobManagementService = Depends(get_job_management_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[JobStatusResponse]:
    """
    Get detail status suatu job.

    **Permission required:** scheduled_job.read
    """
    return await service.get_job_status(job_id)


@router.post("/{job_id}/trigger", response_model=DataResponse[JobTriggerResultResponse])
@require_permission("scheduled_job.execute")
async def trigger_job_manual(
    job_id: str,
    service: JobManagementService = Depends(get_job_management_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[JobTriggerResultResponse]:
    """
    Trigger job secara manual (untuk testing atau emergency).

    **Permission required:** scheduled_job.execute
    """
    return await service.trigger_job_manual(job_id)
