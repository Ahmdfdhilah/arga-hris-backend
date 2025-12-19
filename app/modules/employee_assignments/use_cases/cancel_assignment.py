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
from app.core.messaging.event_publisher import event_publisher
from app.core.messaging.events import EventType


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
        """
        Cancel assignment.

        Requirements:
        - Assignment harus exist
        - Status harus pending atau active

        Returns:
            AssignmentResponse dengan status cancelled
        """
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )

        if assignment.status not in ["pending", "active"]:
            raise BadRequestException(
                f"Assignment tidak bisa dibatalkan. Status saat ini: {assignment.status}"
            )

        # Update data
        update_data = {
            "status": "cancelled",
            "updated_by": updated_by,
        }

        # Tambahkan reason jika ada
        if request and request.reason:
            update_data["reason"] = request.reason

        await self.commands.update(assignment_id, update_data)

        # Reload
        assignment = await self.queries.get_by_id(assignment_id)

        # Publish event
        await self._publish_cancelled_event(assignment)

        return AssignmentResponse.from_orm_with_relationships(assignment)

    async def _publish_cancelled_event(self, assignment) -> None:
        """Publish assignment.cancelled event."""
        from app.modules.employee_assignments.utils.events import (
            build_assignment_event_data,
        )

        event_data = build_assignment_event_data(assignment)
        await event_publisher.publish_entity_event(
            event_type=EventType.DELETED,
            entity_type="assignment",
            entity_id=assignment.id,
            data={**event_data, "event_action": "cancelled"},
        )
