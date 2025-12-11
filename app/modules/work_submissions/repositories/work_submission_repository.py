from typing import Optional, List
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories.base_repository import BaseRepository
from app.modules.work_submissions.models.work_submission import WorkSubmission


class WorkSubmissionRepository(BaseRepository[WorkSubmission]):
    """Repository untuk operasi database work submission."""

    def __init__(self, db: AsyncSession):
        super().__init__(WorkSubmission, db)

    async def list_by_employee(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[WorkSubmission]:
        """List work submissions berdasarkan employee dengan filter."""
        query = select(WorkSubmission).where(WorkSubmission.employee_id == employee_id)

        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        query = query.order_by(WorkSubmission.submission_month.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_employee(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Hitung total work submissions berdasarkan employee."""
        query = select(func.count(WorkSubmission.id)).where(
            WorkSubmission.employee_id == employee_id
        )

        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def list_all_submissions(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[WorkSubmission]:
        """List work submissions dengan berbagai filter untuk admin."""
        query = select(WorkSubmission)

        if employee_id:
            query = query.where(WorkSubmission.employee_id == employee_id)
        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        query = query.order_by(WorkSubmission.submission_month.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all_submissions(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Hitung total work submissions dengan berbagai filter untuk admin."""
        query = select(func.count(WorkSubmission.id))

        if employee_id:
            query = query.where(WorkSubmission.employee_id == employee_id)
        if submission_month:
            query = query.where(WorkSubmission.submission_month == submission_month)
        if status:
            query = query.where(WorkSubmission.status == status)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def check_existing_submission(
        self,
        employee_id: int,
        submission_month: date,
        exclude_id: Optional[int] = None,
    ) -> Optional[WorkSubmission]:
        """Cek apakah sudah ada submission untuk employee di bulan tertentu."""
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

    async def get_submission_by_employee_and_month(
        self,
        employee_id: int,
        submission_month: date,
    ) -> Optional[WorkSubmission]:
        """Get submission berdasarkan employee dan bulan."""
        query = select(WorkSubmission).where(
            and_(
                WorkSubmission.employee_id == employee_id,
                WorkSubmission.submission_month == submission_month,
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
