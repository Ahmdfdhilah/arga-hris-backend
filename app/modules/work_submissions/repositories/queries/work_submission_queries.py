"""
WorkSubmission Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.work_submissions.models.work_submission import WorkSubmission


class WorkSubmissionQueries:
    """Read operations for WorkSubmission"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, submission_id: int) -> Optional[WorkSubmission]:
        result = await self.db.execute(
            select(WorkSubmission).where(WorkSubmission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmission], int]:
        query = select(WorkSubmission).where(WorkSubmission.employee_id == employee_id)
        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(WorkSubmission.submission_month.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_all(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmission], int]:
        query = select(WorkSubmission)
        if employee_id:
            query = query.where(WorkSubmission.employee_id == employee_id)
        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.order_by(WorkSubmission.submission_month.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def check_existing(
        self,
        employee_id: int,
        submission_month: date,
        exclude_id: Optional[int] = None,
    ) -> Optional[WorkSubmission]:
        query = select(WorkSubmission).where(
            and_(
                WorkSubmission.employee_id == employee_id,
                WorkSubmission.submission_month == submission_month,
            )
        )
        if exclude_id:
            query = query.where(WorkSubmission.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_employee_and_month(
        self,
        employee_id: int,
        submission_month: date,
    ) -> Optional[WorkSubmission]:
        query = select(WorkSubmission).where(
            and_(
                WorkSubmission.employee_id == employee_id,
                WorkSubmission.submission_month == submission_month,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
