"""Use case untuk membuat holiday baru."""

from datetime import date
from typing import Optional
import uuid

from app.modules.holiday_calendar.repositories import HolidayQueries, HolidayCommands
from app.modules.holiday_calendar.models import Holiday
from app.core.exceptions import ConflictException


class CreateHolidayUseCase:
    """Use case untuk membuat holiday baru."""

    def __init__(self, queries: HolidayQueries, commands: HolidayCommands):
        self.queries = queries
        self.commands = commands

    async def execute(
        self,
        holiday_date: date,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[uuid.UUID] = None,
    ) -> Holiday:
        """Buat holiday baru.
        
        Args:
            holiday_date: Tanggal libur
            name: Nama hari libur
            description: Deskripsi opsional
            created_by: UUID user yang membuat
            
        Returns:
            Holiday yang baru dibuat
            
        Raises:
            ConflictException: Jika tanggal sudah ada
        """
        # Cek apakah tanggal sudah ada
        existing = await self.queries.get_by_date(holiday_date)
        if existing:
            raise ConflictException(f"Hari libur untuk tanggal {holiday_date} sudah terdaftar")

        data = {
            "date": holiday_date,
            "name": name,
            "description": description,
            "is_active": True,
            "created_by": created_by,
        }

        return await self.commands.create(data)
