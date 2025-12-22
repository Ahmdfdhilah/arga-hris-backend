"""
Create OrgUnit Use Case
"""

from typing import Optional
from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import ConflictException, BadRequestException
from app.core.messaging.event_publisher import EventPublisher

from app.modules.org_units.utils.path_calculator import OrgUnitPathUtil
from app.modules.org_units.utils.events import OrgUnitEventUtil


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
        existing = await self.queries.get_by_code(code)
        if existing:
            raise ConflictException(f"Organization unit code '{code}' already exists")

        level = 1
        path = "0"
        parent = None

        if parent_id:
            parent = await self.queries.get_by_id(parent_id)
            if not parent:
                raise BadRequestException(
                    f"Parent organization unit with ID {parent_id} not found"
                )
            level = parent.level + 1

        if head_id and self.employee_queries:
            head = await self.employee_queries.get_by_id(head_id)
            if not head:
                raise BadRequestException(f"Head employee with ID {head_id} not found")

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

        path, level = OrgUnitPathUtil.build_initial_path(parent, created.id)
        created.path = path
        created.level = level
        await self.commands.update(created)

        created = await self.queries.get_by_id(created.id)
        await OrgUnitEventUtil.publish(self.event_publisher, "created", created)

        return created
