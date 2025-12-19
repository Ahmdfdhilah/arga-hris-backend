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
from app.core.messaging.event_publisher import event_publisher
from app.core.messaging.events import EventType


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
        """
        Activate assignment.

        Requirements:
        - Assignment harus exist
        - Status harus pending

        Returns:
            AssignmentResponse dengan status active
        """
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )

        if assignment.status != "pending":
            raise BadRequestException(
                f"Assignment tidak bisa diaktifkan. Status saat ini: {assignment.status}"
            )

        # Update status
        await self.commands.update_status(
            assignment_id=assignment_id,
            new_status="active",
            updated_by=updated_by,
        )

        # Reload
        assignment = await self.queries.get_by_id(assignment_id)

        # Publish event
        await self._publish_activated_event(assignment)

        return AssignmentResponse.from_orm_with_relationships(assignment)

    async def _publish_activated_event(self, assignment) -> None:
        """Publish assignment.activated event (custom event type)."""
        from app.modules.employee_assignments.utils.events import (
            build_assignment_event_data,
        )

        event_data = build_assignment_event_data(assignment)
        # Use UPDATED event type but with "activated" semantic in data
        await event_publisher.publish_entity_event(
            event_type=EventType.UPDATED,
            entity_type="assignment",
            entity_id=assignment.id,
            data={**event_data, "event_action": "activated"},
        )
