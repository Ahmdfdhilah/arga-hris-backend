from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import ConflictException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher


class CreateOrgUnitUseCase:
    def __init__(
        self,
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        employee_queries: Optional[EmployeeQueries] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.event_publisher = event_publisher

    async def execute(
        self,
        code: str,
        name: str,
        type: str,
        created_by: str,
        parent_id: Optional[int] = None,
        head_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> OrgUnit:
        # Check if code already exists
        existing = await self.queries.get_by_code(code)
        if existing:
            raise ConflictException(f"Organization unit code '{code}' already exists")

        # Calculate level and path based on parent
        level = 1
        path = "0"  # Temporary, will be updated after insert

        if parent_id:
            parent = await self.queries.get_by_id(parent_id)
            if not parent:
                raise BadRequestException(
                    f"Parent organization unit with ID {parent_id} not found"
                )
            level = parent.level + 1

        # Check if head exists if provided
        if head_id and self.employee_queries:
            head = await self.employee_queries.get_by_id(head_id)
            if not head:
                raise BadRequestException(f"Head employee with ID {head_id} not found")

        # Create org unit
        org_unit = OrgUnit(
            code=code,
            name=name,
            type=type,
            parent_id=parent_id,
            level=level,
            path=path,
            head_id=head_id,
            description=description,
            is_active=True,
        )
        org_unit.set_created_by(created_by)

        created = await self.commands.create(org_unit)

        # Update path with actual ID
        if parent_id:
            # Re-fetch parent to ensure valid state? Already fetched above.
            # But let's follow original logic where it re-fetches or uses parent object.
            # Original logic fetched parent again inside the block, can reuse 'parent' variable if scope allows.
            # Let's verify 'parent' variable availability.
            # In python variables define in if scope leak out.
            # But safer to reuse logic.
            # Let's just use the previously fetched parent if parent_id is set.
            # The original code fetched it again.
            parent = await self.queries.get_by_id(parent_id)
            created.path = f"{parent.path}.{created.id}"
        else:
            created.path = str(created.id)

        await self.commands.update(created)

        # Reload with relationships
        created = await self.queries.get_by_id(created.id)

        # Publish event
        if self.event_publisher:
            await self._publish_event("created", created)

        return created

    async def _publish_event(self, event_type: str, org_unit: OrgUnit) -> None:
        """Publish org unit event if publisher available"""
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
            if event_type == "created":
                await self.event_publisher.publish_org_unit_created(org_unit.id, data)
        except Exception:
            # Consider logging here if we had logger
            pass
