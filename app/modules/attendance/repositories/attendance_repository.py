from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories.base_repository import BaseRepository
from app.modules.attendance.models.attendance import Attendance


class AttendanceRepository(BaseRepository[Attendance]):
    """Repository untuk operasi database attendance."""

    def __init__(self, db: AsyncSession):
        super().__init__(Attendance, db)

    async def get_by_employee_and_date(
        self, employee_id: int, attendance_date: date
    ) -> Optional[Attendance]:
        """Ambil attendance berdasarkan employee dan tanggal."""
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
    ) -> List[Attendance]:
        """List attendance berdasarkan employee dengan filter tanggal."""
        query = select(Attendance).where(Attendance.employee_id == employee_id)

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)

        query = query.order_by(Attendance.attendance_date.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """Hitung total attendance berdasarkan employee."""
        query = select(func.count(Attendance.id)).where(Attendance.employee_id == employee_id)

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Attendance]:
        """List attendance berdasarkan multiple employees dengan filter."""
        query = select(Attendance).where(Attendance.employee_id.in_(employee_ids))

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        query = query.order_by(Attendance.attendance_date.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Hitung total attendance berdasarkan multiple employees."""
        query = select(func.count(Attendance.id)).where(
            Attendance.employee_id.in_(employee_ids)
        )

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_by_org_unit(
        self,
        org_unit_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Attendance]:
        """List attendance berdasarkan org_unit_id."""
        query = select(Attendance).where(Attendance.org_unit_id == org_unit_id)

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        query = query.order_by(Attendance.attendance_date.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_org_unit(
        self,
        org_unit_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Hitung total attendance berdasarkan org_unit_id."""
        query = select(func.count(Attendance.id)).where(Attendance.org_unit_id == org_unit_id)

        if start_date:
            query = query.where(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.where(Attendance.attendance_date <= end_date)
        if status:
            query = query.where(Attendance.status == status)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_all_attendances(
        self,
        employee_ids: Optional[List[int]] = None,
        org_unit_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Attendance]:
        """List attendance dengan berbagai filter untuk admin."""
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

        query = query.order_by(Attendance.attendance_date.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all_attendances(
        self,
        employee_ids: Optional[List[int]] = None,
        org_unit_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Hitung total attendance dengan berbagai filter untuk admin."""
        query = select(func.count(Attendance.id))

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

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_attendance_report_by_org_unit(
        self,
        org_unit_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Attendance]:
        """
        Ambil semua attendance untuk report berdasarkan org_unit_id dan date range.
        Tanpa paginasi untuk keperluan export Excel.
        """
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

    async def get_attendances_by_employee_ids(
        self,
        employee_ids: List[int],
        start_date: date,
        end_date: date,
    ) -> List[Attendance]:
        """
        Ambil semua attendance untuk list employee IDs dalam date range.
        Digunakan untuk calculate summary per employee.
        """
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
