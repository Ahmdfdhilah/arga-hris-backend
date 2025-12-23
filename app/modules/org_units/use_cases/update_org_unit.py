"""
Update OrgUnit Use Case
Clean implementation using extracted utils.
"""

from typing import Optional, Dict, Any
import logging

from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging import EventPublisher

from app.modules.org_units.utils.path_calculator import OrgUnitPathUtil
from app.modules.org_units.utils.head_propagation import OrgUnitHeadUtil
from app.modules.org_units.utils.events import OrgUnitEventUtil
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class UpdateOrgUnitUseCase:
    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        employee_queries: Optional[EmployeeQueries] = None,
        employee_commands: Optional[EmployeeCommands] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.employee_commands = employee_commands
        self.event_publisher = event_publisher

    async def execute(
        self,
        org_unit_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> OrgUnit:
        org_unit = await self.queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Organization unit with ID {org_unit_id} not found"
            )

        old_head_id = org_unit.head_id
        parent_changed = False

        # Validate parent change
        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]
            if parent_id != org_unit.parent_id:
                if parent_id is not None and parent_id == org_unit_id:
                    raise BadRequestException(
                        "Organization unit cannot be its own parent"
                    )

                if parent_id is not None:
                    parent = await self.queries.get_by_id(parent_id)
                    if not parent:
                        raise BadRequestException(
                            f"Parent organization unit with ID {parent_id} not found"
                        )

                    if parent.path and str(org_unit_id) in parent.path.split("."):
                        raise BadRequestException("Circular hierarchy detected")

                parent_changed = True

        # Check head existence
        if "head_id" in update_data:
            head_id = update_data["head_id"]
            if head_id is not None and self.employee_queries:
                head = await self.employee_queries.get_by_id(head_id)
                if not head:
                    raise BadRequestException(
                        f"Head employee with ID {head_id} not found"
                    )

        # Update fields
        if "name" in update_data:
            org_unit.name = update_data["name"]
        if "type" in update_data:
            org_unit.type = update_data["type"]
        if "parent_id" in update_data:
            org_unit.parent_id = update_data["parent_id"]
        if "head_id" in update_data:
            org_unit.head_id = update_data["head_id"]
        if "description" in update_data:
            org_unit.description = update_data["description"]
        if "is_active" in update_data:
            org_unit.is_active = update_data["is_active"]

        org_unit.set_updated_by(updated_by)
        await self.commands.update(org_unit)

        # Track affected entities for event publishing
        affected_employee_ids = []
        affected_org_unit_ids = []

        # Handle head change - delegate to util
        if ("head_id" in update_data or parent_changed) and self.employee_queries and self.employee_commands:
            new_head_id = org_unit.head_id
            affected_employee_ids = await OrgUnitHeadUtil.handle_head_change(
                self.queries,
                self.commands,
                self.employee_queries,
                self.employee_commands,
                org_unit_id,
                old_head_id,
                new_head_id,
                updated_by,
            )

        # Recalculate path if parent changed - delegate to util
        if parent_changed:
            affected_org_unit_ids = await OrgUnitPathUtil.recalculate_path(
                self.queries, self.commands, org_unit
            )

        updated = await self.queries.get_by_id(org_unit_id)

        await OrgUnitEventUtil.publish(self.event_publisher, "updated", updated)

        if self.event_publisher and affected_employee_ids:
            logger.info(f"Publishing employee.updated for {len(affected_employee_ids)} affected employees")
            for employee_id in affected_employee_ids:
                affected_employee = await self.employee_queries.get_by_id(employee_id)
                if affected_employee:
                    await EmployeeEventUtil.publish(
                        self.event_publisher,
                        "updated",
                        affected_employee
                    )
                    logger.debug(f"Published employee.updated for employee {employee_id}")

        if self.event_publisher and affected_org_unit_ids:
            logger.info(f"Publishing org_unit.updated for {len(affected_org_unit_ids)} affected descendants")
            for descendant_id in affected_org_unit_ids:
                affected_org_unit = await self.queries.get_by_id(descendant_id)
                if affected_org_unit:
                    await OrgUnitEventUtil.publish(
                        self.event_publisher,
                        "updated",
                        affected_org_unit
                    )
                    logger.debug(f"Published org_unit.updated for descendant {descendant_id}")

        return updated
