"""
WorkSubmission Command Repository - Write operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.work_submissions.models.work_submission import WorkSubmission


class WorkSubmissionCommands:
    """Write operations for WorkSubmission"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> WorkSubmission:
        submission = WorkSubmission(**data)
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async def update(self, submission_id: int, data: Dict[str, Any]) -> Optional[WorkSubmission]:
        from app.modules.work_submissions.repositories.queries import WorkSubmissionQueries
        
        queries = WorkSubmissionQueries(self.db)
        submission = await queries.get_by_id(submission_id)
        if not submission:
            return None
        
        for key, value in data.items():
            setattr(submission, key, value)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async def delete(self, submission_id: int) -> bool:
        from app.modules.work_submissions.repositories.queries import WorkSubmissionQueries
        
        queries = WorkSubmissionQueries(self.db)
        submission = await queries.get_by_id(submission_id)
        if not submission:
            return False
        
        await self.db.delete(submission)
        await self.db.commit()
        return True
