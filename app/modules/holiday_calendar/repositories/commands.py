"""Repository commands untuk Holiday - Write operations."""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.holiday_calendar.models.holiday import Holiday


class HolidayCommands:
    """Write operations untuk Holiday."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Holiday:
        """Buat holiday baru."""
        holiday = Holiday(**data)
        self.db.add(holiday)
        await self.db.commit()
        await self.db.refresh(holiday)
        return holiday

    async def update(self, holiday: Holiday) -> Holiday:
        """Update holiday yang sudah ada."""
        await self.db.commit()
        await self.db.refresh(holiday)
        return holiday

    async def delete(self, holiday: Holiday) -> None:
        """Hard delete holiday."""
        await self.db.delete(holiday)
        await self.db.commit()
