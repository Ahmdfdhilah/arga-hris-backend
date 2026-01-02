"""Holiday Calendar Service - Facade untuk holiday operations."""

from typing import Optional, List, Tuple
from datetime import date
import uuid

from app.modules.holiday_calendar.repositories import HolidayQueries, HolidayCommands
from app.modules.holiday_calendar.use_cases import (
    CreateHolidayUseCase,
    UpdateHolidayUseCase,
    DeleteHolidayUseCase,
)
from app.modules.holiday_calendar.schemas import (
    CreateHolidayRequest,
    UpdateHolidayRequest,
    HolidayResponse,
    HolidayListItemResponse,
    IsHolidayResponse,
)
from app.core.exceptions import NotFoundException


class HolidayService:
    """Service facade untuk holiday calendar operations."""

    def __init__(self, queries: HolidayQueries, commands: HolidayCommands):
        self.queries = queries
        self.commands = commands

    async def create(
        self, request: CreateHolidayRequest, user_id: Optional[uuid.UUID] = None
    ) -> HolidayResponse:
        """Buat holiday baru."""
        use_case = CreateHolidayUseCase(self.queries, self.commands)
        holiday = await use_case.execute(
            holiday_date=request.date,
            name=request.name,
            description=request.description,
            created_by=user_id,
        )
        return HolidayResponse.model_validate(holiday)

    async def update(
        self,
        holiday_id: int,
        request: UpdateHolidayRequest,
        user_id: Optional[uuid.UUID] = None,
    ) -> HolidayResponse:
        """Update holiday."""
        use_case = UpdateHolidayUseCase(self.queries, self.commands)
        holiday = await use_case.execute(
            holiday_id=holiday_id,
            holiday_date=request.date,
            name=request.name,
            description=request.description,
            is_active=request.is_active,
            updated_by=user_id,
        )
        return HolidayResponse.model_validate(holiday)

    async def delete(self, holiday_id: int) -> None:
        """Hapus holiday."""
        use_case = DeleteHolidayUseCase(self.queries, self.commands)
        await use_case.execute(holiday_id)

    async def get_by_id(self, holiday_id: int) -> HolidayResponse:
        """Ambil holiday berdasarkan ID."""
        holiday = await self.queries.get_by_id(holiday_id)
        if not holiday:
            raise NotFoundException(f"Holiday dengan ID {holiday_id} tidak ditemukan")
        return HolidayResponse.model_validate(holiday)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        year: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[HolidayListItemResponse], int]:
        """List holidays dengan paginasi. Return tuple (items, total)."""
        skip = (page - 1) * page_size
        holidays = await self.queries.list(
            skip=skip, limit=page_size, year=year, is_active=is_active
        )
        total = await self.queries.count(year=year, is_active=is_active)
        items = [HolidayListItemResponse.model_validate(h) for h in holidays]
        return items, total

    async def check_is_holiday(self, target_date: date) -> IsHolidayResponse:
        """Cek apakah tanggal adalah hari libur."""
        holiday = await self.queries.get_by_date(target_date)
        return IsHolidayResponse(
            date=target_date,
            is_holiday=holiday is not None,
            holiday_name=holiday.name if holiday else None,
        )

    async def is_holiday(self, target_date: date) -> bool:
        """Cek apakah tanggal adalah hari libur (untuk internal use)."""
        return await self.queries.is_holiday(target_date)

