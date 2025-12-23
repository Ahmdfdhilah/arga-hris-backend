"""
OrgUnit Event Utility
Handles event publishing for org unit operations.
"""

from typing import Dict, Any, Optional
import logging

from app.modules.org_units.models.org_unit import OrgUnit
from datetime import datetime
import uuid
from app.core.messaging import EventPublisher, DomainEvent

logger = logging.getLogger(__name__)


class OrgUnitEventUtil:
    """Utility for org unit event publishing"""

    @staticmethod
    def to_event_data(org_unit: OrgUnit) -> Dict[str, Any]:
        """Convert OrgUnit model to event data dict"""
        return {
            "id": org_unit.id,
            "code": org_unit.code,
            "name": org_unit.name,
            "type": org_unit.type,
            "parent_id": org_unit.parent_id,
            "head_id": org_unit.head_id,
            "level": org_unit.level,
            "path": org_unit.path,
            "is_active": org_unit.is_active,
        }

    @staticmethod
    async def publish(
        event_publisher: Optional[EventPublisher],
        event_type: str,
        org_unit: OrgUnit,
    ) -> None:
        """Publish org unit event (created, updated, deleted)"""
        if not event_publisher:
            return

        try:
            data = OrgUnitEventUtil.to_event_data(org_unit)
            
            event = DomainEvent(
                entity_type="org_unit",
                event_action=event_type,
                entity_id=org_unit.id,
                data=data,
                timestamp=datetime.utcnow(),
                source_service="hris",
                correlation_id=str(uuid.uuid4())
            )
            
            await event_publisher.publish(event)
        except Exception as e:
            logger.warning(f"Failed to publish org_unit.{event_type} event: {e}")
