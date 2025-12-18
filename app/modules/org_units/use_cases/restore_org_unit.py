from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher


class RestoreOrgUnitUseCase:
    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.event_publisher = event_publisher

    async def execute(self, org_unit_id: int) -> OrgUnit:
        org_unit = await self.queries.get_by_id_with_deleted(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        if not org_unit.is_deleted():
            raise BadRequestException("Organization unit is not deleted")

        # Check if parent is deleted
        if org_unit.parent_id:
            parent = await self.queries.get_by_id_with_deleted(org_unit.parent_id)
            if parent and parent.is_deleted():
                raise BadRequestException(
                    "Cannot restore: parent unit is still deleted"
                )

        restored = await self.commands.restore(org_unit_id)

        # Publish event (restored = updated)
        if self.event_publisher:
            await self._publish_event("updated", restored)

        return restored

    async def _publish_event(self, event_type: str, org_unit: OrgUnit) -> None:
        if not self.event_publisher:
            return

        try:
            data = {
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
            if event_type == "updated":
                await self.event_publisher.publish_org_unit_updated(org_unit.id, data)
        except Exception:
            pass
