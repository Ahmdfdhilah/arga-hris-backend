"""
Employee Account Service - SSO-First Flow (Refactored for Local Repository)

Orchestrates operations between:
- SSO (gRPC) - User authentication/profile
- Local Repositories - Employee/OrgUnit data (master)
- HRIS DB - Local user linking

Flow: SSO → Employee → HRIS User (idempotent, auto-recovery)
"""

from typing import Optional, Dict, Any
import logging

from app.modules.employees.repositories.employee_repository import EmployeeRepository
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.models.employee import Employee
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

logger = logging.getLogger(__name__)


class EmployeeAccountService:
    """
    Service untuk operasi unified employee account.
    Uses local repositories for employee/org_unit data, SSO gRPC for user management.
    """

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        org_unit_repo: OrgUnitRepository,
        user_repo: UserRepository,
        role_repo: RoleRepository,
    ):
        self.employee_repo = employee_repo
        self.org_unit_repo = org_unit_repo
        self.user_repo = user_repo
        self.role_repo = role_repo
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
        employee_gender: Optional[str] = None,
        supervisor_id: Optional[int] = None,
    ) -> EmployeeAccountData:
        """
        Create employee with linked SSO user and HRIS user.
        """
        warnings = []
        full_name = f"{first_name} {last_name}"
        sso_id = None
        employee_id = None
        employee_obj = None
        hris_user = None
        temp_password = None

        # === STEP 1: SSO User ===
        logger.info(f"Step 1: Check/create SSO user for email: {email}")
        
        existing_sso = await self.sso_client.get_user_by_email(email)
        
        if existing_sso:
            sso_id = existing_sso["id"]
            logger.info(f"SSO user exists: {sso_id}")
            
            existing_hris = await self.user_repo.get_by_sso_id(sso_id)
            if existing_hris and existing_hris.employee_id:
                existing_emp = await self.employee_repo.get_by_id(existing_hris.employee_id)
                if existing_emp and existing_emp.email == email:
                    warnings.append("Employee sudah terdaftar sebelumnya")
                    return EmployeeAccountData(
                        employee=EmployeeResponse.model_validate(existing_emp),
                        user=None,
                        temporary_password=None,
                        warnings=warnings,
                    )
                else:
                    raise ConflictException(
                        f"Email {email} sudah terdaftar dan terhubung ke employee lain"
                    )
        else:
            create_result = await self.sso_client.create_user(
                email=email,
                name=full_name,
                phone=phone,
                role="user",
            )
            
            if not create_result.get("success"):
                error = create_result.get("error", "Unknown error")
                raise ConflictException(f"Gagal membuat user di SSO: {error}")
            
            sso_id = create_result["user"]["id"]
            temp_password = create_result.get("temporary_password")
            logger.info(f"SSO user created: {sso_id}")

        # === STEP 2: Employee (Local) ===
        logger.info(f"Step 2: Check/create employee for email: {email}")
        
        existing_employee = await self.employee_repo.get_by_email(email)
        
        if existing_employee:
            employee_id = existing_employee.id
            employee_obj = existing_employee
            logger.info(f"Employee exists: {employee_id}")
            
            linked_user = await self.user_repo.get_by_employee_id(employee_id)
            if linked_user and linked_user.sso_id != sso_id:
                raise ConflictException(
                    f"Employee sudah terhubung ke user SSO lain ({linked_user.sso_id})"
                )
        else:
            # Auto-assign supervisor based on org unit
            auto_supervisor_id = supervisor_id
            if not auto_supervisor_id and org_unit_id:
                org_unit = await self.org_unit_repo.get_by_id(org_unit_id)
                if org_unit and org_unit.head_id:
                    auto_supervisor_id = org_unit.head_id
            
            employee = Employee(
                number=number,
                name=full_name,
                email=email,
                phone=phone,
                position=position,
                employee_type=employee_type,
                employee_gender=employee_gender,
                org_unit_id=org_unit_id,
                supervisor_id=auto_supervisor_id,
                is_active=True
            )
            employee.set_created_by(created_by)
            
            employee_obj = await self.employee_repo.create(employee)
            employee_id = employee_obj.id
            
            # Reload with relationships
            employee_obj = await self.employee_repo.get_by_id(employee_id)
            logger.info(f"Employee created: {employee_id}")

        # === STEP 3: HRIS User ===
        logger.info(f"Step 3: Check/create HRIS user for sso_id: {sso_id}")
        
        hris_user = await self.user_repo.get_by_sso_id(sso_id)
        
        if hris_user:
            if not hris_user.employee_id:
                await self.user_repo.link_employee(hris_user.id, employee_id, org_unit_id)
                logger.info(f"HRIS user {hris_user.id} linked to employee {employee_id}")
            else:
                warnings.append("HRIS user sudah ter-link sebelumnya")
        else:
            hris_user = await self.user_repo.create({
                "sso_id": sso_id,
                "employee_id": employee_id,
                "org_unit_id": org_unit_id,
                "is_active": True,
            })
            logger.info(f"HRIS user created: {hris_user.id}")

        await self._assign_default_role(hris_user.id, employee_id)

        return EmployeeAccountData(
            employee=EmployeeResponse.model_validate(employee_obj),
            user=None,
            temporary_password=temp_password,
            warnings=warnings if warnings else None,
        )

    async def update_employee_with_account(
        self,
        user_id: int,
        updated_by: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        number: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        supervisor_id: Optional[int] = None,
        alias: Optional[str] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> EmployeeAccountUpdateData:
        """Update employee and sync to SSO."""
        warnings = []

        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        if not user.employee_id:
            raise ValidationException("User tidak memiliki employee_id")

        employee = await self.employee_repo.get_by_id(user.employee_id)
        if not employee:
            raise NotFoundException(f"Employee dengan ID {user.employee_id} tidak ditemukan")

        # Build full name if provided
        full_name = None
        if first_name or last_name:
            existing_name = employee.name or ""
            parts = existing_name.split(" ", 1)
            existing_first = parts[0] if len(parts) > 0 else ""
            existing_last = parts[1] if len(parts) > 1 else ""
            
            fn = first_name if first_name else existing_first
            ln = last_name if last_name else existing_last
            full_name = f"{fn} {ln}"

        # Update Employee
        if full_name:
            employee.name = full_name
        if phone is not None:
            employee.phone = phone
        if position is not None:
            employee.position = position
        if employee_type is not None:
            employee.employee_type = employee_type
        if employee_gender is not None:
            employee.employee_gender = employee_gender
        if org_unit_id is not None:
            employee.org_unit_id = org_unit_id
        if supervisor_id is not None:
            employee.supervisor_id = supervisor_id
        
        employee.set_updated_by(updated_by)
        await self.employee_repo.update(employee)
        
        # Reload with relationships
        employee = await self.employee_repo.get_by_id(user.employee_id)
        logger.info(f"Employee updated: {user.employee_id}")

        # Update HRIS user org_unit if changed
        if org_unit_id:
            await self.user_repo.update(user_id, {"org_unit_id": org_unit_id})

        # Update SSO user profile
        if user.sso_id and (full_name or alias or gender or address or bio):
            try:
                await self.sso_client.update_user(
                    user_id=user.sso_id,
                    name=full_name,
                    alias=alias,
                    gender=gender,
                    address=address,
                    bio=bio,
                )
                logger.info(f"SSO user updated: {user.sso_id}")
            except Exception as e:
                logger.warning(f"SSO update failed: {e}")
                warnings.append(f"SSO sync gagal: {e}")

        return EmployeeAccountUpdateData(
            employee=EmployeeResponse.model_validate(employee),
            user=None,
            updated_fields={"employee": True, "sso": True},
            warnings=warnings if warnings else None,
        )

    async def delete_employee_account(
        self,
        user_id: int,
        deleted_by: int,
    ) -> Dict[str, Any]:
        """Soft delete employee and deactivate SSO user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        warnings = []

        # Deactivate SSO user
        if user.sso_id:
            try:
                result = await self.sso_client.delete_user(user.sso_id)
                if not result.get("success"):
                    warnings.append(f"SSO delete failed: {result.get('error')}")
                else:
                    logger.info(f"SSO user deleted: {user.sso_id}")
            except Exception as e:
                logger.warning(f"SSO delete failed: {e}")
                warnings.append(f"SSO delete failed: {e}")

        # Soft delete employee
        if user.employee_id:
            try:
                is_head = await self.org_unit_repo.is_head_of_any_unit(user.employee_id)
                if is_head:
                    warnings.append("Employee is org unit head - reassign before deleting")
                else:
                    employee = await self.employee_repo.get_by_id(user.employee_id)
                    subordinates = await self.employee_repo.get_all_by_supervisor(user.employee_id)
                    if subordinates:
                        subordinate_ids = [s.id for s in subordinates]
                        new_supervisor_id = employee.supervisor_id if employee else None
                        await self.employee_repo.bulk_update_supervisor(
                            subordinate_ids, new_supervisor_id, deleted_by
                        )
                    
                    await self.employee_repo.delete(user.employee_id, deleted_by)
                    logger.info(f"Employee deleted: {user.employee_id}")
            except Exception as e:
                logger.warning(f"Employee delete failed: {e}")
                warnings.append(f"Employee delete failed: {e}")

        # Deactivate HRIS user
        await self.user_repo.deactivate(user_id)
        logger.info(f"HRIS user deactivated: {user_id}")

        return {"success": True, "warnings": warnings if warnings else None}

    async def get_employee_account(self, user_id: int) -> Dict[str, Any]:
        """Get employee account with SSO user data."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        sso_user = None
        if user.sso_id:
            sso_user = await self.sso_client.get_user(user.sso_id)

        employee = None
        if user.employee_id:
            emp = await self.employee_repo.get_by_id(user.employee_id)
            if emp:
                employee = {
                    "id": emp.id,
                    "number": emp.number,
                    "name": emp.name,
                    "email": emp.email,
                    "phone": emp.phone,
                    "position": emp.position,
                    "org_unit_id": emp.org_unit_id,
                    "is_active": emp.is_active,
                }

        return {
            "hris_user": {
                "id": user.id,
                "sso_id": user.sso_id,
                "employee_id": user.employee_id,
                "org_unit_id": user.org_unit_id,
                "is_active": user.is_active,
            },
            "sso_user": sso_user,
            "employee": employee,
        }

    async def list_employee_accounts(
        self,
        page: int = 1,
        limit: int = 20,
        is_active: Optional[bool] = None,
        org_unit_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List employee accounts with SSO data."""
        result = await self.user_repo.list_paginated(
            page=page,
            limit=limit,
            is_active=is_active,
            has_employee=True,
            org_unit_id=org_unit_id,
        )

        items = []
        sso_ids = [u.sso_id for u in result["users"] if u.sso_id]
        
        sso_users = {}
        if sso_ids:
            sso_list = await self.sso_client.batch_get_users(sso_ids)
            sso_users = {u["id"]: u for u in sso_list}

        for user in result["users"]:
            sso_data = sso_users.get(user.sso_id, {})
            items.append(EmployeeAccountListItem(
                id=user.id,
                sso_id=user.sso_id,
                employee_id=user.employee_id,
                name=sso_data.get("name", ""),
                email=sso_data.get("email", ""),
                is_active=user.is_active,
            ))

        return {
            "items": items,
            "pagination": result["pagination"],
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
