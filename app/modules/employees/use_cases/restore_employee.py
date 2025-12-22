from typing import Optional
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.users.users.repositories import UserCommands
from app.core.messaging.event_publisher import EventPublisher
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import NotFoundException, BadRequestException

# Utils
from app.modules.employees.utils.sso_sync import SSOSyncUtil
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class RestoreEmployeeUseCase:
    """Use Case for restoring a soft-deleted employee."""

    def __init__(
        self,
        queries: EmployeeQueries,
        commands: EmployeeCommands,
        user_commands: UserCommands,
        sso_client: SSOUserGRPCClient,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.user_commands = user_commands
        self.sso_client = sso_client
        self.event_publisher = event_publisher

    async def execute(self, employee_id: int) -> Employee:
        """
        Execute the restore employee use case.
        Restores both the employee and SSO user.
        """
        employee = await self.queries.get_by_id_with_deleted(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        if not employee.is_deleted():
            raise BadRequestException("Employee is not deleted")

        # 1. Restore SSO User
        if employee.user_id:
            await SSOSyncUtil.restore_sso_user(
                sso_client=self.sso_client,
                user_commands=self.user_commands,
                user_id=employee.user_id,
            )

        # 2. Restore Employee
        restored = await self.commands.restore(employee_id)

        # 3. Publish Event
        if self.event_publisher:
            await EmployeeEventUtil.publish(self.event_publisher, "updated", restored)

        return restored
