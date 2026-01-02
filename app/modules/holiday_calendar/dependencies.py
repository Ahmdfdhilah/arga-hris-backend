"""Dependencies untuk Holiday Calendar module."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.modules.holiday_calendar.repositories import HolidayQueries, HolidayCommands
from app.modules.holiday_calendar.services import HolidayService


async def get_holiday_queries(
    db: AsyncSession = Depends(get_db),
) -> HolidayQueries:
    """Dependency untuk HolidayQueries."""
    return HolidayQueries(db)


async def get_holiday_commands(
    db: AsyncSession = Depends(get_db),
) -> HolidayCommands:
    """Dependency untuk HolidayCommands."""
    return HolidayCommands(db)


async def get_holiday_service(
    queries: HolidayQueries = Depends(get_holiday_queries),
    commands: HolidayCommands = Depends(get_holiday_commands),
) -> HolidayService:
    """Dependency untuk HolidayService."""
    return HolidayService(queries, commands)

