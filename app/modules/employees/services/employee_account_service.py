"""
Employee Account Service - SSO-First Flow

Orchestrates operations between:
- SSO (gRPC) - User authentication/profile
- Workforce (gRPC) - Employee data
- HRIS DB - Local user linking

Flow: SSO → Employee → HRIS User (idempotent, auto-recovery)
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
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
    Uses SSO gRPC for user management - no local user data duplication.
    """

    def __init__(
        self,
        employee_client: EmployeeGRPCClient,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        org_unit_client: OrgUnitGRPCClient,
    ):
        self.employee_client = employee_client
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.org_unit_client = org_unit_client
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
        
        Flow (idempotent - can resume from failure):
        1. Check/Create SSO user (critical - user can't login without this)
        2. Check/Create Employee via gRPC
        3. Check/Create HRIS user with links
        
        Each step auto-links if record already exists.
        """
        warnings = []
        full_name = f"{first_name} {last_name}"
        sso_id = None
        employee_id = None
        employee_data = None
        hris_user = None
        temp_password = None

        # === STEP 1: SSO User ===
        logger.info(f"Step 1: Check/create SSO user for email: {email}")
        
        # Check if SSO user exists
        existing_sso = await self.sso_client.get_user_by_email(email)
        
        if existing_sso:
            sso_id = existing_sso["id"]
            logger.info(f"SSO user exists: {sso_id}")
            
            # Check if already linked to HRIS user with different employee
            existing_hris = await self.user_repo.get_by_sso_id(sso_id)
            if existing_hris and existing_hris.employee_id:
                # Check if it's the same employee (by email)
                existing_emp = await self.employee_client.get_employee(existing_hris.employee_id)
                if existing_emp and existing_emp.get("email") == email:
                    # Same employee - return existing data (idempotent)
                    warnings.append("Employee sudah terdaftar sebelumnya")
                    return EmployeeAccountData(
                        employee=EmployeeResponse(**existing_emp),
                        user=None,
                        guest_account=None,
                        temporary_password=None,
                        warnings=warnings,
                    )
                else:
                    raise ConflictException(
                        f"Email {email} sudah terdaftar dan terhubung ke employee lain"
                    )
        else:
            # Create SSO user
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

        # === STEP 2: Employee via gRPC ===
        logger.info(f"Step 2: Check/create employee for email: {email}")
        
        existing_employee = await self.employee_client.get_employee_by_email(email)
        
        if existing_employee:
            employee_id = int(existing_employee["id"])
            employee_data = existing_employee
            logger.info(f"Employee exists: {employee_id}")
            
            # Check if already linked to different HRIS user
            linked_user = await self.user_repo.get_by_employee_id(employee_id)
            if linked_user and linked_user.sso_id != sso_id:
                raise ConflictException(
                    f"Employee sudah terhubung ke user SSO lain ({linked_user.sso_id})"
                )
        else:
            # Create employee
            employee_data = await self.employee_client.create_employee(
                employee_number=number,
                employee_name=full_name,
                employee_email=email,
                employee_phone=phone or "",
                employee_position=position or "",
                employee_type=employee_type,
                employee_gender=employee_gender,
                employee_org_unit_id=org_unit_id,
                created_by=created_by,
                employee_supervisor_id=supervisor_id,
            )
            employee_id = int(employee_data["id"])
            logger.info(f"Employee created: {employee_id}")

        # === STEP 3: HRIS User ===
        logger.info(f"Step 3: Check/create HRIS user for sso_id: {sso_id}")
        
        hris_user = await self.user_repo.get_by_sso_id(sso_id)
        
        if hris_user:
            # Update employee link if not set
            if not hris_user.employee_id:
                await self.user_repo.link_employee(hris_user.id, employee_id, org_unit_id)
                logger.info(f"HRIS user {hris_user.id} linked to employee {employee_id}")
            else:
                warnings.append("HRIS user sudah ter-link sebelumnya")
        else:
            # Create HRIS user
            hris_user = await self.user_repo.create({
                "sso_id": sso_id,
                "employee_id": employee_id,
                "org_unit_id": org_unit_id,
                "is_active": True,
            })
            logger.info(f"HRIS user created: {hris_user.id}")

        # Assign default role
        await self._assign_default_role(hris_user.id, employee_id)

        return EmployeeAccountData(
            employee=EmployeeResponse(**employee_data),
            user=None,  # HRIS user data is minimal now
            guest_account=None,
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
        # Profile fields for SSO
        alias: Optional[str] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> EmployeeAccountUpdateData:
        """Update employee and sync to SSO."""
        warnings = []

        # Get HRIS user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        if not user.employee_id:
            raise ValidationException("User tidak memiliki employee_id")

        # Build full name if provided
        full_name = None
        if first_name or last_name:
            # Get existing employee data
            existing_emp = await self.employee_client.get_employee(user.employee_id)
            if existing_emp:
                existing_name = existing_emp.get("name", "")
                parts = existing_name.split(" ", 1)
                existing_first = parts[0] if len(parts) > 0 else ""
                existing_last = parts[1] if len(parts) > 1 else ""
                
                fn = first_name if first_name else existing_first
                ln = last_name if last_name else existing_last
                full_name = f"{fn} {ln}"

        # Update Employee via gRPC
        employee_data = None
        if full_name or phone or position or employee_type or employee_gender or org_unit_id or supervisor_id:
            try:
                employee_data = await self.employee_client.update_employee(
                    employee_id=user.employee_id,
                    updated_by=updated_by,
                    employee_name=full_name,
                    employee_phone=phone,
                    employee_position=position,
                    employee_type=employee_type,
                    employee_gender=employee_gender,
                    employee_org_unit_id=org_unit_id,
                    employee_supervisor_id=supervisor_id,
                )
                logger.info(f"Employee updated: {user.employee_id}")
            except Exception as e:
                logger.error(f"Employee update failed: {e}")
                raise ValidationException(f"Gagal update employee: {e}")

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
            employee=EmployeeResponse(**employee_data) if employee_data else None,
            user=None,
            guest_account=None,
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
                await self.employee_client.delete_employee(
                    employee_id=user.employee_id,
                    deleted_by=deleted_by,
                )
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

        # Get SSO user data
        sso_user = None
        if user.sso_id:
            sso_user = await self.sso_client.get_user(user.sso_id)

        # Get employee data
        employee = None
        if user.employee_id:
            employee = await self.employee_client.get_employee(user.employee_id)

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

        # Enrich with SSO data
        items = []
        sso_ids = [u.sso_id for u in result["users"] if u.sso_id]
        
        # Batch get SSO users
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
            # Employee role
            role = await self.role_repo.get_role_by_name("employee")
            if role:
                await self.role_repo.assign_role(user_id, role.id)
                logger.info(f"Employee role assigned to user {user_id}")

            # Check if org unit head
            if await self._is_org_unit_head(employee_id):
                head_role = await self.role_repo.get_role_by_name("org_unit_head")
                if head_role:
                    await self.role_repo.assign_role(user_id, head_role.id)
                    logger.info(f"Org unit head role assigned to user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to assign role: {e}")

    async def _is_org_unit_head(self, employee_id: int) -> bool:
        """Check if employee is org unit head."""
        try:
            result = await self.org_unit_client.list_org_units(
                page=1, limit=1000, is_active=True
            )
            for org_unit in result.get("org_units", []):
                if org_unit.get("head_id") == employee_id:
                    return True
            return False
        except Exception:
            return False
