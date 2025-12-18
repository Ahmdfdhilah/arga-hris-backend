from typing import Optional
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.users.users.repositories import UserCommands
from app.core.messaging.event_publisher import EventPublisher
from app.core.exceptions import NotFoundException, BadRequestException

# Utils
from app.modules.employees.utils.events import EmployeeEventUtil

logger = logging.getLogger(__name__)


class RestoreEmployeeUseCase:
    """Use Case for restoring a soft-deleted employee."""

    def __init__(
        self,
        queries: EmployeeQueries,
        commands: EmployeeCommands,
        user_commands: UserCommands,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.user_commands = user_commands
        self.event_publisher = event_publisher

    async def execute(self, employee_id: int) -> Employee:
        """
        Execute the restore employee use case.
        """
        employee = await self.queries.get_by_id_with_deleted(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        if not employee.is_deleted():
            raise BadRequestException("Employee is not deleted")

        restored = await self.commands.restore(employee_id)

        if employee.user_id:
            await self.user_commands.activate(employee.user_id)

        if self.event_publisher:
            await EmployeeEventUtil.publish(self.event_publisher, "updated", restored)

        return restored
