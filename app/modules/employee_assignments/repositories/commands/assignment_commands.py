"""
Assignment Command Repository - Write operations
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)


class AssignmentCommands:
    """Write operations for EmployeeAssignment"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, assignment: EmployeeAssignment) -> EmployeeAssignment:
        """Create new assignment."""
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def update(self, assignment: EmployeeAssignment) -> EmployeeAssignment:
        """Update assignment."""
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def delete(self, assignment_id: int) -> bool:
        """Hard delete assignment. Returns False if not found."""
        from app.modules.employee_assignments.repositories.queries import (
            AssignmentQueries,
        )

        queries = AssignmentQueries(self.db)
        assignment = await queries.get_by_id(assignment_id, load_relationships=False)
        if not assignment:
            return False

        await self.db.delete(assignment)
        await self.db.commit()
        return True
