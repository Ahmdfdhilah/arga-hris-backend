"""
Use Case: Expire Assignment

Changes assignment status from active to expired.
Dipanggil oleh scheduler job saat end_date terlewati.
"""

from typing import Optional

from app.modules.employee_assignments.schemas.responses import AssignmentResponse
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.core.exceptions import NotFoundException, BadRequestException

from app.modules.employee_assignments.utils import AssignmentEventUtil


class ExpireAssignmentUseCase:
    """Expire active assignment."""

    def __init__(
        self,
        queries: AssignmentQueries,
        commands: AssignmentCommands,
    ):
        self.queries = queries
        self.commands = commands

    async def execute(
        self,
        assignment_id: int,
        updated_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Expire assignment."""
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )

        if assignment.status != "active":
            raise BadRequestException(
                f"Assignment tidak bisa di-expire. Status saat ini: {assignment.status}"
            )

        assignment.status = "expired"
        if updated_by:
            assignment.updated_by = updated_by

        await self.commands.update(assignment)

        updated = await self.queries.get_by_id(assignment_id)
        await AssignmentEventUtil.publish("expired", updated)

        return AssignmentResponse.from_orm_with_relationships(updated)
