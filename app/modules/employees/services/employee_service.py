"""
Employee Service - Business logic for Employee operations
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import (
    EmployeeQueries,
    EmployeeCommands,
    EmployeeFilters,
    PaginationParams,
)
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.employees.schemas import EmployeeResponse
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.modules.users.rbac.repositories import RoleQueries
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    BadRequestException,
)
from app.core.messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class EmployeeService:
    """Unified service for all employee operations"""

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
        self.queries = queries
        self.commands = commands
        self.org_unit_queries = org_unit_queries
        self.user_queries = user_queries
        self.user_commands = user_commands
        self.role_queries = role_queries
        self.event_publisher = event_publisher
        self.sso_client = SSOUserGRPCClient()

    def _to_event_data(self, employee: Employee) -> Dict[str, Any]:
        data = {
            "id": employee.id,
            "user_id": employee.user_id,
            "number": employee.number,
            "position": employee.position,
            "type": employee.type,
            "org_unit_id": employee.org_unit_id,
            "supervisor_id": employee.supervisor_id,
            "is_active": employee.is_active,
        }
        if employee.user:
            data["user"] = {
                "id": employee.user.id,  # SSO UUID
                "name": employee.user.name,
                "email": employee.user.email,
                "phone": employee.user.phone,
                "gender": employee.user.gender,
            }
        return data

    async def _publish_event(self, event_type: str, employee: Employee) -> None:
        if not self.event_publisher:
            return
        try:
            data = self._to_event_data(employee)
            if event_type == "created":
                await self.event_publisher.publish_employee_created(employee.id, data)
            elif event_type == "updated":
                await self.event_publisher.publish_employee_updated(employee.id, data)
            elif event_type == "deleted":
                await self.event_publisher.publish_employee_deleted(employee.id, data)
        except Exception as e:
            logger.warning(f"Failed to publish employee.{event_type}: {e}")

    async def _auto_assign_supervisor(self, org_unit_id: int) -> Optional[int]:
        org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
        if not org_unit:
            return None
        if org_unit.head_id:
            return org_unit.head_id
        if org_unit.parent_id:
            parent = await self.org_unit_queries.get_by_id(org_unit.parent_id)
            if parent and parent.head_id:
                return parent.head_id
        return None

    async def get(self, employee_id: int) -> EmployeeResponse:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        return EmployeeResponse.model_validate(employee)

    async def get_by_user_id(self, user_id: str) -> Optional[EmployeeResponse]:
        employee = await self.queries.get_by_user_id(user_id)
        return EmployeeResponse.model_validate(employee) if employee else None

    async def get_by_email(self, email: str) -> Optional[EmployeeResponse]:
        employee = await self.queries.get_by_email(email)
        return EmployeeResponse.model_validate(employee) if employee else None

    async def get_by_number(self, number: str) -> Optional[EmployeeResponse]:
        employee = await self.queries.get_by_number(number)
        return EmployeeResponse.model_validate(employee) if employee else None

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(
            org_unit_id=org_unit_id, is_active=is_active, search=search
        )
        employees, pagination = await self.queries.list(params, filters)
        return [
            EmployeeResponse.model_validate(e) for e in employees
        ], pagination.to_dict()

    async def list_by_org_unit(
        self,
        org_unit_id: int,
        page: int = 1,
        limit: int = 10,
        include_children: bool = False,
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(f"OrgUnit with ID {org_unit_id} not found")
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.queries.get_by_org_unit(
            org_unit_id, include_children, params
        )
        return [
            EmployeeResponse.model_validate(e) for e in employees
        ], pagination.to_dict()

    async def list_subordinates(
        self, employee_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.queries.get_subordinates(
            employee_id, recursive, params
        )
        return [
            EmployeeResponse.model_validate(e) for e in employees
        ], pagination.to_dict()

    async def list_deleted(
        self, page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        params = PaginationParams(page=page, limit=limit)
        employees, pagination = await self.queries.list_deleted(params, search)
        return [
            EmployeeResponse.model_validate(e) for e in employees
        ], pagination.to_dict()

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
    ) -> Tuple[EmployeeResponse, Optional[str], Optional[List[str]]]:
        warnings = []
        full_name = f"{first_name} {last_name}"
        temp_password = None

        existing_number = await self.queries.get_by_number(number)
        if existing_number:
            raise ConflictException(f"Employee number '{number}' already exists")

        if org_unit_id:
            org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
            if not org_unit:
                raise BadRequestException(f"OrgUnit with ID {org_unit_id} not found")

        existing_sso = await self.sso_client.get_user_by_email(email)

        if existing_sso:
            sso_user = existing_sso
            local_user = await self.user_queries.get_by_id(sso_user["id"])
            if local_user:
                existing_emp = await self.queries.get_by_user_id(local_user.id)
                if existing_emp:
                    warnings.append("Employee already registered for this account")
                    return EmployeeResponse.model_validate(existing_emp), None, warnings
        else:
            create_result = await self.sso_client.create_user(
                email=email, name=full_name, phone=phone, gender=gender, role="user"
            )
            if not create_result.get("success"):
                raise ConflictException(
                    f"Failed to create SSO user: {create_result.get('error')}"
                )
            sso_user = create_result["user"]
            temp_password = create_result.get("temporary_password")

        local_user = await self.user_queries.get_by_id(sso_user["id"])
        if not local_user:
            local_user = await self.user_commands.create(
                {
                    "id": sso_user["id"],  # SSO UUID as primary key
                    "name": sso_user.get("name", full_name),
                    "email": sso_user.get("email", email),
                    "phone": sso_user.get("phone", phone),
                    "gender": sso_user.get("gender", gender),
                    "avatar_path": sso_user.get("avatar_path"),
                    "is_active": True,
                    "synced_at": datetime.utcnow(),
                }
            )
        else:
            await self.user_commands.update(
                local_user.id,
                {
                    "name": sso_user.get("name", full_name),
                    "email": sso_user.get("email", email),
                    "phone": sso_user.get("phone", phone),
                    "gender": sso_user.get("gender", gender),
                    "synced_at": datetime.utcnow(),
                },
            )
            local_user = await self.user_queries.get_by_id(local_user.id)

        auto_supervisor = supervisor_id
        if not auto_supervisor and org_unit_id:
            auto_supervisor = await self._auto_assign_supervisor(org_unit_id)

        employee = Employee(
            user_id=local_user.id,
            number=number,
            position=position,
            type=employee_type,
            org_unit_id=org_unit_id,
            supervisor_id=auto_supervisor,
            is_active=True,
        )
        employee.set_created_by(created_by)

        created = await self.commands.create(employee)
        created = await self.queries.get_by_id(created.id)

        await self._publish_event("created", created)

        return (
            EmployeeResponse.model_validate(created),
            temp_password,
            warnings if warnings else None,
        )

    async def update(
        self,
        employee_id: int,
        updated_by: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        supervisor_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[EmployeeResponse, Optional[List[str]]]:
        warnings = []

        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        if not employee.user_id:
            raise BadRequestException("Employee has no linked user")

        local_user = await self.user_queries.get_by_id(employee.user_id)
        if not local_user:
            raise NotFoundException(f"User with ID {employee.user_id} not found")

        full_name = None
        if first_name or last_name:
            existing_name = local_user.name or ""
            parts = existing_name.split(" ", 1)
            fn = first_name if first_name else (parts[0] if len(parts) > 0 else "")
            ln = last_name if last_name else (parts[1] if len(parts) > 1 else "")
            full_name = f"{fn} {ln}".strip()

        if local_user.id and (full_name or phone or gender):
            try:
                sso_result = await self.sso_client.update_user(
                    user_id=local_user.id, name=full_name, phone=phone, gender=gender
                )
                if sso_result.get("success"):
                    sso_user = sso_result.get("user", {})
                    update_data = {"synced_at": datetime.utcnow()}
                    if full_name:
                        update_data["name"] = sso_user.get("name", full_name)
                    if phone:
                        update_data["phone"] = sso_user.get("phone", phone)
                    if gender:
                        update_data["gender"] = sso_user.get("gender", gender)
                    await self.user_commands.update(local_user.id, update_data)
                else:
                    warnings.append(f"SSO sync failed: {sso_result.get('error')}")
            except Exception as e:
                warnings.append(f"SSO sync failed: {e}")

        if position is not None:
            employee.position = position
        if employee_type is not None:
            employee.type = employee_type
        if org_unit_id is not None:
            employee.org_unit_id = org_unit_id
        if supervisor_id is not None:
            if supervisor_id == employee_id:
                raise BadRequestException("Employee cannot be their own supervisor")
            employee.supervisor_id = supervisor_id
        if is_active is not None:
            employee.is_active = is_active

        employee.set_updated_by(updated_by)
        await self.commands.update(employee)

        updated = await self.queries.get_by_id(employee_id)
        await self._publish_event("updated", updated)

        return EmployeeResponse.model_validate(updated), warnings if warnings else None

    async def delete(self, employee_id: int, deleted_by: str) -> Dict[str, Any]:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        warnings = []

        is_head = await self.org_unit_queries.is_head_of_any_unit(employee_id)
        if is_head:
            raise BadRequestException(
                "Cannot delete: employee is org unit head. Reassign first."
            )

        local_user = None
        if employee.user_id:
            local_user = await self.user_queries.get_by_id(employee.user_id)

        if local_user and local_user.id:
            try:
                result = await self.sso_client.delete_user(local_user.id)
                if not result.get("success"):
                    warnings.append(f"SSO deactivate failed: {result.get('error')}")
            except Exception as e:
                warnings.append(f"SSO deactivate failed: {e}")

        subordinates = await self.queries.get_all_by_supervisor(employee_id)
        if subordinates:
            subordinate_ids = [s.id for s in subordinates]
            await self.commands.bulk_update_supervisor(
                subordinate_ids, employee.supervisor_id, deleted_by
            )

        await self.commands.delete(employee_id, deleted_by)

        if local_user:
            await self.user_commands.deactivate(local_user.id)

        deleted = await self.queries.get_by_id_with_deleted(employee_id)
        await self._publish_event("deleted", deleted)

        return {"success": True, "warnings": warnings if warnings else None}

    async def restore(self, employee_id: int) -> EmployeeResponse:
        employee = await self.queries.get_by_id_with_deleted(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        if not employee.is_deleted():
            raise BadRequestException("Employee is not deleted")

        restored = await self.commands.restore(employee_id)

        if employee.user_id:
            await self.user_commands.activate(employee.user_id)

        await self._publish_event("updated", restored)
        return EmployeeResponse.model_validate(restored)
