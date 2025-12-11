from typing import Optional, Dict, Any, List
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.modules.employees.schemas import EmployeeResponse
from app.modules.users.users.repositories.user_repository import UserRepository


class EmployeeService:
    def __init__(self, grpc_client: EmployeeGRPCClient, user_repo: UserRepository):
        self.grpc_client = grpc_client
        self.user_repo = user_repo

    async def _enrich_employee_with_user_id(self, employee_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich employee data with user_id"""
        employee_id = employee_dict.get("id")
        if employee_id:
            user = await self.user_repo.get_by_employee_id(employee_id)
            if user:
                employee_dict["user_id"] = user.id
        return employee_dict

    async def _enrich_employees_with_user_ids(self, employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich multiple employees with user_ids"""
        for employee in employees:
            await self._enrich_employee_with_user_id(employee)
        return employees

    async def get_employee(self, employee_id: int) -> EmployeeResponse:
        """Get employee by ID"""
        data = await self.grpc_client.get_employee(employee_id)
        data = await self._enrich_employee_with_user_id(data)
        return EmployeeResponse.model_validate(data)

    async def get_employee_by_email(self, email: str) -> Optional[EmployeeResponse]:
        """Get employee by email"""
        data = await self.grpc_client.get_employee_by_email(email)
        if data is None:
            return None
        data = await self._enrich_employee_with_user_id(data)
        return EmployeeResponse.model_validate(data)

    async def get_employee_by_number(self, employee_number: str) -> Optional[EmployeeResponse]:
        """Get employee by employee number"""
        data = await self.grpc_client.get_employee_by_number(employee_number)
        if data is None:
            return None
        data = await self._enrich_employee_with_user_id(data)
        return EmployeeResponse.model_validate(data)

    async def list_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        include_details: Optional[bool] = None
    ) -> tuple[List[EmployeeResponse], Dict[str, Any]]:
        """List employees with filters and pagination"""
        data = await self.grpc_client.list_employees(
            page, limit, search, org_unit_id, is_active, include_details
        )
        employees_data = data["employees"]
        employees_data = await self._enrich_employees_with_user_ids(employees_data)

        items = [EmployeeResponse.model_validate(emp) for emp in employees_data]
        pagination = data["pagination"]
        return items, pagination

    async def get_employee_subordinates(
        self, employee_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> tuple[List[EmployeeResponse], Dict[str, Any]]:
        """Get employee subordinates"""
        data = await self.grpc_client.get_employee_subordinates(
            employee_id, page, limit, recursive
        )
        employees_data = data["employees"]
        employees_data = await self._enrich_employees_with_user_ids(employees_data)

        items = [EmployeeResponse.model_validate(emp) for emp in employees_data]
        pagination = data["pagination"]
        return items, pagination

    async def get_employees_by_org_unit(
        self, org_unit_id: int, page: int = 1, limit: int = 10, include_children: bool = False
    ) -> tuple[List[EmployeeResponse], Dict[str, Any]]:
        """Get employees by organization unit"""
        data = await self.grpc_client.get_employees_by_org_unit(
            org_unit_id, page, limit, include_children
        )
        employees_data = data["employees"]
        employees_data = await self._enrich_employees_with_user_ids(employees_data)

        items = [EmployeeResponse.model_validate(emp) for emp in employees_data]
        pagination = data["pagination"]
        return items, pagination

    async def create_employee(
        self,
        number: str,
        name: str,
        email: str,
        phone: str,
        position: str,
        org_unit_id: int,
        created_by: int,
        supervisor_id: Optional[int] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
    ) -> EmployeeResponse:
        """Create new employee via gRPC"""
        data = await self.grpc_client.create_employee(
            employee_number=number,
            employee_name=name,
            employee_email=email,
            employee_phone=phone,
            employee_position=position,
            employee_type=employee_type,
            employee_gender=employee_gender,
            employee_org_unit_id=org_unit_id,
            created_by=created_by,
            employee_supervisor_id=supervisor_id,
        )
        data = await self._enrich_employee_with_user_id(data)
        return EmployeeResponse.model_validate(data)

    async def update_employee(
        self,
        employee_id: int,
        updated_by: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        supervisor_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> EmployeeResponse:
        """Update employee via gRPC"""
        data = await self.grpc_client.update_employee(
            employee_id=employee_id,
            updated_by=updated_by,
            employee_name=name,
            employee_email=email,
            employee_phone=phone,
            employee_position=position,
            employee_type=employee_type,
            employee_gender=employee_gender,
            employee_org_unit_id=org_unit_id,
            employee_supervisor_id=supervisor_id,
            is_active=is_active,
        )
        data = await self._enrich_employee_with_user_id(data)
        return EmployeeResponse.model_validate(data)
