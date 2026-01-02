"""Router untuk Holiday Calendar endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.modules.holiday_calendar.dependencies import get_holiday_service
from app.modules.holiday_calendar.services import HolidayService
from app.modules.holiday_calendar.schemas import (
    CreateHolidayRequest,
    UpdateHolidayRequest,
    HolidayResponse,
    HolidayListItemResponse,
    IsHolidayResponse,
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

router = APIRouter(prefix="/holidays", tags=["Holidays"])


@router.get("/check", response_model=DataResponse[IsHolidayResponse])
async def check_is_holiday(
    target_date: date = Query(..., description="Tanggal yang ingin dicek"),
    service: HolidayService = Depends(get_holiday_service),
) -> DataResponse[IsHolidayResponse]:
    """
    Cek apakah suatu tanggal adalah hari libur.
    
    Endpoint publik untuk pengecekan hari libur.
    """
    result = await service.check_is_holiday(target_date)
    return create_success_response(
        message="Pengecekan hari libur berhasil",
        data=result,
    )


@router.get("/", response_model=PaginatedResponse[HolidayListItemResponse])
@require_permission("holiday:read")
async def list_holidays(
    service: HolidayService = Depends(get_holiday_service),
    current_user: CurrentUser = Depends(get_current_user),
    year: Optional[int] = Query(None, description="Filter berdasarkan tahun"),
    is_active: Optional[bool] = Query(None, description="Filter status aktif"),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah item per halaman"),
) -> PaginatedResponse[HolidayListItemResponse]:
    """
    Ambil daftar hari libur.
    
    **Permission required**: holiday:read
    """
    items, total = await service.list(page=page, page_size=limit, year=year, is_active=is_active)
    return create_paginated_response(
        message="Daftar hari libur berhasil diambil",
        data=items,
        page=page,
        limit=limit,
        total_items=total,
    )


@router.post("/", status_code=201, response_model=DataResponse[HolidayResponse])
@require_permission("holiday:write")
async def create_holiday(
    request: CreateHolidayRequest,
    service: HolidayService = Depends(get_holiday_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[HolidayResponse]:
    """
    Tambah hari libur baru.
    
    **Permission required**: holiday:write
    """
    result = await service.create(request, user_id=current_user.id)
    return create_success_response(
        message="Hari libur berhasil ditambahkan",
        data=result,
    )


@router.get("/{holiday_id}", response_model=DataResponse[HolidayResponse])
@require_permission("holiday:read")
async def get_holiday(
    holiday_id: int,
    service: HolidayService = Depends(get_holiday_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[HolidayResponse]:
    """
    Ambil detail hari libur.
    
    **Permission required**: holiday:read
    """
    result = await service.get_by_id(holiday_id)
    return create_success_response(
        message="Detail hari libur berhasil diambil",
        data=result,
    )


@router.patch("/{holiday_id}", response_model=DataResponse[HolidayResponse])
@require_permission("holiday:write")
async def update_holiday(
    holiday_id: int,
    request: UpdateHolidayRequest,
    service: HolidayService = Depends(get_holiday_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[HolidayResponse]:
    """
    Update hari libur.
    
    **Permission required**: holiday:write
    """
    result = await service.update(holiday_id, request, user_id=current_user.id)
    return create_success_response(
        message="Hari libur berhasil diupdate",
        data=result,
    )


@router.delete("/{holiday_id}", response_model=DataResponse[None])
@require_permission("holiday:delete")
async def delete_holiday(
    holiday_id: int,
    service: HolidayService = Depends(get_holiday_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[None]:
    """
    Hapus hari libur.
    
    **Permission required**: holiday:delete
    """
    await service.delete(holiday_id)
    return create_success_response(
        message="Hari libur berhasil dihapus",
        data=None,
    )

