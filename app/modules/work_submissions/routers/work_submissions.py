from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from app.modules.work_submissions.dependencies import WorkSubmissionServiceDep
from app.modules.work_submissions.schemas.requests import (
    WorkSubmissionCreateRequest,
    WorkSubmissionUpdateRequest,
)
from app.modules.work_submissions.schemas.responses import (
    WorkSubmissionResponse,
    WorkSubmissionListResponse,
)
from app.core.dependencies.auth import get_current_user
from app.core.security.rbac import require_permission
from app.core.schemas import (
    CurrentUser,
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)
from app.core.exceptions import UnprocessableEntityException


router = APIRouter(prefix="/work-submissions", tags=["Work Submissions"])


@router.get("/my-submissions", response_model=PaginatedResponse[WorkSubmissionResponse])
@require_permission("work_submission.read_own")
async def get_my_submissions(
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    submission_month: Optional[date] = Query(
        None, description="Filter berdasarkan bulan submission"
    ),
    status: Optional[str] = Query(
        None, description="Filter berdasarkan status (draft/submitted)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[WorkSubmissionResponse]:
    """
    Ambil daftar work submissions employee sendiri.
    Employee hanya bisa melihat submission miliknya sendiri.

    **Permission required**: work_submission.read_own
    """

    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    items, total = await service.get_my_submissions(
        employee_id=current_user.employee_id,
        submission_month=submission_month,
        status=status,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=page,
        limit=limit,
        total_items=total,
    )


@router.post("/", status_code=201, response_model=DataResponse[WorkSubmissionResponse])
@require_permission("work_submission.create")
async def create_submission(
    request: WorkSubmissionCreateRequest,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[WorkSubmissionResponse]:
    """
    Membuat work submission baru.

    **Note**: Files diupload terpisah menggunakan endpoint upload files.

    **Permission required**: work_submission.create
    """
    data = await service.create_submission(
        request=request,
        created_by_user_id=current_user.id,
    )
    return create_success_response(message="Created", data=data)


@router.get("/", response_model=PaginatedResponse[WorkSubmissionListResponse])
@require_permission("work_submission.read_all")
async def list_all_submissions(
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    employee_id: Optional[int] = Query(
        None, description="Filter berdasarkan employee ID"
    ),
    submission_month: Optional[date] = Query(
        None, description="Filter berdasarkan bulan submission"
    ),
    status: Optional[str] = Query(
        None, description="Filter berdasarkan status (draft/submitted)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[WorkSubmissionListResponse]:
    """
    Ambil daftar semua work submissions (HR Admin/Super Admin only).

    **Permission required**: work_submission.read_all
    """
    items, total = await service.list_all_submissions(
        employee_id=employee_id,
        submission_month=submission_month,
        status=status,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=page,
        limit=limit,
        total_items=total,
    )


@router.get("/{submission_id}", response_model=DataResponse[WorkSubmissionResponse])
@require_permission("work_submission.read")
async def get_submission(
    submission_id: int,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[WorkSubmissionResponse]:
    """
    Ambil detail work submission berdasarkan ID.

    **Permission required**: work_submission.read
    """
    data = await service.get_submission_by_id(submission_id)
    return create_success_response(message="Success", data=data)


@router.put("/{submission_id}", response_model=DataResponse[WorkSubmissionResponse])
@require_permission("work_submission.update")
async def update_submission(
    submission_id: int,
    request: WorkSubmissionUpdateRequest,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[WorkSubmissionResponse]:
    """
    Update work submission.

    **Permission required**: work_submission.update
    """
    data = await service.update_submission(
        submission_id=submission_id,
        request=request,
    )
    return create_success_response(message="Updated", data=data)


@router.delete("/{submission_id}", response_model=DataResponse[None])
@require_permission("work_submission.delete")
async def delete_submission(
    submission_id: int,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[None]:
    """
    Hapus work submission beserta semua files-nya.

    **Permission required**: work_submission.delete
    """
    await service.delete_submission(submission_id)
    return create_success_response(message="Deleted", data=None)


@router.post(
    "/{submission_id}/upload-files", response_model=DataResponse[WorkSubmissionResponse]
)
@require_permission("work_submission.upload_file")
async def upload_files(
    submission_id: int,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    files: List[UploadFile] = File(
        ..., description="Files untuk diupload (max 10 files)"
    ),
) -> DataResponse[WorkSubmissionResponse]:
    """
    Upload files ke work submission.

    **Supported file types**: PDF, Word, Excel, PowerPoint, Images (PNG, JPG), ZIP
    **Max file size**: 10 MB per file
    **Max files**: 10 files per submission

    **Permission required**: work_submission.upload_files
    """
    data = await service.upload_files(
        submission_id=submission_id,
        files=files,
    )
    return create_success_response(message="Files uploaded", data=data)


@router.delete(
    "/{submission_id}/files", response_model=DataResponse[WorkSubmissionResponse]
)
@require_permission("work_submission.delete_file")
async def delete_file(
    submission_id: int,
    service: WorkSubmissionServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    file_path: str = Body(..., embed=True, description="File path yang akan dihapus"),
) -> DataResponse[WorkSubmissionResponse]:
    """
    Hapus single file dari work submission.

    **Permission required**: work_submission.delete_file
    """
    data = await service.delete_file(
        submission_id=submission_id,
        file_path=file_path,
    )
    return create_success_response(message="File deleted", data=data)
