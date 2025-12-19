"""
Employee Assignments Router - API Endpoints
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query

from app.modules.employee_assignments.dependencies import AssignmentServiceDep
from app.modules.employee_assignments.schemas.requests import (
    AssignmentCreateRequest,
    AssignmentCancelRequest,
)
from app.modules.employee_assignments.schemas.responses import (
    AssignmentResponse,
    AssignmentListItemResponse,
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

router = APIRouter(prefix="/assignments", tags=["Employee Assignments"])


@router.post("/", status_code=201, response_model=DataResponse[AssignmentResponse])
@require_permission("assignment.create")
async def create_assignment(
    request: AssignmentCreateRequest,
    service: AssignmentServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AssignmentResponse]:
    """
    Membuat assignment penggantian sementara.

    **Permission required**: assignment.create
    """
    result = await service.create(request=request, created_by=current_user.id)
    return create_success_response(
        message="Assignment berhasil dibuat",
        data=result,
    )


@router.get("/", response_model=PaginatedResponse[AssignmentListItemResponse])
@require_permission("assignment.read")
async def list_assignments(
    service: AssignmentServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    status: Optional[str] = Query(
        None, description="Filter status (pending/active/expired/cancelled)"
    ),
    employee_id: Optional[int] = Query(
        None, description="Filter berdasarkan employee yang menggantikan"
    ),
    replaced_employee_id: Optional[int] = Query(
        None, description="Filter berdasarkan employee yang digantikan"
    ),
    org_unit_id: Optional[int] = Query(None, description="Filter berdasarkan org unit"),
    start_date_from: Optional[date] = Query(
        None, description="Filter start_date dari tanggal"
    ),
    start_date_to: Optional[date] = Query(
        None, description="Filter start_date sampai tanggal"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah item per halaman"),
) -> PaginatedResponse[AssignmentListItemResponse]:
    """
    Daftar semua assignment dengan filters.

    **Permission required**: assignment.read
    """
    items, total_items = await service.list(
        status=status,
        employee_id=employee_id,
        replaced_employee_id=replaced_employee_id,
        org_unit_id=org_unit_id,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        page=page,
        limit=limit,
    )

    return create_paginated_response(
        message="Daftar assignment berhasil diambil",
        data=items,
        page=page,
        limit=limit,
        total_items=total_items,
    )


@router.get("/{assignment_id}", response_model=DataResponse[AssignmentResponse])
@require_permission("assignment.read")
async def get_assignment(
    assignment_id: int,
    service: AssignmentServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AssignmentResponse]:
    """
    Ambil detail assignment berdasarkan ID.

    **Permission required**: assignment.read
    """
    result = await service.get_by_id(assignment_id)
    return create_success_response(
        message="Data assignment berhasil diambil",
        data=result,
    )


@router.post("/{assignment_id}/cancel", response_model=DataResponse[AssignmentResponse])
@require_permission("assignment.cancel")
async def cancel_assignment(
    assignment_id: int,
    service: AssignmentServiceDep,
    request: Optional[AssignmentCancelRequest] = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AssignmentResponse]:
    """
    Batalkan assignment yang masih pending atau active.

    **Permission required**: assignment.cancel
    """
    result = await service.cancel(
        assignment_id=assignment_id,
        request=request,
        updated_by=current_user.id,
    )
    return create_success_response(
        message="Assignment berhasil dibatalkan",
        data=result,
    )
