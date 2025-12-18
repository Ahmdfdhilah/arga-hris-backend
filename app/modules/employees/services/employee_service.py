from typing import Optional, List, Tuple, Dict, Any
import logging

# Repositories
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.modules.users.rbac.repositories import RoleQueries
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.messaging.event_publisher import EventPublisher

# Schemas
from app.modules.employees.schemas import EmployeeResponse

# Use Cases
from app.modules.employees.use_cases.create_employee import CreateEmployeeUseCase
from app.modules.employees.use_cases.update_employee import UpdateEmployeeUseCase
from app.modules.employees.use_cases.delete_employee import DeleteEmployeeUseCase
from app.modules.employees.use_cases.restore_employee import RestoreEmployeeUseCase
from app.modules.employees.use_cases.get_employee import (
    GetEmployeeUseCase,
    GetEmployeeByNumberUseCase,
    GetEmployeeByEmailUseCase,
)
from app.modules.employees.use_cases.list_employees import (
    ListEmployeesUseCase,
    ListDeletedEmployeesUseCase,
)
from app.modules.employees.use_cases.list_by_org_unit import ListByOrgUnitUseCase
from app.modules.employees.use_cases.list_subordinates import ListSubordinatesUseCase

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    Facade Service for Employee operations.
    Delegates business logic to specific Use Cases.
    Handles Response Building (DTO -> Schema).
    """

    def __init__(
        self,
        queries: EmployeeQueries,
        commands: EmployeeCommands,
        org_unit_queries: OrgUnitQueries,
        user_queries: UserQueries,
        user_commands: UserCommands,
        role_queries: Optional[RoleQueries] = None,
        event_publisher: Optional[EventPublisher] = None,
    ):
        # Dependencies
        self.queries = queries
        self.commands = commands
        self.sso_client = SSOUserGRPCClient()
        self.event_publisher = event_publisher

        # Initialize Use Cases
        self.create_uc = CreateEmployeeUseCase(
            queries,
            commands,
            org_unit_queries,
            user_queries,
            user_commands,
            self.sso_client,
            event_publisher,
        )
        self.update_uc = UpdateEmployeeUseCase(
            queries,
            commands,
            org_unit_queries,
            user_queries,
            user_commands,
            self.sso_client,
            event_publisher,
        )
        self.delete_uc = DeleteEmployeeUseCase(
            queries,
            commands,
            org_unit_queries,
            user_commands,
            self.sso_client,
            event_publisher,
        )
        self.restore_uc = RestoreEmployeeUseCase(
            queries, commands, user_commands, event_publisher
        )
        self.get_uc = GetEmployeeUseCase(queries)
        self.get_by_number_uc = GetEmployeeByNumberUseCase(queries)
        self.get_by_email_uc = GetEmployeeByEmailUseCase(queries)
        self.list_uc = ListEmployeesUseCase(queries)
        self.list_deleted_uc = ListDeletedEmployeesUseCase(queries)
        self.list_by_org_uc = ListByOrgUnitUseCase(queries, org_unit_queries)
        self.list_subordinates_uc = ListSubordinatesUseCase(queries)

    # --- Write Operations ---

    async def create(
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
    ) -> EmployeeResponse:
        employee, warning = await self.create_uc.execute(
            number=number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            created_by=created_by,
            org_unit_id=org_unit_id,
            phone=phone,
            position=position,
            employee_type=employee_type,
            gender=gender,
            supervisor_id=supervisor_id,
        )
        return EmployeeResponse.model_validate(employee)

    async def update(
        self,
        employee_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> EmployeeResponse:
        employee = await self.update_uc.execute(employee_id, updated_by, update_data)
        return EmployeeResponse.model_validate(employee)

    async def delete(self, employee_id: int, deleted_by: str) -> Dict[str, Any]:
        return await self.delete_uc.execute(employee_id, deleted_by)

    async def restore(self, employee_id: int) -> EmployeeResponse:
        employee = await self.restore_uc.execute(employee_id)
        return EmployeeResponse.model_validate(employee)

    # --- Read Operations ---

    async def get(self, employee_id: int) -> EmployeeResponse:
        employee = await self.get_uc.execute(employee_id)
        return EmployeeResponse.model_validate(employee)

    async def get_by_number(self, number: str) -> Optional[EmployeeResponse]:
        employee = await self.get_by_number_uc.execute(number)
        return EmployeeResponse.model_validate(employee) if employee else None

    async def get_by_email(self, email: str) -> Optional[EmployeeResponse]:
        employee = await self.get_by_email_uc.execute(email)
        return EmployeeResponse.model_validate(employee) if employee else None

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employees, total = await self.list_uc.execute(
            page, limit, search, org_unit_id, is_active
        )
        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def list_deleted(
        self, page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employees, total = await self.list_deleted_uc.execute(page, limit, search)
        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def list_by_org_unit(
        self,
        org_unit_id: int,
        page: int = 1,
        limit: int = 10,
        include_children: bool = False,
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employees, total = await self.list_by_org_uc.execute(
            org_unit_id, page, limit, include_children
        )
        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def list_subordinates(
        self, employee_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employees, total = await self.list_subordinates_uc.execute(
            employee_id, page, limit, recursive
        )
        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination
