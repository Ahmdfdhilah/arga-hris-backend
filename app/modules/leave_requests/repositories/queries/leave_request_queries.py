"""
LeaveRequest Query Repository - Read operations
"""

from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.leave_requests.models.leave_request import LeaveRequest


class LeaveRequestQueries:
    """Read operations for LeaveRequest"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, leave_request_id: int) -> Optional[LeaveRequest]:
        result = await self.db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_request_id))
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[LeaveRequest]:
        query = select(LeaveRequest).where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        query = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        query = select(func.count(LeaveRequest.id)).where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        return (await self.db.execute(query)).scalar_one()

    async def list_all(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[LeaveRequest]:
        query = select(LeaveRequest)
        if employee_id is not None:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        query = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        query = select(func.count(LeaveRequest.id))
        if employee_id is not None:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        return (await self.db.execute(query)).scalar_one()

    async def check_overlapping(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_id: Optional[int] = None,
    ) -> Optional[LeaveRequest]:
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

    async def is_on_leave(self, employee_id: int, check_date: date) -> Optional[LeaveRequest]:
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
        query = select(LeaveRequest).where(LeaveRequest.employee_id.in_(employee_ids))
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        query = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employees(
        self,
        employee_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
    ) -> int:
        query = select(func.count(LeaveRequest.id)).where(LeaveRequest.employee_id.in_(employee_ids))
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        return (await self.db.execute(query)).scalar_one()
