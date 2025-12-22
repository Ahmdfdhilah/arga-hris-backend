"""
Use Case: Activate Assignment

Changes assignment status from pending to active.
Dipanggil oleh scheduler job saat start_date tercapai.
"""

from typing import Optional

from app.modules.employee_assignments.schemas.responses import AssignmentResponse
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.core.exceptions import NotFoundException, BadRequestException

from app.modules.employee_assignments.utils import AssignmentEventUtil


class ActivateAssignmentUseCase:
    """Activate pending assignment."""

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
        """Activate assignment."""
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )

        if assignment.status != "pending":
            raise BadRequestException(
                f"Assignment tidak bisa diaktifkan. Status saat ini: {assignment.status}"
            )

        assignment.status = "active"
        if updated_by:
            assignment.updated_by = updated_by

        await self.commands.update(assignment)

        updated = await self.queries.get_by_id(assignment_id)
        await AssignmentEventUtil.publish("activated", updated)

        return AssignmentResponse.from_orm_with_relationships(updated)
