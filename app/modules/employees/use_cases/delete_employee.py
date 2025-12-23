from typing import Optional, Dict, Any
import logging

from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserCommands
from app.core.messaging import EventPublisher
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import NotFoundException, BadRequestException

# Utils
from app.modules.employees.utils.sso_sync import SSOSyncUtil
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class DeleteEmployeeUseCase:
    """Use Case for soft-deleting an employee."""

    def __init__(
        self,
        queries: EmployeeQueries,
        commands: EmployeeCommands,
        org_unit_queries: OrgUnitQueries,
        user_commands: UserCommands,
        sso_client: SSOUserGRPCClient,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.org_unit_queries = org_unit_queries
        self.user_commands = user_commands
        self.sso_client = sso_client
        self.event_publisher = event_publisher

    async def execute(self, employee_id: int, deleted_by: str) -> Dict[str, Any]:
        """
        Execute the delete employee use case.
        """
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        is_head = await self.org_unit_queries.is_head_of_any_unit(employee_id)
        if is_head:
            raise BadRequestException(
                "Cannot delete: employee is org unit head. Reassign first."
            )

        # 1. Delete SSO User
        if employee.user_id:
            await SSOSyncUtil.delete_sso_user(
                sso_client=self.sso_client,
                user_commands=self.user_commands,
                user_id=employee.user_id,
            )

        # 2. Reassign Subordinates
        subordinates = await self.queries.get_all_by_supervisor(employee_id)
        if subordinates:
            subordinate_ids = [s.id for s in subordinates]
            await self.commands.bulk_update_supervisor(
                subordinate_ids, employee.supervisor_id, deleted_by
            )

        # 3. Delete Employee
        await self.commands.delete(employee_id, deleted_by)

        deleted = await self.queries.get_by_id_with_deleted(employee_id)

        # 5. Publish Event
        if self.event_publisher:
            await EmployeeEventUtil.publish(self.event_publisher, "deleted", deleted)

        return {"success": True}
