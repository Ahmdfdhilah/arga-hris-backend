"""
Use Case: Cancel Assignment

Changes assignment status to cancelled.
Bisa dipanggil untuk pending atau active assignments.
"""

from typing import Optional

from app.modules.employee_assignments.schemas.requests import AssignmentCancelRequest
from app.modules.employee_assignments.schemas.responses import AssignmentResponse
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.core.exceptions import NotFoundException, BadRequestException

from app.modules.employee_assignments.utils import AssignmentEventUtil


class CancelAssignmentUseCase:
    """Cancel pending or active assignment."""

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
        request: Optional[AssignmentCancelRequest] = None,
        updated_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Cancel assignment."""
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )

        if assignment.status not in ["pending", "active"]:
            raise BadRequestException(
                f"Assignment tidak bisa dibatalkan. Status saat ini: {assignment.status}"
            )

        assignment.status = "cancelled"
        if updated_by:
            assignment.updated_by = updated_by
        if request and request.reason:
            assignment.reason = request.reason

        await self.commands.update(assignment)

        updated = await self.queries.get_by_id(assignment_id)
        await AssignmentEventUtil.publish("cancelled", updated)

        return AssignmentResponse.from_orm_with_relationships(updated)
