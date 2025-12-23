from typing import Any, Dict
import logging
from app.modules.employees.models.employee import Employee
from datetime import datetime
import uuid
from app.core.messaging import EventPublisher, DomainEvent

logger = logging.getLogger(__name__)


class EmployeeEventUtil:
    """Utility for publishing employee events"""

    @staticmethod
    def to_event_data(employee: Employee) -> Dict[str, Any]:
        """Convert employee to event data payload"""
        data = {
            "id": employee.id,
            "user_id": employee.user_id,
            "code": employee.code,
            "name": employee.name,
            "email": employee.email,
            "position": employee.position,
            "site": employee.site,
            "type": employee.type,
            "org_unit_id": employee.org_unit_id,
            "supervisor_id": employee.supervisor_id,
            "is_active": employee.is_active,
        }
        if employee.user:
            data["user"] = {
                "id": employee.user.id,  # SSO UUID
                "name": employee.user.name,
                "email": employee.user.email,
                "phone": employee.user.phone,
                "gender": employee.user.gender,
            }
        return data

    @staticmethod
    async def publish(
        event_publisher: EventPublisher, event_type: str, employee: Employee
    ) -> None:
        """Publish employee event"""
        if not event_publisher:
            return

        try:
            data = EmployeeEventUtil.to_event_data(employee)
            
            event = DomainEvent(
                entity_type="employee",
                event_action=event_type,
                entity_id=employee.id,
                data=data,
                timestamp=datetime.utcnow(),
                source_service="hris",
                correlation_id=str(uuid.uuid4())
            )
            
            await event_publisher.publish(event)
        except Exception as e:
            logger.warning(f"Failed to publish employee.{event_type}: {e}")
