"""Repository queries untuk Holiday - Read operations."""

from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.holiday_calendar.models.holiday import Holiday


class HolidayQueries:
    """Read operations untuk Holiday."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, holiday_id: int) -> Optional[Holiday]:
        """Ambil holiday berdasarkan ID."""
        result = await self.db.execute(
            select(Holiday).where(Holiday.id == holiday_id)
        )
        return result.scalar_one_or_none()

    async def get_by_date(self, target_date: date) -> Optional[Holiday]:
        """Ambil holiday berdasarkan tanggal."""
        result = await self.db.execute(
            select(Holiday).where(
                and_(Holiday.date == target_date, Holiday.is_active == True)
            )
        )
        return result.scalar_one_or_none()

    async def is_holiday(self, target_date: date) -> bool:
        """Cek apakah tanggal adalah hari libur."""
        result = await self.db.execute(
            select(Holiday.id).where(
                and_(Holiday.date == target_date, Holiday.is_active == True)
            )
        )
        return result.scalar_one_or_none() is not None

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        year: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[Holiday]:
        """List holidays dengan filter opsional."""
        query = select(Holiday)

        conditions = []
        if year is not None:
            conditions.append(func.extract("year", Holiday.date) == year)
        if is_active is not None:
            conditions.append(Holiday.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Holiday.date.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        year: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Hitung total holidays dengan filter opsional."""
        query = select(func.count(Holiday.id))

        conditions = []
        if year is not None:
            conditions.append(func.extract("year", Holiday.date) == year)
        if is_active is not None:
            conditions.append(Holiday.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_holidays_in_range(
        self, start_date: date, end_date: date
    ) -> List[Holiday]:
        """Ambil holidays dalam range tanggal."""
        result = await self.db.execute(
            select(Holiday).where(
                and_(
                    Holiday.date >= start_date,
                    Holiday.date <= end_date,
                    Holiday.is_active == True,
                )
            ).order_by(Holiday.date.asc())
        )
        return list(result.scalars().all())
