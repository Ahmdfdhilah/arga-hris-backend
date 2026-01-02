"""Use case untuk update holiday."""

from datetime import date
from typing import Optional
import uuid

from app.modules.holiday_calendar.repositories import HolidayQueries, HolidayCommands
from app.modules.holiday_calendar.models import Holiday
from app.core.exceptions import NotFoundException, ConflictException


class UpdateHolidayUseCase:
    """Use case untuk update holiday."""

    def __init__(self, queries: HolidayQueries, commands: HolidayCommands):
        self.queries = queries
        self.commands = commands

    async def execute(
        self,
        holiday_id: int,
        holiday_date: Optional[date] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[uuid.UUID] = None,
    ) -> Holiday:
        """Update holiday.
        
        Args:
            holiday_id: ID holiday yang akan diupdate
            holiday_date: Tanggal libur baru (opsional)
            name: Nama baru (opsional)
            description: Deskripsi baru (opsional)
            is_active: Status aktif baru (opsional)
            updated_by: UUID user yang mengupdate
            
        Returns:
            Holiday yang sudah diupdate
            
        Raises:
            NotFoundException: Jika holiday tidak ditemukan
            ConflictException: Jika tanggal baru sudah ada
        """
        holiday = await self.queries.get_by_id(holiday_id)
        if not holiday:
            raise NotFoundException(f"Holiday dengan ID {holiday_id} tidak ditemukan")

        # Jika tanggal berubah, cek apakah tanggal baru sudah ada
        if holiday_date and holiday_date != holiday.date:
            existing = await self.queries.get_by_date(holiday_date)
            if existing:
                raise ConflictException(f"Hari libur untuk tanggal {holiday_date} sudah terdaftar")
            holiday.date = holiday_date

        if name is not None:
            holiday.name = name
        if description is not None:
            holiday.description = description
        if is_active is not None:
            holiday.is_active = is_active
        if updated_by is not None:
            holiday.updated_by = updated_by

        return await self.commands.update(holiday)
