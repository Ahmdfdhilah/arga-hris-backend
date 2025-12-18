from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from app.modules.leave_requests.dependencies import LeaveRequestServiceDep
from app.modules.leave_requests.schemas.requests import (
    LeaveRequestCreateRequest,
    LeaveRequestUpdateRequest,
)
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    LeaveRequestListResponse,
)
from app.core.dependencies.auth import get_current_user
from app.core.security.rbac import require_permission
from app.core.schemas import (
    CurrentUser,
    DataResponse,
    PaginatedResponse,
    create_paginated_response,
)
from app.core.exceptions import UnprocessableEntityException

router = APIRouter(prefix="/leave-requests", tags=["Leave Requests"])


@router.get(
    "/my-leave-requests", response_model=PaginatedResponse[LeaveRequestResponse]
)
@require_permission("leave_request.read_own")
async def get_my_leave_requests(
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    leave_type: Optional[str] = Query(
        None, description="Filter jenis cuti (leave/holiday)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[LeaveRequestResponse]:
    """
    Ambil daftar leave requests employee sendiri.
    Employee hanya bisa melihat leave request miliknya sendiri.

    **Permission required**: leave_request.read_own
    """
    items, total_items = await service.get_my_leave_requests(
        employee_id=current_user.employee_id or 0,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar leave request berhasil diambil",
        data=items,
        page=page,
        limit=limit,
        total_items=total_items,
    )


@router.post("/", status_code=201, response_model=DataResponse[LeaveRequestResponse])
@require_permission("leave_request.create")
async def create_leave_request(
    request: LeaveRequestCreateRequest,
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[LeaveRequestResponse]:
    """
    Membuat leave request baru (HR Admin/Super Admin only).

    **Permission required**: leave_request.create
    """
    return await service.create_leave_request(
        request=request,
        created_by_user_id=current_user.id,
    )


@router.get("/", response_model=PaginatedResponse[LeaveRequestListResponse])
@require_permission("leave_request.read_all")
async def list_all_leave_requests(
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    employee_id: Optional[int] = Query(
        None, description="Filter berdasarkan employee ID"
    ),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    leave_type: Optional[str] = Query(
        None, description="Filter jenis cuti (leave/holiday)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[LeaveRequestListResponse]:
    """
    Ambil daftar semua leave requests (HR Admin/Super Admin only).

    **Permission required**: leave_request.read_all
    """
    items, total_items = await service.list_all_leave_requests(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar leave request berhasil diambil",
        data=items,
        page=page,
        limit=limit,
        total_items=total_items,
    )


@router.get("/{leave_request_id}", response_model=DataResponse[LeaveRequestResponse])
@require_permission("leave_request.read")
async def get_leave_request(
    leave_request_id: int,
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[LeaveRequestResponse]:
    """
    Ambil detail leave request berdasarkan ID (HR Admin/Super Admin only).

    **Permission required**: leave_request.read
    """
    return await service.get_leave_request_by_id(leave_request_id)


@router.put("/{leave_request_id}", response_model=DataResponse[LeaveRequestResponse])
@require_permission("leave_request.update")
async def update_leave_request(
    leave_request_id: int,
    request: LeaveRequestUpdateRequest,
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[LeaveRequestResponse]:
    """
    Update leave request (HR Admin/Super Admin only).

    **Permission required**: leave_request.update
    """
    return await service.update_leave_request(
        leave_request_id=leave_request_id,
        request=request,
    )


@router.delete("/{leave_request_id}", response_model=DataResponse[None])
@require_permission("leave_request.delete")
async def delete_leave_request(
    leave_request_id: int,
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[None]:
    """
    Hapus leave request (HR Admin/Super Admin only).

    **Permission required**: leave_request.delete
    """
    return await service.delete_leave_request(leave_request_id)


@router.get(
    "/team/leave-requests", response_model=PaginatedResponse[LeaveRequestListResponse]
)
@require_permission("leave_request.read_team")
async def get_team_leave_requests(
    service: LeaveRequestServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    leave_type: Optional[str] = Query(
        None, description="Filter jenis cuti (leave/holiday)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[LeaveRequestListResponse]:
    """
    Ambil leave requests team/subordinates (untuk org unit head).
    Menampilkan leave requests dari semua subordinates (recursive).

    **Permission required**: leave_request.read_team
    """
    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    items, total_items = await service.get_team_leave_requests(
        employee_id=current_user.employee_id,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar leave request berhasil diambil",
        data=items,
        page=page,
        limit=limit,
        total_items=total_items,
    )
