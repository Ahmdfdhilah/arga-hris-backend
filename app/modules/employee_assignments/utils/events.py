"""
Event utilities for Employee Assignments module.
"""

from typing import Dict, Any, Optional
import logging

from app.modules.employee_assignments.models.employee_assignment import EmployeeAssignment
from app.core.messaging.event_publisher import event_publisher
from app.core.messaging.events import EventType

logger = logging.getLogger(__name__)


class AssignmentEventUtil:
    """Utility for assignment event publishing."""

    @staticmethod
    def to_event_data(assignment: EmployeeAssignment) -> Dict[str, Any]:
        """Build event data payload from EmployeeAssignment model."""
        return {
            "id": assignment.id,
            "employee_id": assignment.employee_id,
            "replaced_employee_id": assignment.replaced_employee_id,
            "org_unit_id": assignment.org_unit_id,
            "status": assignment.status,
            "start_date": assignment.start_date.isoformat() if assignment.start_date else None,
            "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
            "leave_request_id": assignment.leave_request_id,
            "reason": assignment.reason,
        }

    @staticmethod
    async def publish(
        event_action: str,
        assignment: EmployeeAssignment,
    ) -> None:
        """
        Publish assignment event.
        
        Args:
            event_action: created, activated, cancelled, expired
            assignment: EmployeeAssignment model
        """
        try:
            event_data = AssignmentEventUtil.to_event_data(assignment)
            event_data["event_action"] = event_action

            # Map action to EventType
            event_type_map = {
                "created": EventType.CREATED,
                "activated": EventType.UPDATED,
                "cancelled": EventType.DELETED,
                "expired": EventType.UPDATED,
            }
            event_type = event_type_map.get(event_action, EventType.UPDATED)

            await event_publisher.publish_entity_event(
                event_type=event_type,
                entity_type="assignment",
                entity_id=assignment.id,
                data=event_data,
            )
        except Exception as e:
            logger.warning(f"Failed to publish assignment.{event_action} event: {e}")