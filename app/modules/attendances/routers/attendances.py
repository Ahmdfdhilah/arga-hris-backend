from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, Query
from app.modules.attendances.dependencies import AttendanceServiceDep
from app.modules.attendances.schemas.requests import (
    CheckInRequest,
    CheckOutRequest,
    BulkMarkPresentRequest,
    MarkPresentByIdRequest,
)
from app.modules.attendances.schemas.responses import (
    AttendanceResponse,
    AttendanceListResponse,
    EmployeeAttendanceReport,
    EmployeeAttendanceOverview,
    BulkMarkPresentSummary,
    AttendanceStatusCheckResponse,
)
from app.core.dependencies.auth import get_current_user
from app.core.security.rbac import require_permission, require_role
from app.core.schemas import (
    CurrentUser,
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)
from app.core.exceptions import UnprocessableEntityException

router = APIRouter()


@router.post("/check-in", response_model=DataResponse[AttendanceResponse])
@require_permission("attendance.create")
async def check_in(
    request_obj: Request,
    service: AttendanceServiceDep,
    selfie: UploadFile = File(..., description="Foto selfie check-in (WAJIB)"),
    notes: Optional[str] = Form(None),
    latitude: Optional[float] = Form(
        None, ge=-90, le=90, description="Latitude koordinat lokasi"
    ),
    longitude: Optional[float] = Form(
        None, ge=-180, le=180, description="Longitude koordinat lokasi"
    ),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AttendanceResponse]:
    """
    Check-in attendance untuk employee.

    **PENTING**: Foto selfie WAJIB diisi untuk check-in.
    **Permission required**: attendance.create
    """
    check_in_request = CheckInRequest(
        notes=notes, latitude=latitude, longitude=longitude
    )
    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    data = await service.check_in(
        employee_id=current_user.employee_id,
        request=check_in_request,
        request_obj=request_obj,
        selfie=selfie,
    )
    return create_success_response(message="Check-in berhasil", data=data)


@router.post("/check-out", response_model=DataResponse[AttendanceResponse])
@require_permission("attendance.create")
async def check_out(
    request_obj: Request,
    service: AttendanceServiceDep,
    selfie: UploadFile = File(..., description="Foto selfie check-out (WAJIB)"),
    notes: Optional[str] = Form(None),
    latitude: Optional[float] = Form(
        None, ge=-90, le=90, description="Latitude koordinat lokasi"
    ),
    longitude: Optional[float] = Form(
        None, ge=-180, le=180, description="Longitude koordinat lokasi"
    ),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AttendanceResponse]:
    """
    Check-out attendance untuk employee.

    **PENTING**: Foto selfie WAJIB diisi untuk check-out.
    **Permission required**: attendance.create
    """
    check_out_request = CheckOutRequest(
        notes=notes, latitude=latitude, longitude=longitude
    )
    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    data, message = await service.check_out(
        employee_id=current_user.employee_id,
        request=check_out_request,
        request_obj=request_obj,
        selfie=selfie,
    )
    return create_success_response(message=message, data=data)


@router.get("/reports", response_model=DataResponse[list[EmployeeAttendanceReport]])
@require_role(["hr_admin", "super_admin"])
async def get_attendance_report(
    service: AttendanceServiceDep,
    org_unit_id: int = Query(..., gt=0, description="ID org unit (WAJIB)"),
    start_date: date = Query(..., description="Tanggal mulai (WAJIB)"),
    end_date: date = Query(..., description="Tanggal akhir (WAJIB)"),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[list[EmployeeAttendanceReport]]:
    """
    Ambil attendance report untuk org unit tertentu dalam date range.

    Return list employees dengan attendance mereka untuk keperluan export Excel.
    Tidak ada paginasi, semua data akan dikembalikan.

    **Role required**: hr_admin, super_admin
    """
    data = await service.get_attendance_report(
        org_unit_id=org_unit_id,
        start_date=start_date,
        end_date=end_date,
    )
    return create_success_response(
        message=f"Attendance report berhasil diambil untuk {len(data)} employees",
        data=data,
    )


@router.get("/overview", response_model=PaginatedResponse[EmployeeAttendanceOverview])
@require_role(["hr_admin", "super_admin"])
async def get_attendance_overview(
    service: AttendanceServiceDep,
    start_date: date = Query(..., description="Tanggal mulai (WAJIB)"),
    end_date: date = Query(..., description="Tanggal akhir (WAJIB)"),
    org_unit_id: Optional[int] = Query(
        None,
        gt=0,
        description="ID org unit (opsional, jika tidak diisi maka akan mengambil semua employees)",
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[EmployeeAttendanceOverview]:
    """
    Ambil attendance overview per employee dengan paginasi.

    Return summary kehadiran (total present, absent, leave) per employee.
    Dengan paginasi untuk ditampilkan di table.

    Jika org_unit_id tidak diisi, maka akan mengambil semua employees dari seluruh org unit.

    **Role required**: hr_admin, super_admin
    """
    items, pagination = await service.get_attendance_overview(
        org_unit_id=org_unit_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Attendance overview berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/check-attendance-status",
    response_model=DataResponse[AttendanceStatusCheckResponse],
)
@require_permission("attendance.read_own")
async def check_attendance_status(
    service: AttendanceServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AttendanceStatusCheckResponse]:
    """
    Check apakah user bisa absen hari ini (check status cuti dan hari kerja).

    Returns:
        - can_attend: boolean
        - reason: string (alasan jika tidak bisa absen)
        - is_on_leave: boolean
        - is_working_day: boolean
        - leave_details: dict (detail cuti jika sedang cuti)

    **Permission required**: attendance.read_own
    """
    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    data = await service.check_attendance_status(
        employee_id=current_user.employee_id
    )
    return create_success_response(
        message="Status attendance berhasil diambil", data=data
    )


@router.get("/my-attendance", response_model=PaginatedResponse[AttendanceListResponse])
@require_permission("attendance.read_own")
async def get_my_attendance(
    service: AttendanceServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    type: Optional[str] = Query(
        None,
        description="Tipe periode (today/weekly/monthly). Jika diisi, start_date dan end_date diabaikan",
    ),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[AttendanceListResponse]:
    """
    Ambil attendance history employee sendiri.
    Jika parameter type diisi, maka start_date dan end_date akan diabaikan.

    **Permission required**: attendance.read_own
    """

    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    items, pagination = await service.get_my_attendance(
        employee_id=current_user.employee_id,
        type=type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar attendance berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/team", response_model=PaginatedResponse[AttendanceListResponse])
@require_permission("attendance.read_team")
async def get_team_attendance(
    service: AttendanceServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    status: Optional[str] = Query(
        None, description="Filter status (present/absent/leave)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[AttendanceListResponse]:
    """Ambil attendance team/subordinates (untuk org unit head)."""

    if current_user.employee_id is None:
        raise UnprocessableEntityException("employee id tidak valid")

    items, pagination = await service.get_team_attendance(
        employee_id=current_user.employee_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar attendance team berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/", response_model=PaginatedResponse[AttendanceListResponse])
@require_role(["hr_admin", "super_admin"])
async def get_all_attendances(
    service: AttendanceServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    type: Optional[str] = Query(
        None,
        description="Tipe periode (today/weekly/monthly). Jika diisi, start_date dan end_date diabaikan",
    ),
    start_date: Optional[date] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[date] = Query(None, description="Tanggal akhir filter"),
    org_unit_id: Optional[int] = Query(None, description="Filter berdasarkan org unit"),
    employee_id: Optional[int] = Query(
        None, description="Filter berdasarkan employee ID tertentu"
    ),
    status: Optional[str] = Query(
        None, description="Filter status (present/absent/leave)"
    ),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=250, description="Jumlah item per halaman"),
) -> PaginatedResponse[AttendanceListResponse]:
    """
    Ambil semua attendance dengan berbagai filter (admin/super admin only).
    Jika parameter type diisi, maka start_date dan end_date akan diabaikan.
    """
    items, pagination = await service.get_all_attendances(
        type=type,
        start_date=start_date,
        end_date=end_date,
        org_unit_id=org_unit_id,
        employee_id=employee_id,
        status=status,
        page=page,
        limit=limit,
    )
    return create_paginated_response(
        message="Daftar semua attendance berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/{attendance_id}", response_model=DataResponse[AttendanceResponse])
@require_permission("attendance.read")
async def get_attendance(
    service: AttendanceServiceDep,
    attendance_id: int,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AttendanceResponse]:
    """Ambil attendance berdasarkan ID."""
    data = await service.get_attendance_by_id(attendance_id)
    return create_success_response(message="Attendance berhasil diambil", data=data)


@router.post("/bulk-mark-present", response_model=DataResponse[BulkMarkPresentSummary])
@require_role(["hr_admin", "super_admin"])
async def bulk_mark_present(
    service: AttendanceServiceDep,
    request: BulkMarkPresentRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BulkMarkPresentSummary]:
    """
    Bulk mark present untuk semua employees dengan role 'employee' pada tanggal tertentu.

    Use case: Libur nasional, libur mendadak, atau event khusus.

    Logic:
    - Membuat atau update attendance untuk semua users yang memiliki role 'employee' dan employee_id
    - Status: present
    - Jika attendance sudah ada pada tanggal tersebut, akan diupdate statusnya dan notes
    - Jika belum ada, akan dibuat attendance baru
    """
    data = await service.bulk_mark_present(
        request=request,
        created_by=current_user.employee_id or current_user.id,
    )
    return create_success_response(
        message=f"Bulk mark present berhasil. {data.created} attendance dibuat, {data.updated} attendance diupdate.",
        data=data,
    )


@router.patch("/{attendance_id}/mark-present", response_model=DataResponse[AttendanceResponse])
@require_permission("attendance.update")
async def mark_present_by_id(
    service: AttendanceServiceDep,
    attendance_id: int,
    request: MarkPresentByIdRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[AttendanceResponse]:
    """
    Mark attendance sebagai present berdasarkan ID (untuk admin/super admin).

    Use case: Super admin dan HRIS admin ingin mengubah status attendance karyawan tertentu.

    Restrictions:
    - User tidak dapat mengubah attendance mereka sendiri (bahkan jika super admin)
    - Memerlukan permission 'attendance.update'

    Logic:
    - Update attendance yang sudah ada menjadi status 'present'
    - Isi check_in_time (09:00) dan check_out_time (17:00) dari attendance_date
    - Hitung work_hours otomatis (8 jam standar)
    - Tambahkan keterangan otomatis: "Diubah oleh [nama admin] pada [tanggal waktu]"

    **Permission required**: attendance.update
    """
    current_employee_id = current_user.employee_id or current_user.id

    data = await service.mark_present_by_id(
        attendance_id=attendance_id,
        current_user_employee_id=current_employee_id,
        admin_name=current_user.full_name,
        notes=request.notes,
    )
    return create_success_response(
        message="Attendance berhasil diupdate menjadi present",
        data=data,
    )
