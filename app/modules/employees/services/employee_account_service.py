"""
Employee Account Service - SSO-First Flow (Refactored for User/Employee separation)

Orchestrates operations between:
- SSO (gRPC) - User authentication/profile (MASTER for profile data)
- Local User table - Profile data replica
- Local Employee table - Employment data (MASTER)

Flow for create:
1. Create SSO user via gRPC (sync, get response)
2. Create local User from SSO response (immediate sync)
3. Create Employee linked to User

Follows Master Data Sync Rules:
- Write to Master via gRPC, await response
- Caller syncs locally from response (not event)
- Events published for other services
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.modules.employees.repositories.employee_repository import EmployeeRepository
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.models.employee import Employee
from app.modules.users.users.models.user import User
from app.external_clients.grpc.sso_client import SSOUserGRPCClient
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException,
)
from app.modules.employees.schemas import (
    EmployeeResponse,
    EmployeeAccountData,
    EmployeeAccountUpdateData,
    EmployeeAccountListItem,
)
from app.core.messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class EmployeeAccountService:
    """
    Service untuk operasi unified employee account.
    
    Handles full lifecycle:
    - Create: SSO → local User → Employee
    - Update: Employee + sync to SSO
    - Delete: Deactivate SSO + soft delete Employee
    """

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_unit_repo: OrgUnitRepository,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.employee_repo = employee_repo
        self.org_unit_repo = org_unit_repo
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.event_publisher = event_publisher
        self.sso_client = SSOUserGRPCClient()

    async def create_employee_with_account(
        self,
        number: str,
        first_name: str,
        last_name: str,
        email: str,
        created_by: int,
        org_unit_id: Optional[int] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        gender: Optional[str] = None,
        supervisor_id: Optional[int] = None,
    ) -> EmployeeAccountData:
        """
        Create employee with linked SSO user and local User.
        
        Flow:
        1. Check/create SSO user (Master for profile)
        2. Create local User (sync from SSO response)
        3. Create Employee linked to User
        """
        warnings = []
        full_name = f"{first_name} {last_name}"
        temp_password = None

        # === STEP 1: Create/Get SSO User ===
        logger.info(f"Step 1: Check/create SSO user for email: {email}")
        
        existing_sso = await self.sso_client.get_user_by_email(email)
        
        if existing_sso:
            sso_user = existing_sso
            logger.info(f"SSO user exists: {sso_user['id']}")
            
            # Check if already has employee
            existing_local_user = await self.user_repo.get_by_sso_id(sso_user["id"])
            if existing_local_user:
                existing_emp = await self.employee_repo.get_by_user_id(existing_local_user.id)
                if existing_emp:
                    warnings.append("Employee sudah terdaftar sebelumnya")
                    return EmployeeAccountData(
                        employee=EmployeeResponse.model_validate(existing_emp),
                        temporary_password=None,
                        warnings=warnings,
                    )
        else:
            # Create SSO user (synchronous call)
            create_result = await self.sso_client.create_user(
                email=email,
                name=full_name,
                phone=phone,
                gender=gender,
                role="user",
            )
            
            if not create_result.get("success"):
                error = create_result.get("error", "Unknown error")
                raise ConflictException(f"Gagal membuat user di SSO: {error}")
            
            sso_user = create_result["user"]
            temp_password = create_result.get("temporary_password")
            logger.info(f"SSO user created: {sso_user['id']}")

        # === STEP 2: Create Local User (immediate sync from response) ===
        logger.info(f"Step 2: Sync local user from SSO response")
        
        local_user = await self.user_repo.get_by_sso_id(sso_user["id"])
        
        if not local_user:
            # Create local user with profile data from SSO response
            local_user = await self.user_repo.create({
                "sso_id": sso_user["id"],
                "name": sso_user.get("name", full_name),
                "email": sso_user.get("email", email),
                "phone": sso_user.get("phone", phone),
                "gender": sso_user.get("gender", gender),
                "avatar_path": sso_user.get("avatar_path"),
                "is_active": True,
                "synced_at": datetime.utcnow(),
            })
            logger.info(f"Local user created: {local_user.id}")
        else:
            # Update existing local user with fresh SSO data
            await self.user_repo.update(local_user.id, {
                "name": sso_user.get("name", full_name),
                "email": sso_user.get("email", email),
                "phone": sso_user.get("phone", phone),
                "gender": sso_user.get("gender", gender),
                "synced_at": datetime.utcnow(),
            })
            local_user = await self.user_repo.get(local_user.id)
            logger.info(f"Local user updated: {local_user.id}")

        # === STEP 3: Create Employee ===
        logger.info(f"Step 3: Create employee linked to user {local_user.id}")
        
        # Check if employee already exists for this user
        existing_emp = await self.employee_repo.get_by_user_id(local_user.id)
        if existing_emp:
            warnings.append("Employee sudah ada untuk user ini")
            return EmployeeAccountData(
                employee=EmployeeResponse.model_validate(existing_emp),
                temporary_password=temp_password,
                warnings=warnings,
            )
        
        # Check employee number uniqueness
        existing_number = await self.employee_repo.get_by_number(number)
        if existing_number:
            raise ConflictException(f"Employee number '{number}' sudah digunakan")

        # Validate org unit
        if org_unit_id:
            org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
            if not org_unit:
                raise ValidationException(f"Organization unit dengan ID {org_unit_id} tidak ditemukan")

        # Auto-assign supervisor from org unit head
        auto_supervisor_id = supervisor_id
        if not auto_supervisor_id and org_unit_id:
            org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
            if org_unit and org_unit.head_id:
                auto_supervisor_id = org_unit.head_id

        # Create employee
        employee = Employee(
            user_id=local_user.id,
            number=number,
            position=position,
            type=employee_type,
            org_unit_id=org_unit_id,
            supervisor_id=auto_supervisor_id,
            is_active=True
        )
        employee.set_created_by(created_by)
        
        created_emp = await self.employee_repo.create(employee)
        
        # Reload with relationships
        created_emp = await self.employee_repo.get_by_id(created_emp.id)
        logger.info(f"Employee created: {created_emp.id}")

        # === STEP 4: Assign default role ===
        await self._assign_default_role(local_user.id, created_emp.id)

        # === STEP 5: Publish event (for other services) ===
        await self._publish_employee_event("created", created_emp)

        return EmployeeAccountData(
            employee=EmployeeResponse.model_validate(created_emp),
            temporary_password=temp_password,
            warnings=warnings if warnings else None,
        )

    async def update_employee_with_account(
        self,
        employee_id: int,
        updated_by: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        supervisor_id: Optional[int] = None,
    ) -> EmployeeAccountUpdateData:
        """
        Update employee and sync profile to SSO.
        
        Flow:
        1. Update SSO user (Master) via gRPC
        2. Update local User from response
        3. Update Employee employment data
        """
        warnings = []

        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee dengan ID {employee_id} tidak ditemukan")

        if not employee.user_id:
            raise ValidationException("Employee tidak memiliki user terhubung")

        local_user = await self.user_repo.get(employee.user_id)
        if not local_user:
            raise NotFoundException(f"User dengan ID {employee.user_id} tidak ditemukan")

        # Build full name if provided
        full_name = None
        if first_name or last_name:
            existing_name = local_user.name or ""
            parts = existing_name.split(" ", 1)
            existing_first = parts[0] if len(parts) > 0 else ""
            existing_last = parts[1] if len(parts) > 1 else ""
            
            fn = first_name if first_name else existing_first
            ln = last_name if last_name else existing_last
            full_name = f"{fn} {ln}"

        # === STEP 1: Update SSO User (Master) ===
        if local_user.sso_id and (full_name or phone or gender):
            try:
                sso_result = await self.sso_client.update_user(
                    user_id=local_user.sso_id,
                    name=full_name,
                    phone=phone,
                    gender=gender,
                )
                if sso_result.get("success"):
                    logger.info(f"SSO user updated: {local_user.sso_id}")
                    
                    # === STEP 2: Update local User from response ===
                    sso_user = sso_result.get("user", {})
                    await self.user_repo.update(local_user.id, {
                        "name": sso_user.get("name", full_name) if full_name else None,
                        "phone": sso_user.get("phone", phone) if phone else None,
                        "gender": sso_user.get("gender", gender) if gender else None,
                        "synced_at": datetime.utcnow(),
                    })
                else:
                    warnings.append(f"SSO update failed: {sso_result.get('error')}")
            except Exception as e:
                logger.warning(f"SSO update failed: {e}")
                warnings.append(f"SSO sync gagal: {e}")

        # === STEP 3: Update Employee (employment data) ===
        if position is not None:
            employee.position = position
        if employee_type is not None:
            employee.type = employee_type
        if org_unit_id is not None:
            employee.org_unit_id = org_unit_id
        if supervisor_id is not None:
            employee.supervisor_id = supervisor_id
        
        employee.set_updated_by(updated_by)
        await self.employee_repo.update(employee)
        
        # Reload with relationships
        employee = await self.employee_repo.get_by_id(employee_id)
        logger.info(f"Employee updated: {employee_id}")

        # Publish event
        await self._publish_employee_event("updated", employee)

        return EmployeeAccountUpdateData(
            employee=EmployeeResponse.model_validate(employee),
            updated_fields={"employee": True, "sso": local_user.sso_id is not None},
            warnings=warnings if warnings else None,
        )

    async def delete_employee_account(
        self,
        employee_id: int,
        deleted_by: int,
    ) -> Dict[str, Any]:
        """Soft delete employee and deactivate SSO user."""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee dengan ID {employee_id} tidak ditemukan")

        warnings = []

        # Get linked user
        local_user = None
        if employee.user_id:
            local_user = await self.user_repo.get(employee.user_id)

        # Deactivate SSO user
        if local_user and local_user.sso_id:
            try:
                result = await self.sso_client.delete_user(local_user.sso_id)
                if not result.get("success"):
                    warnings.append(f"SSO delete failed: {result.get('error')}")
                else:
                    logger.info(f"SSO user deactivated: {local_user.sso_id}")
            except Exception as e:
                logger.warning(f"SSO delete failed: {e}")
                warnings.append(f"SSO delete failed: {e}")

        # Check if employee is org unit head
        is_head = await self.org_unit_repo.is_head_of_any_unit(employee_id)
        if is_head:
            raise ValidationException("Employee is org unit head - reassign before deleting")

        # Reassign subordinates
        subordinates = await self.employee_repo.get_all_by_supervisor(employee_id)
        if subordinates:
            subordinate_ids = [s.id for s in subordinates]
            new_supervisor_id = employee.supervisor_id
            await self.employee_repo.bulk_update_supervisor(
                subordinate_ids, new_supervisor_id, deleted_by
            )
            logger.info(f"Reassigned {len(subordinate_ids)} subordinates")

        # Soft delete employee
        await self.employee_repo.delete(employee_id, deleted_by)
        logger.info(f"Employee deleted: {employee_id}")

        # Deactivate local user
        if local_user:
            await self.user_repo.deactivate(local_user.id)
            logger.info(f"Local user deactivated: {local_user.id}")

        # Publish event
        deleted_emp = await self.employee_repo.get_by_id_with_deleted(employee_id)
        await self._publish_employee_event("deleted", deleted_emp)

        return {"success": True, "warnings": warnings if warnings else None}

    async def get_employee_account(self, employee_id: int) -> Dict[str, Any]:
        """Get employee with user profile and SSO data."""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee dengan ID {employee_id} tidak ditemukan")

        # Get SSO data for additional info
        sso_user = None
        if employee.user and employee.user.sso_id:
            try:
                sso_user = await self.sso_client.get_user(employee.user.sso_id)
            except Exception as e:
                logger.warning(f"Failed to get SSO user: {e}")

        return {
            "employee": EmployeeResponse.model_validate(employee),
            "sso_user": sso_user,
        }

    async def list_employee_accounts(
        self,
        page: int = 1,
        limit: int = 20,
        is_active: Optional[bool] = None,
        org_unit_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List employees with user profile data."""
        from app.modules.employees.repositories.employee_repository import (
            EmployeeFilters,
            PaginationParams,
        )
        
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(
            org_unit_id=org_unit_id,
            is_active=is_active,
            search=search,
        )
        
        employees, pagination = await self.employee_repo.list(params, filters)
        
        items = []
        for emp in employees:
            items.append(EmployeeAccountListItem(
                id=emp.id,
                sso_id=emp.user.sso_id if emp.user else None,
                employee_id=emp.id,
                name=emp.user.name if emp.user else "",
                email=emp.user.email if emp.user else "",
                is_active=emp.is_active,
            ))

        return {
            "items": items,
            "pagination": pagination.to_dict(),
        }

    async def _assign_default_role(self, user_id: int, employee_id: int) -> None:
        """Assign default role to user."""
        try:
            role = await self.role_repo.get_role_by_name("employee")
            if role:
                await self.role_repo.assign_role(user_id, role.id)
                logger.info(f"Employee role assigned to user {user_id}")

            if await self._is_org_unit_head(employee_id):
                head_role = await self.role_repo.get_role_by_name("org_unit_head")
                if head_role:
                    await self.role_repo.assign_role(user_id, head_role.id)
                    logger.info(f"Org unit head role assigned to user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to assign role: {e}")

    async def _is_org_unit_head(self, employee_id: int) -> bool:
        """Check if employee is org unit head."""
        return await self.org_unit_repo.is_head_of_any_unit(employee_id)

    async def _publish_employee_event(self, event_type: str, employee: Employee) -> None:
        """Publish employee event for other services."""
        if not self.event_publisher:
            return
        
        try:
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
                    "id": employee.user.id,
                    "sso_id": employee.user.sso_id,
                    "name": employee.user.name,
                    "email": employee.user.email,
                    "phone": employee.user.phone,
                    "gender": employee.user.gender,
                }
            
            if event_type == "created":
                await self.event_publisher.publish_employee_created(employee.id, data)
            elif event_type == "updated":
                await self.event_publisher.publish_employee_updated(employee.id, data)
            elif event_type == "deleted":
                await self.event_publisher.publish_employee_deleted(employee.id, data)
        except Exception as e:
            logger.warning(f"Failed to publish employee.{event_type} event: {e}")
