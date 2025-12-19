"""
Assignment Command Repository - Write operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)


class AssignmentCommands:
    """Write operations for EmployeeAssignment"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> EmployeeAssignment:
        """Create new assignment."""
        assignment = EmployeeAssignment(**data)
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def update(
        self, assignment_id: int, data: Dict[str, Any]
    ) -> Optional[EmployeeAssignment]:
        """Update assignment. Returns None if not found."""
        from app.modules.employee_assignments.repositories.queries import (
            AssignmentQueries,
        )

        queries = AssignmentQueries(self.db)
        assignment = await queries.get_by_id(assignment_id, load_relationships=False)
        if not assignment:
            return None

        for key, value in data.items():
            setattr(assignment, key, value)

        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def update_status(
        self,
        assignment_id: int,
        new_status: str,
        updated_by: Optional[str] = None,
    ) -> Optional[EmployeeAssignment]:
        """Update assignment status dengan optional audit field."""
        data = {"status": new_status}
        if updated_by:
            data["updated_by"] = updated_by
        return await self.update(assignment_id, data)

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
