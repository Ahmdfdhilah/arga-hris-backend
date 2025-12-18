"""
Employee Service - Business logic for Employee operations
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import logging

from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
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
        skip = (page - 1) * limit

        employees = await self.queries.list(
            org_unit_id=org_unit_id,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count(
            org_unit_id=org_unit_id,
            is_active=is_active,
            search=search,
        )

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
        org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(f"OrgUnit with ID {org_unit_id} not found")

        skip = (page - 1) * limit

        employees = await self.queries.get_by_org_unit(
            org_unit_id=org_unit_id,
            include_children=include_children,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count_by_org_unit(
            org_unit_id=org_unit_id,
            include_children=include_children,
        )

        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def list_subordinates(
        self, employee_id: int, page: int = 1, limit: int = 10, recursive: bool = False
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        skip = (page - 1) * limit

        employees = await self.queries.get_subordinates(
            supervisor_id=employee_id,
            recursive=recursive,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count_subordinates(
            supervisor_id=employee_id,
            recursive=recursive,
        )

        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

    async def list_deleted(
        self, page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Tuple[List[EmployeeResponse], Dict[str, Any]]:
        skip = (page - 1) * limit

        employees = await self.queries.list_deleted(
            search=search,
            skip=skip,
            limit=limit,
        )
        total = await self.queries.count_deleted(search=search)

        items = [EmployeeResponse.model_validate(e) for e in employees]
        pagination = {"page": page, "limit": limit, "total_items": total}
        return items, pagination

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
        full_name = f"{first_name} {last_name}"

        existing_number = await self.queries.get_by_number(number)
        if existing_number:
            raise ConflictException(f"Employee number '{number}' already exists")

        if org_unit_id:
            org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
            if not org_unit:
                raise BadRequestException(f"OrgUnit with ID {org_unit_id} not found")

        # 1. Create SSO User (Strict Sync)
        create_result = await self.sso_client.create_user(
            email=email, name=full_name, phone=phone, gender=gender, role="user"
        )
        if not create_result.get("success"):
            # Check if user already exists
            existing_sso = await self.sso_client.get_user_by_email(email)
            if existing_sso:
                # User exists in SSO, proceed to link
                sso_user = existing_sso
            else:
                # Genuine failure
                raise ConflictException(
                    f"Failed to create SSO user: {create_result.get('error')}"
                )
        else:
            sso_user = create_result["user"]

        # 2. Sync Local User
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
            # Check if already linked to another employee
            existing_emp = await self.queries.get_by_user_id(local_user.id)
            if existing_emp:
                raise ConflictException(
                    f"User {email} is already linked to employee {existing_emp.number}"
                )
            # Update local user data
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

        # 3. Auto-assign Supervisor if needed
        auto_supervisor = supervisor_id
        if not auto_supervisor and org_unit_id:
            auto_supervisor = await self._auto_assign_supervisor(org_unit_id)

        # 4. Create Employee
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

        # 5. Publish Event
        await self._publish_event("created", created)

        return EmployeeResponse.model_validate(created)

    async def update(
        self,
        employee_id: int,
        updated_by: str,
        update_data: Dict[str, Any],
    ) -> EmployeeResponse:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        # 0. Check Number Uniqueness
        if "number" in update_data:
            number = update_data["number"]
            # number is Optional in UpdateRequest, so it could be None if someone explicitly sends null,
            # though validate_number usually prevents empty strings.
            # But uniqueness check only applies if it's a valid string.
            if number and number != employee.number:
                existing_number = await self.queries.get_by_number(number)
                if existing_number:
                    raise ConflictException(
                        f"Employee number '{number}' already exists"
                    )
                employee.number = number

        if not employee.user_id:
            raise BadRequestException("Employee has no linked user")

        local_user = await self.user_queries.get_by_id(employee.user_id)
        if not local_user:
            raise NotFoundException(f"User with ID {employee.user_id} not found")

        # 1. Prepare SSO Update Data
        sso_update_fields = {}
        full_name = None

        # Handle Name Construction
        # If either first or last name is updated, we need to reconstruct full name
        if "first_name" in update_data or "last_name" in update_data:
            existing_name = local_user.name or ""
            parts = existing_name.split(" ", 1)
            # Default to existing parts
            fn = parts[0] if len(parts) > 0 else ""
            ln = parts[1] if len(parts) > 1 else ""

            # Override with updates (if key exists, value is used even if None effectively clearing it)
            if "first_name" in update_data:
                fn = update_data["first_name"] or ""
            if "last_name" in update_data:
                ln = update_data["last_name"] or ""

            full_name = f"{fn} {ln}".strip()
            sso_update_fields["name"] = full_name

        if "email" in update_data:
            sso_update_fields["email"] = update_data["email"]
        if "phone" in update_data:
            sso_update_fields["phone"] = update_data["phone"]
        if "gender" in update_data:
            sso_update_fields["gender"] = update_data["gender"]

        # 2. Update SSO User (Strict Sync)
        if sso_update_fields:
            sso_result = await self.sso_client.update_user(
                user_id=local_user.id, **sso_update_fields
            )
            if not sso_result.get("success"):
                raise ConflictException(
                    f"Failed to update SSO user: {sso_result.get('error')}"
                )

            # 3. Update Local User
            sso_user = sso_result.get("user", {})
            local_user_update = {"synced_at": datetime.utcnow()}

            # Map back fields from SSO response to ensure consistency
            if "name" in sso_update_fields:
                local_user_update["name"] = sso_user.get(
                    "name", sso_update_fields["name"]
                )
            if "email" in sso_update_fields:
                local_user_update["email"] = sso_user.get(
                    "email", sso_update_fields["email"]
                )
            if "phone" in sso_update_fields:
                local_user_update["phone"] = sso_user.get(
                    "phone", sso_update_fields["phone"]
                )
            if "gender" in sso_update_fields:
                local_user_update["gender"] = sso_user.get(
                    "gender", sso_update_fields["gender"]
                )

            await self.user_commands.update(local_user.id, local_user_update)

        # 4. Update Employee
        if "position" in update_data:
            employee.position = update_data["position"]
        if "type" in update_data:
            employee.type = update_data["type"]
        if "org_unit_id" in update_data:
            employee.org_unit_id = update_data["org_unit_id"]
        if "supervisor_id" in update_data:
            sid = update_data["supervisor_id"]
            if sid is not None and sid == employee_id:
                raise BadRequestException("Employee cannot be their own supervisor")
            employee.supervisor_id = sid
        if "is_active" in update_data:
            employee.is_active = update_data["is_active"]

        employee.set_updated_by(updated_by)
        await self.commands.update(employee)

        employee.set_updated_by(updated_by)
        await self.commands.update(employee)

        updated = await self.queries.get_by_id(employee_id)

        # 4. Publish Event
        await self._publish_event("updated", updated)

        return EmployeeResponse.model_validate(updated)

    async def delete(self, employee_id: int, deleted_by: str) -> Dict[str, Any]:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        is_head = await self.org_unit_queries.is_head_of_any_unit(employee_id)
        if is_head:
            raise BadRequestException(
                "Cannot delete: employee is org unit head. Reassign first."
            )

        local_user = None
        if employee.user_id:
            local_user = await self.user_queries.get_by_id(employee.user_id)

        # 1. Delete SSO User (Strict Sync)
        if local_user and local_user.id:
            result = await self.sso_client.delete_user(local_user.id)
            if not result.get("success"):
                raise ConflictException(
                    f"Failed to delete SSO user: {result.get('error')}"
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

        # 4. Deactivate Local User
        if local_user:
            await self.user_commands.deactivate(local_user.id)

        deleted = await self.queries.get_by_id_with_deleted(employee_id)

        # 5. Publish Event
        await self._publish_event("deleted", deleted)

        return {"success": True}

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
