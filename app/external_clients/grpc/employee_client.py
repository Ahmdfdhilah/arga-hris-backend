import grpc
from typing import Optional, Dict, Any
from app.external_clients.grpc.base_client import BaseGRPCClient
from proto.employee import employee_pb2, employee_pb2_grpc
from proto.common import common_pb2
from app.modules.employees.schemas.responses import (
    EmployeeResponse,
)


class EmployeeGRPCClient(BaseGRPCClient):
 
    def __init__(self):
        super().__init__("EmployeeService")

    async def get_stub(self) -> employee_pb2_grpc.EmployeeServiceStub:
        channel = await self.get_channel()
        return employee_pb2_grpc.EmployeeServiceStub(channel)

    async def get_employee(self, employee_id: int) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            request = employee_pb2.GetEmployeeRequest(employee_id=employee_id)
            response = await stub.GetEmployee(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_employee_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            stub = await self.get_stub()
            request = employee_pb2.GetEmployeeByEmailRequest(employee_email=email)
            response = await stub.GetEmployeeByEmail(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def get_employee_by_number(self, employee_number: str) -> Optional[Dict[str, Any]]:
        try:
            stub = await self.get_stub()
            request = employee_pb2.GetEmployeeByNumberRequest(
                employee_number=employee_number
            )
            response = await stub.GetEmployeeByNumber(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def list_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        include_details: Optional[bool] = None
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)

            request = employee_pb2.ListEmployeesRequest(
                pagination=pagination,
                search=search,
                employee_org_unit_id=org_unit_id,
                is_active=is_active,
                include_details=include_details
            )

            response = await stub.ListEmployees(request)
            return {
                "employees": [
                    self._employee_to_dict(emp) for emp in response.employees
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_employee_subordinates(
        self, employee_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)

            request = employee_pb2.GetSubordinatesRequest(
                employee_supervisor_id=employee_id,
                recursive=recursive,
                pagination=pagination
            )

            response = await stub.GetEmployeeSubordinates(request)
            return {
                "employees": [
                    self._employee_to_dict(emp) for emp in response.employees
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_employees_by_org_unit(
        self, org_unit_id: int, page: int = 1, limit: int = 10, include_children: bool = False
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)

            request = employee_pb2.GetEmployeesByOrgUnitRequest(
                employee_org_unit_id=org_unit_id,
                include_children=include_children,
                pagination=pagination
            )

            response = await stub.GetEmployeesByOrgUnit(request)
            return {
                "employees": [
                    self._employee_to_dict(emp) for emp in response.employees
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def create_employee(
        self,
        employee_number: str,
        employee_name: str,
        employee_email: str,
        employee_phone: str,
        employee_position: str,
        created_by: int,
        employee_org_unit_id: Optional[int] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        employee_supervisor_id: Optional[int] = None,
        employee_metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()

            request_params = {
                "employee_number": employee_number,
                "employee_name": employee_name,
                "employee_email": employee_email,
                "employee_phone": employee_phone,
                "employee_position": employee_position,
                "created_by": created_by,
            }

            if employee_org_unit_id is not None:
                request_params["employee_org_unit_id"] = employee_org_unit_id

            if employee_type:
                request_params["employee_type"] = employee_type

            if employee_gender:
                request_params["employee_gender"] = employee_gender

            if employee_supervisor_id:
                request_params["employee_supervisor_id"] = employee_supervisor_id

            if employee_metadata:
                request_params["employee_metadata"] = employee_metadata

            request = employee_pb2.CreateEmployeeRequest(**request_params)
            response = await stub.CreateEmployee(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def update_employee(
        self,
        employee_id: int,
        updated_by: int,
        employee_name: Optional[str] = None,
        employee_email: Optional[str] = None,
        employee_phone: Optional[str] = None,
        employee_position: Optional[str] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        employee_org_unit_id: Optional[int] = None,
        employee_supervisor_id: Optional[int] = None,
        employee_metadata: Optional[Dict[str, str]] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        try:
            stub = await self.get_stub()

            request = employee_pb2.UpdateEmployeeRequest(
                employee_id=employee_id,
                updated_by=updated_by,
                employee_name=employee_name,
                employee_email=employee_email,
                employee_phone=employee_phone,
                employee_position=employee_position,
                employee_type=employee_type,
                employee_gender=employee_gender,
                employee_org_unit_id=employee_org_unit_id,
                employee_supervisor_id=employee_supervisor_id,
                employee_metadata=employee_metadata,
                is_active=is_active
            )
            response = await stub.UpdateEmployee(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    def _employee_to_dict(self, employee: employee_pb2.Employee) -> Dict[str, Any]:
        """Convert gRPC Employee message to dict using Pydantic schema for validation"""
        data = {
            "id": employee.employee_id,
            "employee_number": employee.employee_number,
            "name": employee.employee_name,
            "email": employee.employee_email or None,
            "phone": employee.employee_phone or None,
            "position": employee.employee_position or None,
            "employee_type": employee.employee_type or None,
            "employee_gender": employee.employee_gender or None,
            "org_unit_id": employee.employee_org_unit_id or None,
            "supervisor_id": employee.employee_supervisor_id or None,
            "employee_metadata": dict(employee.employee_metadata) if employee.employee_metadata else None,
            "is_active": employee.is_active,
            "created_at": employee.created_at.ToJsonString() if employee.HasField("created_at") else None,
            "updated_at": employee.updated_at.ToJsonString() if employee.HasField("updated_at") else None,
            "created_by": employee.created_by if employee.created_by else None,
            "updated_by": employee.updated_by if employee.updated_by else None,
            "deleted_at": employee.deleted_at.ToJsonString() if employee.HasField("deleted_at") else None,
            "deleted_by": employee.deleted_by if employee.deleted_by else None,
        }

        if employee.HasField("org_unit"):
            data["org_unit"] = {
                "id": employee.org_unit.org_unit_id,
                "code": employee.org_unit.org_unit_code,
                "name": employee.org_unit.org_unit_name,
                "type": employee.org_unit.org_unit_type,
            }

        if employee.HasField("supervisor"):
            data["supervisor"] = {
                "id": employee.supervisor.employee_id,
                "employee_number": employee.supervisor.employee_number,
                "name": employee.supervisor.employee_name,
                "position": employee.supervisor.employee_position or None,
            }

        # Validate using Pydantic schema and return as dict
        validated = EmployeeResponse.model_validate(data)
        return validated.model_dump()

    async def soft_delete_employee(
        self,
        employee_id: int,
        deleted_by_user_id: int
    ) -> Dict[str, Any]:
        """Soft delete employee via gRPC"""
        try:
            stub = await self.get_stub()
            request = employee_pb2.SoftDeleteEmployeeRequest(
                employee_id=employee_id,
                deleted_by_user_id=deleted_by_user_id
            )
            response = await stub.SoftDeleteEmployee(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def restore_employee(self, employee_id: int) -> Dict[str, Any]:
        """Restore soft-deleted employee via gRPC"""
        try:
            stub = await self.get_stub()
            request = employee_pb2.RestoreEmployeeRequest(
                employee_id=employee_id
            )
            response = await stub.RestoreEmployee(request)
            return self._employee_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def list_deleted_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List deleted employees via gRPC"""
        try:
            stub = await self.get_stub()
            pagination = common_pb2.Pagination(page=page, limit=limit)
            request = employee_pb2.ListDeletedEmployeesRequest(
                pagination=pagination,
                search=search,
            )
            response = await stub.ListDeletedEmployees(request)
            return {
                "employees": [
                    self._employee_to_dict(emp) for emp in response.employees
                ],
                "pagination": {
                    "page": response.pagination_info.page,
                    "limit": response.pagination_info.limit,
                    "total_items": response.pagination_info.total_items,
                    "total_pages": response.pagination_info.total_pages,
                },
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)
