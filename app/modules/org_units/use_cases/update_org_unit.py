from typing import Optional, Dict, Any
import logging
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher

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

                    # Check for circular hierarchy
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

        # Handle head change - update supervisor relationships
        # We also trigger this if parent_id changed? (Since effective supervisor might come from parent)
        if "head_id" in update_data or parent_changed:
            new_head_id = org_unit.head_id  # Could be None
            if self.employee_queries and self.employee_commands:
                await self._handle_head_change(
                    org_unit_id, old_head_id, new_head_id, updated_by
                )

        # Recalculate path if parent changed
        if parent_changed:
            await self._recalculate_path(org_unit)

        # Reload with relationships
        updated = await self.queries.get_by_id(org_unit_id)

        # Publish event
        if self.event_publisher:
            await self._publish_event("updated", updated)

        return updated

    async def _recalculate_path(self, org_unit: OrgUnit) -> None:
        """Recalculate path for org unit and all descendants"""
        if org_unit.parent_id:
            parent = await self.queries.get_by_id(org_unit.parent_id)
            if parent:
                old_path = org_unit.path
                org_unit.path = f"{parent.path}.{org_unit.id}"
                org_unit.level = parent.level + 1
                await self.commands.update(org_unit)

                # Update all descendants
                children, _ = await self.queries.get_children(
                    org_unit.id, recursive=True, skip=0, limit=1000
                )
                for child in children:
                    child.path = child.path.replace(old_path, org_unit.path, 1)
                    parts = child.path.split(".")
                    child.level = len(parts)
                    await self.commands.update(child)
        else:
            org_unit.path = str(org_unit.id)
            org_unit.level = 1
            await self.commands.update(org_unit)

    async def _handle_head_change(
        self,
        org_unit_id: int,
        old_head_id: Optional[int],
        new_head_id: Optional[int],
        updated_by: str,
    ) -> None:
        """
        Handle Org Unit Head change:
        - If Head changed, update direct subordinates' supervisor_id.
        - If Head cleared, resolve effective supervisor (from parent).
        - Propagate to child Org Units that do not have their own Head (inherit).
        """
        # 1. Resolve who the supervisor should be for this unit (Generic)
        effective_supervisor_id = new_head_id
        if not effective_supervisor_id:
            # If head was cleared, look upstream
            effective_supervisor_id = await self._resolve_supervisor_for_unit(
                org_unit_id
            )

        # 2. Update Direct Members of this Unit
        members, _ = await self.employee_queries.list(org_unit_id=org_unit_id, limit=1000)
        logger.info(
            f"Updating {len(members)} members for OrgUnit {org_unit_id}. Effective Sup: {effective_supervisor_id}"
        )

        for emp in members:
            target_sup = effective_supervisor_id

            if target_sup == emp.id:
                logger.info(
                    f"Employee {emp.id} is the generic supervisor. Re-resolving excluding self."
                )
                target_sup = await self._resolve_supervisor_for_unit(
                    org_unit_id, exclude_employee_id=emp.id
                )
                logger.info(f"Re-resolved supervisor for {emp.id}: {target_sup}")

            if emp.supervisor_id != target_sup:
                logger.info(
                    f"Updating Employee {emp.id}: supervisor {emp.supervisor_id} -> {target_sup}"
                )
                emp.supervisor_id = target_sup
                emp.set_updated_by(updated_by)
                await self.employee_commands.update(emp)

        # 3. Propagate to child units
        children, _ = await self.queries.get_children(org_unit_id, recursive=False)
        for child in children:
            if not child.head_id:
                await self._handle_head_change(child.id, None, None, updated_by)

    async def _resolve_supervisor_for_unit(
        self, org_unit_id: int, exclude_employee_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Internal helper to resolve effective supervisor for a unit.
        Simulates the upstream lookup.
        If exclude_employee_id is provided, it skips that employee if found as head.
        """
        current_unit = await self.queries.get_by_id(org_unit_id)
        while current_unit:
            logger.info(
                f"Resolving sup for Unit {org_unit_id}. Checking Unit {current_unit.id}. Head: {current_unit.head_id}. Exclude: {exclude_employee_id}"
            )
            if current_unit.head_id:
                if (
                    exclude_employee_id is None
                    or current_unit.head_id != exclude_employee_id
                ):
                    return current_unit.head_id
                else:
                    logger.info("Skipping head because matches exclude_employee_id")

            if not current_unit.parent_id:
                break
            current_unit = await self.queries.get_by_id(current_unit.parent_id)
        return None

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
        except Exception as e:
            logger.warning(f"Failed to publish org_unit.{event_type} event: {e}")
