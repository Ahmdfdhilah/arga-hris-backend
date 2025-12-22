"""
Restore OrgUnit Use Case
"""

from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher

from app.modules.org_units.utils.events import OrgUnitEventUtil


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

        if org_unit.parent_id:
            parent = await self.queries.get_by_id_with_deleted(org_unit.parent_id)
            if parent and parent.is_deleted():
                raise BadRequestException(
                    "Cannot restore: parent unit is still deleted"
                )

        restored = await self.commands.restore(org_unit_id)
        await OrgUnitEventUtil.publish(self.event_publisher, "updated", restored)

        return restored
