from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher


class DeleteOrgUnitUseCase:
    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.event_publisher = event_publisher

    async def execute(self, org_unit_id: int, deleted_by: str) -> None:
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        if org_unit.is_deleted():
            raise BadRequestException("Organization unit is already deleted")

        # Check for active employees
        active_count = await self.queries.count_active_employees(org_unit_id)
        if active_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {active_count} active employees. "
                "Move or deactivate employees first"
            )

        # Check for child units
        child_count = await self.queries.count_active_children(org_unit_id)
        if child_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {child_count} child units. "
                "Delete or move child units first"
            )

        # Soft delete
        await self.commands.delete(org_unit_id, deleted_by)

        # Get updated org unit content for event
        deleted_ou = await self.queries.get_by_id_with_deleted(org_unit_id)

        # Publish event
        if self.event_publisher:
            await self._publish_event("deleted", deleted_ou)

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
            if event_type == "deleted":
                await self.event_publisher.publish_org_unit_deleted(org_unit.id, data)
        except Exception:
            pass
