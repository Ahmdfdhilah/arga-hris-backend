from typing import Optional, Tuple
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.core.messaging.event_publisher import EventPublisher
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import ConflictException

# Utils
from app.modules.employees.utils.supervisor_assignment import SupervisorAssignmentUtil
from app.modules.employees.utils.sso_sync import SSOSyncUtil
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class CreateEmployeeUseCase:
    """Use Case for creating a new employee."""

    def __init__(
        self,
        queries: EmployeeQueries,
        commands: EmployeeCommands,
        org_unit_queries: OrgUnitQueries,
        user_queries: UserQueries,
        user_commands: UserCommands,
        sso_client: SSOUserGRPCClient,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.org_unit_queries = org_unit_queries
        self.user_queries = user_queries
        self.user_commands = user_commands
        self.sso_client = sso_client
        self.event_publisher = event_publisher

    async def execute(
        self,
        number: str,
        first_name: str,
        last_name: str,
        email: str,
        created_by: str,
        org_unit_id: Optional[int] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        gender: Optional[str] = None,
        supervisor_id: Optional[int] = None,
    ) -> Tuple[Employee, str]:
        """
        Execute the create employee use case.
        Returns Tuple[Employee, warning_message]
        """
        # Check if number exists
        existing_number = await self.queries.get_by_number(number)
        if existing_number:
            raise ConflictException(f"Employee number '{number}' already exists")

        # 1. Create/Sync SSO User
        local_user = await SSOSyncUtil.create_sso_user(
            sso_client=self.sso_client,
            user_queries=self.user_queries,
            user_commands=self.user_commands,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            gender=gender,
        )

        # 2. Auto-resolve supervisor if not provided but org_unit is
        final_supervisor_id = supervisor_id
        if org_unit_id and not final_supervisor_id:
            final_supervisor_id = await SupervisorAssignmentUtil.resolve_supervisor(
                org_unit_queries=self.org_unit_queries,
                org_unit_id=org_unit_id,
                exclude_employee_id=None,
            )

        # 3. Create Employee
        employee = Employee(
            user_id=local_user.id,
            number=number,
            position=position,
            type=employee_type,
            org_unit_id=org_unit_id,
            supervisor_id=final_supervisor_id,
            is_active=True,
        )
        employee.set_created_by(created_by)

        created = await self.commands.create(employee)
        # Reload to get relationships
        created = await self.queries.get_by_id(created.id)

        # 4. Publish Event
        if self.event_publisher:
            await EmployeeEventUtil.publish(self.event_publisher, "created", created)

        return created, ""
