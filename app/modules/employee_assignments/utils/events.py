"""
Event utilities for Employee Assignments module.
"""

from typing import Dict, Any, Optional
import logging

from app.modules.employee_assignments.models.employee_assignment import EmployeeAssignment
from datetime import datetime
import uuid
from app.core.messaging import event_publisher, DomainEvent
from app.core.enums.event_type import EventType

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
            
            # Create standardized DomainEvent
            event = DomainEvent(
                entity_type="assignment",
                event_action=event_action,
                entity_id=assignment.id,
                data=event_data,
                timestamp=datetime.utcnow(),
                source_service="hris",
                correlation_id=str(uuid.uuid4())
            )

            await event_publisher.publish(event)
        except Exception as e:
            logger.warning(f"Failed to publish assignment.{event_action} event: {e}")