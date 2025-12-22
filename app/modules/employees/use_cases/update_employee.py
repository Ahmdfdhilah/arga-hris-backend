from typing import Optional, Dict, Any
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.core.messaging.event_publisher import EventPublisher
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    BadRequestException,
)

# Utils
from app.modules.employees.utils.supervisor_assignment import SupervisorAssignmentUtil
from app.modules.employees.utils.sso_sync import SSOSyncUtil
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class UpdateEmployeeUseCase:
    """Use Case for updating specific employee."""

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
        employee_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> Employee:
        """
        Execute the update employee use case.
        
        - name: Updates denormalized name on Employee only (NOT synced to SSO)
        - email/phone: Synced to SSO
        - Sending null/None explicitly clears optional fields
        """
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        # 0. Check Code Uniqueness
        if "code" in update_data:
            code = update_data["code"]
            if code is None:
                raise BadRequestException("Employee code cannot be null")
            if code and code != employee.code:
                existing_code = await self.queries.get_by_code(code)
                if existing_code:
                    raise ConflictException(
                        f"Employee code '{code}' already exists"
                    )
                employee.code = code

        if not employee.user_id:
            raise BadRequestException("Employee has no linked user")

        # 1. Update SSO and Local User details (only email/phone)
        sso_update_data = {}
        if "email" in update_data:
            sso_update_data["email"] = update_data["email"]
        if "phone" in update_data:
            sso_update_data["phone"] = update_data["phone"]

        if sso_update_data:
            await SSOSyncUtil.update_sso_user(
                sso_client=self.sso_client,
                user_queries=self.user_queries,
                user_commands=self.user_commands,
                user_id=employee.user_id,
                update_data=sso_update_data,
            )

        # Update denormalized email on Employee if changed
        if "email" in update_data:
            employee.email = update_data["email"]  # Can be None to clear

        # 2. Update denormalized name (Employee only, NOT SSO)
        if "name" in update_data:
            employee.name = update_data["name"]  # None clears

        # 3. Update Employee-only Fields (handle null for clearing)
        if "position" in update_data:
            employee.position = update_data["position"]  # None clears
        if "site" in update_data:
            employee.site = update_data["site"]  # None clears
        if "type" in update_data:
            employee.type = update_data["type"]  # None clears

        # Handle Supervisor & Org Change Logic
        org_unit_changed = (
            "org_unit_id" in update_data
            and update_data["org_unit_id"] != employee.org_unit_id
        )

        if "org_unit_id" in update_data:
            employee.org_unit_id = update_data["org_unit_id"]  # None clears

        # If supervisor explicitly provided, use it.
        if "supervisor_id" in update_data:
            sid = update_data["supervisor_id"]
            if sid is not None and sid == employee_id:
                raise BadRequestException("Employee cannot be their own supervisor")
            employee.supervisor_id = sid  # None clears
        elif org_unit_changed and employee.org_unit_id:
            # Org changed, but supervisor not explicitly set -> Auto-resolve
            new_supervisor = await SupervisorAssignmentUtil.resolve_supervisor(
                org_unit_queries=self.org_unit_queries,
                org_unit_id=employee.org_unit_id,
                exclude_employee_id=employee.id,
            )
            employee.supervisor_id = new_supervisor

        if "is_active" in update_data:
            employee.is_active = update_data["is_active"]

        employee.set_updated_by(updated_by)
        await self.commands.update(employee)

        employee = await self.queries.get_by_id(employee_id)
        if self.event_publisher:
            await EmployeeEventUtil.publish(self.event_publisher, "updated", employee)

        return employee
