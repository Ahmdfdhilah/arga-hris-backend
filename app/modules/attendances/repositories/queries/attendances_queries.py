"""
Attendance Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendances.models.attendances import Attendance


class AttendanceQueries:
    """Read operations for Attendance"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, attendance_id: int) -> Optional[Attendance]:
        result = await self.db.execute(
            select(Attendance).where(Attendance.id == attendance_id)
        )
        return result.scalar_one_or_none()

    async def get_by_employee_and_date(
        self, employee_id: int, attendance_date: date
    ) -> Optional[Attendance]:
        result = await self.db.execute(
            select(Attendance).where(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.attendance_date == attendance_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance).where(Attendance.employee_id == employee_id)
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(Attendance.check_in_time.desc().nulls_last()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance).where(Attendance.employee_id.in_(employee_ids))
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(Attendance.check_in_time.desc().nulls_last()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_by_org_unit(
        self,
        org_unit_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance).where(Attendance.org_unit_id == org_unit_id)
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(Attendance.check_in_time.desc().nulls_last()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_all(
        self,
        employee_ids: Optional[List[int]] = None,
        org_unit_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance)
        if employee_ids:
            query = query.where(Attendance.employee_id.in_(employee_ids))
        if org_unit_id:
            query = query.where(Attendance.org_unit_id == org_unit_id)
        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(Attendance.check_in_time.desc().nulls_last()).offset(skip).limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_report_by_org_unit(
        self,
        org_unit_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Attendance]:
        query = (
            select(Attendance)
            .where(
                and_(
                    Attendance.org_unit_id == org_unit_id,
                    Attendance.attendance_date >= start_date,
                    Attendance.attendance_date <= end_date,
                )
            )
            .order_by(Attendance.employee_id, Attendance.attendance_date)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_employee_ids(
        self,
        employee_ids: List[int],
        start_date: date,
        end_date: date,
    ) -> List[Attendance]:
        if not employee_ids:
            return []
        query = (
            select(Attendance)
            .where(
                and_(
                    Attendance.employee_id.in_(employee_ids),
                    Attendance.attendance_date >= start_date,
                    Attendance.attendance_date <= end_date,
                )
            )
            .order_by(Attendance.employee_id, Attendance.attendance_date)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
