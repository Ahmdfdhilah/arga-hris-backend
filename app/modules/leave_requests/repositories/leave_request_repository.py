from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories.base_repository import BaseRepository
from app.modules.leave_requests.models.leave_request import LeaveRequest


class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    """Repository untuk operasi database leave request."""

    def __init__(self, db: AsyncSession):
        super().__init__(LeaveRequest, db)

    async def list_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[LeaveRequest]:
        """List leave requests berdasarkan employee dengan filter."""
        query = select(LeaveRequest).where(LeaveRequest.employee_id == employee_id)

        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        query = query.order_by(LeaveRequest.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        """Hitung total leave requests berdasarkan employee."""
        query = select(func.count(LeaveRequest.id)).where(
            LeaveRequest.employee_id == employee_id
        )

        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_all_leave_requests(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[LeaveRequest]:
        """List leave requests dengan berbagai filter untuk admin."""
        query = select(LeaveRequest)

        if employee_id is not None:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        query = query.order_by(LeaveRequest.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all_leave_requests(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        """Hitung total leave requests dengan berbagai filter untuk admin."""
        query = select(func.count(LeaveRequest.id))

        if employee_id is not None:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def check_overlapping_leave(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_id: Optional[int] = None,
    ) -> Optional[LeaveRequest]:
        """Cek apakah ada leave request yang overlap dengan tanggal yang diberikan."""
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date,
            )
        )

        if exclude_id:
            query = query.where(LeaveRequest.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def is_employee_on_leave(
        self,
        employee_id: int,
        check_date: date,
    ) -> Optional[LeaveRequest]:
        """Cek apakah employee sedang cuti pada tanggal tertentu."""
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.start_date <= check_date,
                LeaveRequest.end_date >= check_date,
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[LeaveRequest]:
        """List leave requests berdasarkan multiple employee IDs (untuk team/subordinates)."""
        query = select(LeaveRequest).where(LeaveRequest.employee_id.in_(employee_ids))

        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        query = query.order_by(LeaveRequest.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        """Hitung total leave requests berdasarkan multiple employee IDs."""
        query = select(func.count(LeaveRequest.id)).where(
            LeaveRequest.employee_id.in_(employee_ids)
        )

        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)

        result = await self.db.execute(query)
        return result.scalar_one()
