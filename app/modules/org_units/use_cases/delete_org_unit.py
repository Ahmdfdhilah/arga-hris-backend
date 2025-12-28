"""
Delete OrgUnit Use Case
"""

from typing import Optional
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging import EventPublisher

from app.modules.org_units.utils.events import OrgUnitEventUtil


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

        active_count = await self.queries.count_active_employees(org_unit_id)
        if active_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {active_count} active employees. "
                "Move or deactivate employees first"
            )

        child_count = await self.queries.count_active_children(org_unit_id)
        if child_count > 0:
            raise BadRequestException(
                f"Cannot delete org unit: has {child_count} child units. "
                "Delete or move child units first"
            )

        await self.commands.delete(org_unit_id, deleted_by)

        deleted_ou = await self.queries.get_by_id_with_deleted(org_unit_id)
        await OrgUnitEventUtil.publish(self.event_publisher, "deleted", deleted_ou)
