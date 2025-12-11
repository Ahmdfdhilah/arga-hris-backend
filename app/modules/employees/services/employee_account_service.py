"""
Service untuk operasi unified employee account (Employee + User + Guest)

Service ini mengorkestrasikan operasi antara:
- Employee (via gRPC ke workforce service)
- User (database lokal HRIS)
- Guest Account (database lokal HRIS)
- SSO (fire-and-forget sync)

Pattern: Compensating Transaction untuk rollback
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import httpx

from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.external_clients.rest.sso_client import sso_client
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.guests.repositories.guest_repository import GuestRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException,
)
from app.modules.employees.schemas import (
    EmployeeResponse,
    UserNestedResponse,
    GuestAccountNestedResponse,
    EmployeeAccountData,
    EmployeeAccountUpdateData,
    EmployeeAccountListItem,
    BulkInsertResult,
    EmployeeBulkItem,
)
from app.config.settings import settings

logger = logging.getLogger(__name__)

FIELD_INTERSECTION = {"first_name", "last_name", "org_unit_id"}
FIELD_EMPLOYEE_ONLY = {
    "number",
    "phone",
    "position",
    "employee_type",
    "employee_gender",
    "supervisor_id",
}
FIELD_GUEST_ONLY = {"valid_from", "valid_until", "guest_type", "notes", "sponsor_id"}


class EmployeeAccountService:
    """
    Service untuk operasi unified employee account

    Mengelola lifecycle employee beserta user account dan guest account-nya
    dengan support untuk rollback dan SSO sync (fire-and-forget)
    """

    def __init__(
        self,
        employee_client: EmployeeGRPCClient,
        user_repo: UserRepository,
        guest_repo: GuestRepository,
        role_repo: RoleRepository,
        org_unit_client: OrgUnitGRPCClient,
    ):
        self.employee_client = employee_client
        self.user_repo = user_repo
        self.guest_repo = guest_repo
        self.role_repo = role_repo
        self.org_unit_client = org_unit_client

    async def _is_employee_org_unit_head(self, employee_id: int) -> bool:
        """
        Check if employee is head of any organization unit

        Args:
            employee_id: ID employee yang akan dicek

        Returns:
            True jika employee adalah kepala unit, False jika tidak
        """
        try:
            result = await self.org_unit_client.list_org_units(
                page=1,
                limit=1000,
                is_active=True,
            )

            org_units = result.get("org_units", [])

            # Cek apakah employee_id ada di salah satu head_id
            for org_unit in org_units:
                if org_unit.get("head_id") == employee_id:
                    logger.info(
                        f"Employee {employee_id} is head of org_unit {org_unit.get('id')} ({org_unit.get('name')})"
                    )
                    return True

            return False

        except Exception as e:
            logger.warning(
                f"Failed to check if employee {employee_id} is org unit head: {str(e)}"
            )
            # Return False jika gagal cek, tidak menggagalkan proses
            return False

    async def create_employee_with_account(
        self,
        number: str,
        first_name: str,
        last_name: str,
        email: str,
        created_by: int,
        org_unit_id: Optional[int] = None,
        account_type: str = "none",
        phone: Optional[str] = None,
        position: Optional[str] = None,
        employee_type: Optional[str] = None,
        employee_gender: Optional[str] = None,
        supervisor_id: Optional[int] = None,
        guest_type: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        sponsor_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> EmployeeAccountData:
        """
        Membuat employee beserta user/guest account

        Flow (Robust - SSO First):
        1. Cek/buat Employee via gRPC (by email)
           - Jika sudah ada: validasi tidak ada user lain yang ter-link
           - Jika belum ada: buat employee baru
        2. Create user di SSO (CRITICAL - user butuh ini untuk login)
           - Jika gagal: return error (tidak lanjut ke step 3)
        3. Create User di HRIS DB dengan link ke employee_id dan sso_id
        4. Jika guest: Create GuestAccount + assign role

        Args:
            number: Nomor karyawan (unik)
            first_name: Nama depan
            last_name: Nama belakang
            email: Email karyawan (unik)
            org_unit_id: ID unit organisasi
            created_by: ID user yang membuat
            account_type: Tipe akun ('user', 'guest', 'none')
            phone: Nomor telepon (opsional)
            position: Jabatan (opsional)
            employee_type: Tipe karyawan (opsional)
            employee_gender: Gender karyawan (opsional)
            supervisor_id: ID atasan (opsional)
            guest_type: Tipe guest jika account_type='guest' (opsional)
            valid_from: Tanggal mulai berlaku guest (opsional)
            valid_until: Tanggal akhir berlaku guest (wajib untuk guest)
            sponsor_id: ID sponsor guest (opsional)
            notes: Catatan untuk guest (opsional)

        Returns:
            Dict dengan employee, user, guest_account, temporary_password, dan warnings

        Raises:
            ValidationException: Jika validasi input gagal
            ConflictException: Jika email sudah ter-link ke user lain atau SSO gagal
        """
        warnings = []
        employee_id = None
        employee_data = None
        user = None
        guest_account = None
        temporary_password = None
        sso_id = None

        # Validasi input untuk guest
        if account_type == "guest":
            if not valid_until:
                raise ValidationException("valid_until wajib diisi untuk akun guest")
            if not guest_type:
                raise ValidationException("guest_type wajib diisi untuk akun guest")

        # Validasi account_type
        if account_type not in ["user", "guest", "none"]:
            raise ValidationException("account_type harus 'user', 'guest', atau 'none'")

        try:
            # Step 1: Cek/buat Employee via gRPC
            full_name = f"{first_name} {last_name}"

            # Cek apakah employee dengan email ini sudah ada
            existing_employee = await self.employee_client.get_employee_by_email(email)

            if existing_employee:
                # Employee sudah ada, cek apakah ada user lain yang sudah ter-link
                employee_id_raw = existing_employee.get("id")
                if employee_id_raw is None:
                    raise ValidationException("Employee data tidak memiliki ID")
                employee_id = int(employee_id_raw)
                logger.info(f"Employee already exists: ID={employee_id}, email={email}")

                # Cek apakah ada user yang sudah ter-link dengan employee ini
                existing_user = await self.user_repo.get_by_employee_id(employee_id)
                if existing_user:
                    raise ConflictException(
                        f"Employee dengan email {email} sudah ter-link dengan user lain (user_id={existing_user.id}). "
                        f"Tidak dapat membuat akun baru."
                    )

                # Employee ada tapi belum ter-link, akan di-link nanti
                employee_data = existing_employee
                logger.info(f"Employee exists but not linked, will link to new user")
            else:
                # Employee belum ada, buat baru
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
                employee_id_raw = employee_data.get("id")
                if employee_id_raw is None:
                    raise ValidationException(
                        "Employee data tidak memiliki ID setelah create"
                    )
                employee_id = int(employee_id_raw)
                logger.info(f"Employee created: ID={employee_id}, number={number}")

            # Jika account_type='none', langsung return tanpa buat user
            if account_type == "none":
                return EmployeeAccountData(
                    employee=EmployeeResponse(**employee_data),
                    user=None,
                    guest_account=None,
                    temporary_password=None,
                    warnings=warnings,
                )

            # Step 2: Create user di SSO (CRITICAL!)
            # User butuh ini untuk login, jadi harus berhasil dulu sebelum lanjut
            try:
                user_account_type = "guest" if account_type == "guest" else "regular"

                # Check if user already exists in SSO
                existing_sso_user = await sso_client.get_user_by_email(email)

                if existing_sso_user:
                    # User sudah ada di SSO, gunakan sso_id yang ada
                    sso_id_raw = existing_sso_user.get("id")
                    if sso_id_raw is None:
                        raise ValidationException("SSO user tidak memiliki ID")
                    sso_id = int(sso_id_raw)
                    logger.info(
                        f"SSO user already exists, using existing sso_id={sso_id}, email={email}"
                    )

                    # Untuk guest, tidak ada temporary_password karena user sudah ada
                    # Password harus di-reset manual jika diperlukan
                    if account_type == "guest":
                        warnings.append(
                            "User sudah ada di SSO. Password tidak di-generate ulang. "
                            "Jika perlu reset password, gunakan fitur reset password di SSO."
                        )
                else:
                    # User belum ada di SSO, create baru
                    guest_metadata = None
                    if account_type == "guest":
                        guest_metadata = {
                            "guest_type": guest_type,
                            "valid_from": (
                                valid_from.isoformat()
                                if valid_from
                                else datetime.now().isoformat()
                            ),
                            "valid_until": (
                                valid_until.isoformat() if valid_until else None
                            ),
                            "notes": notes,
                        }

                    sso_response = await sso_client.create_user(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        account_type=user_account_type,
                        guest_metadata=guest_metadata,
                    )

                    # Get sso_id dari response
                    sso_id_raw = sso_response.get("sso_id") or sso_response.get("id")
                    if not sso_id_raw:
                        raise ValidationException("SSO tidak mengembalikan sso_id")
                    sso_id = int(sso_id_raw)

                    logger.info(
                        f"SSO user created successfully: sso_id={sso_id}, email={email}"
                    )

                    # Ambil temporary password jika guest
                    if account_type == "guest":
                        temporary_password = sso_response.get("temporary_password")

                # Auto-assign HRIS application to user
                try:
                    await sso_client.assign_application_to_user(
                        sso_id=sso_id,
                        application_id=settings.SSO_HRIS_APPLICATION_ID,
                    )
                    logger.info(
                        f"User {email} assigned to HRIS application (app_id: {settings.SSO_HRIS_APPLICATION_ID})"
                    )
                except httpx.HTTPStatusError as e:
                    logger.warning(
                        f"Failed to assign HRIS application to user: {e.response.status_code} - {e.response.text}"
                    )
                    warnings.append(
                        "HRIS application assignment gagal, tapi user tetap bisa login"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to assign HRIS application to user: {str(e)}"
                    )
                    warnings.append(
                        "HRIS application assignment gagal, tapi user tetap bisa login"
                    )

            except Exception as e:
                logger.error(f"SSO user creation failed: {str(e)}")
                # SSO gagal adalah critical error karena user butuh ini untuk login
                raise ConflictException(
                    f"Gagal membuat user di SSO (user tidak bisa login tanpa ini): {str(e)}. "
                    f"Employee dengan email {email} sudah dibuat (ID={employee_id}), bisa di-link manual nanti."
                )

            # Step 3: Create User di HRIS DB dengan link ke employee_id dan sso_id
            try:
                # Check apakah sso_id sudah ter-link ke user lain di HRIS
                existing_user_with_sso = await self.user_repo.get_by_sso_id(sso_id)

                if existing_user_with_sso:
                    # SSO ID sudah ter-link ke user lain
                    if existing_user_with_sso.employee_id == employee_id:
                        # Sudah ter-link ke employee yang sama, return existing user
                        logger.info(
                            f"User already exists with same employee_id: user_id={existing_user_with_sso.id}, "
                            f"employee_id={employee_id}, sso_id={sso_id}"
                        )
                        user = existing_user_with_sso
                        warnings.append(
                            "User di HRIS sudah ada dengan employee_id dan sso_id yang sama. "
                            "Menggunakan user yang existing."
                        )
                    else:
                        # SSO ID ter-link ke employee yang berbeda - CONFLICT!
                        raise ConflictException(
                            f"SSO ID {sso_id} sudah ter-link ke user lain dengan employee_id={existing_user_with_sso.employee_id}. "
                            f"Tidak bisa link ke employee_id={employee_id}. "
                            f"Kemungkinan email {email} sudah digunakan oleh employee lain."
                        )
                else:
                    # SSO ID belum ter-link, create user baru
                    user = await self.user_repo.create(
                        {
                            "employee_id": employee_id,
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                            "org_unit_id": org_unit_id,
                            "account_type": user_account_type,
                            "is_active": True,
                            "sso_id": sso_id,  # Link langsung dengan sso_id yang sudah dibuat
                        }
                    )

                    logger.info(
                        f"HRIS user created: ID={user.id}, employee_id={employee_id}, sso_id={sso_id}"
                    )

            except ConflictException:
                # Re-raise conflict exception
                raise
            except Exception as e:
                logger.error(f"HRIS user creation failed: {str(e)}")
                # Jika gagal, warning saja karena SSO sudah berhasil (user bisa login)
                # Nanti bisa di-link manual atau akan ter-link otomatis saat first login
                warnings.append(
                    f"User di SSO sudah dibuat (sso_id={sso_id}) dan bisa login, "
                    f"tapi gagal create di HRIS DB: {str(e)}. "
                    f"Akan ter-link otomatis saat user login pertama kali."
                )

                # Return dengan warning
                return EmployeeAccountData(
                    employee=EmployeeResponse(**employee_data),
                    user=None,
                    guest_account=None,
                    temporary_password=temporary_password,
                    warnings=warnings,
                )

            # Step 4: Jika guest, create GuestAccount + assign role
            if account_type == "guest":
                try:
                    # Create guest account
                    guest_account = await self.guest_repo.create_guest_account(
                        {
                            "user_id": user.id,
                            "guest_type": guest_type,
                            "valid_from": valid_from or datetime.now(),
                            "valid_until": valid_until,
                            "sponsor_id": sponsor_id,
                            "notes": notes,
                        }
                    )

                    logger.info(
                        f"Guest account created: ID={guest_account.id}, user_id={user.id}"
                    )

                    # Assign guest role
                    guest_role = await self.role_repo.get_role_by_name("guest")
                    if guest_role:
                        await self.role_repo.assign_role(user.id, guest_role.id)
                        logger.info(f"Guest role assigned to user {user.id}")
                    else:
                        logger.warning("Guest role tidak ditemukan di database")
                        warnings.append(
                            "Role 'guest' tidak ditemukan, role tidak di-assign"
                        )

                except Exception as e:
                    logger.error(f"Guest account creation failed: {str(e)}")
                    # Guest account gagal, tapi user sudah bisa login (SSO + HRIS user sudah ada)
                    warnings.append(
                        f"Gagal membuat guest account: {str(e)}. "
                        f"User sudah bisa login tapi guest metadata belum lengkap."
                    )
            else:
                # Step 4b: Assign employee role untuk non-guest user
                try:
                    employee_role = await self.role_repo.get_role_by_name("employee")
                    if employee_role:
                        await self.role_repo.assign_role(user.id, employee_role.id)
                        logger.info(f"Employee role assigned to user {user.id}")
                    else:
                        logger.warning("Employee role tidak ditemukan di database")
                        warnings.append(
                            "Role 'employee' tidak ditemukan, role tidak di-assign"
                        )
                except Exception as e:
                    logger.warning(f"Failed to assign employee role: {str(e)}")
                    warnings.append(f"Gagal assign employee role: {str(e)}")

            # Step 5: Check if employee is org unit head dan assign role jika iya
            try:
                is_head = await self._is_employee_org_unit_head(employee_id)
                if is_head:
                    org_unit_head_role = await self.role_repo.get_role_by_name(
                        "org_unit_head"
                    )
                    if org_unit_head_role:
                        await self.role_repo.assign_role(user.id, org_unit_head_role.id)
                        logger.info(
                            f"Org unit head role assigned to user {user.id} (employee {employee_id})"
                        )
                    else:
                        logger.warning("Org unit head role tidak ditemukan di database")
                        warnings.append(
                            "Role 'org_unit_head' tidak ditemukan, role tidak di-assign"
                        )
            except Exception as e:
                logger.warning(f"Failed to check/assign org unit head role: {str(e)}")
                warnings.append(f"Gagal check/assign org unit head role: {str(e)}")

            guest_account_response = None
            if guest_account:
                guest_account_response = GuestAccountNestedResponse(
                    id=guest_account.id,
                    user_id=guest_account.user_id,
                    guest_type=guest_account.guest_type,
                    valid_from=(
                        guest_account.valid_from.isoformat()
                        if guest_account.valid_from
                        else None
                    ),
                    valid_until=(
                        guest_account.valid_until.isoformat()
                        if guest_account.valid_until
                        else None
                    ),
                    sponsor_id=guest_account.sponsor_id,
                    notes=guest_account.notes,
                )

            return EmployeeAccountData(
                employee=EmployeeResponse(**employee_data),
                user=UserNestedResponse.model_validate(user),
                guest_account=guest_account_response,
                temporary_password=temporary_password,
                warnings=warnings,
            )

        except (ValidationException, ConflictException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_employee_with_account: {str(e)}")
            raise ValidationException(f"Gagal membuat karyawan dan akun: {str(e)}")

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
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        guest_type: Optional[str] = None,
        notes: Optional[str] = None,
        sponsor_id: Optional[int] = None,
    ) -> EmployeeAccountUpdateData:
        """
        Update employee dengan smart field routing

        Field dikategorikan menjadi:
        - INTERSECTION: first_name, last_name, org_unit_id (update employee + user + SSO)
        - EMPLOYEE_ONLY: number, phone, position, supervisor_id (update employee saja)
        - GUEST_ONLY: valid_from, valid_until, guest_type, notes, sponsor_id (update guest_account + SSO)

        NOTE: Email TIDAK BISA diubah karena merupakan core credential untuk login dan authentication.

        Flow:
        1. Get user by user_id
        2. Klasifikasi field yang di-update
        3. Update employee via gRPC (intersection + employee-only)
        4. Update user di DB (intersection fields)
        5. Jika guest: update guest_account (guest-only fields)
        6. Sync ke SSO (fire-and-forget untuk intersection + guest-only fields)

        Args:
            user_id: ID user di HRIS
            updated_by: ID user yang melakukan update
            [field parameters]: Field-field yang akan di-update (semua opsional)

        Returns:
            Dict dengan employee, user, guest_account, updated_fields breakdown, dan warnings

        Raises:
            NotFoundException: Jika user tidak ditemukan
        """
        warnings = []

        # Step 1: Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        if not user.employee_id:
            raise ValidationException(
                "User tidak memiliki employee_id, tidak bisa update employee"
            )

        # Step 2: Klasifikasi field yang di-update
        provided_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "org_unit_id": org_unit_id,
            "number": number,
            "phone": phone,
            "position": position,
            "employee_type": employee_type,
            "employee_gender": employee_gender,
            "supervisor_id": supervisor_id,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "guest_type": guest_type,
            "notes": notes,
            "sponsor_id": sponsor_id,
        }

        # Filter hanya field yang tidak None
        provided_fields = {k: v for k, v in provided_fields.items() if v is not None}

        intersection_updates = {
            k: v for k, v in provided_fields.items() if k in FIELD_INTERSECTION
        }
        employee_only_updates = {
            k: v for k, v in provided_fields.items() if k in FIELD_EMPLOYEE_ONLY
        }
        guest_only_updates = {
            k: v for k, v in provided_fields.items() if k in FIELD_GUEST_ONLY
        }

        updated_fields_breakdown = {
            "intersection": list(intersection_updates.keys()),
            "employee_only": list(employee_only_updates.keys()),
            "guest_only": list(guest_only_updates.keys()),
        }

        # Step 3: Update Employee via gRPC (intersection + employee-only)
        employee_data = None
        if intersection_updates or employee_only_updates:
            try:
                # Gabungkan first_name + last_name jadi name jika ada
                full_name = None
                if first_name and last_name:
                    full_name = f"{first_name} {last_name}"
                elif first_name or last_name:
                    # Ambil existing employee data untuk merge
                    existing_employee = await self.employee_client.get_employee(
                        user.employee_id
                    )
                    existing_name = existing_employee.get("name", "")
                    parts = existing_name.split(" ", 1)
                    existing_first = parts[0] if len(parts) > 0 else ""
                    existing_last = parts[1] if len(parts) > 1 else ""

                    if first_name:
                        full_name = f"{first_name} {existing_last}"
                    else:
                        full_name = f"{existing_first} {last_name}"

                employee_data = await self.employee_client.update_employee(
                    employee_id=user.employee_id,
                    updated_by=updated_by,
                    employee_name=full_name,
                    employee_email=None,  # Email tidak boleh diubah
                    employee_phone=phone,
                    employee_position=position,
                    employee_type=employee_type,
                    employee_gender=employee_gender,
                    employee_org_unit_id=org_unit_id,
                    employee_supervisor_id=supervisor_id,
                    is_active=None,
                )

                logger.info(f"Employee updated: ID={user.employee_id}")

            except Exception as e:
                logger.error(f"Employee update failed: {str(e)}")
                raise ValidationException(f"Gagal update employee: {str(e)}")

        # Step 4: Update User di DB (intersection fields)
        if intersection_updates:
            try:
                user_updates = {}
                if first_name is not None:
                    user_updates["first_name"] = first_name
                if last_name is not None:
                    user_updates["last_name"] = last_name
                if org_unit_id is not None:
                    user_updates["org_unit_id"] = org_unit_id
                # Email tidak boleh diubah - dihapus dari user_updates

                updated_user = await self.user_repo.update_user(user_id, **user_updates)

                logger.info(f"User updated: ID={user_id}")

            except Exception as e:
                logger.error(
                    f"User update failed (inconsistency dengan employee): {str(e)}"
                )
                warnings.append(
                    f"Update user gagal: {str(e)}. Employee sudah diupdate, ada inkonsistensi data."
                )
                raise ValidationException(f"Gagal update user: {str(e)}")

        # Step 5: Jika guest, update GuestAccount (guest-only fields)
        guest_account_data = None
        if guest_only_updates:
            # Cek apakah user adalah guest
            if user.account_type != "guest":
                warnings.append("Field guest dilewati karena user bukan guest account")
            else:
                try:
                    guest_updates = {}
                    if valid_from is not None:
                        guest_updates["valid_from"] = valid_from
                    if valid_until is not None:
                        guest_updates["valid_until"] = valid_until
                    if guest_type is not None:
                        guest_updates["guest_type"] = guest_type
                    if notes is not None:
                        guest_updates["notes"] = notes
                    if sponsor_id is not None:
                        guest_updates["sponsor_id"] = sponsor_id

                    guest_account = await self.guest_repo.update_guest_account(
                        user_id, guest_updates
                    )

                    if guest_account:
                        guest_account_data = {
                            "id": guest_account.id,
                            "user_id": guest_account.user_id,
                            "guest_type": guest_account.guest_type,
                            "valid_from": (
                                guest_account.valid_from.isoformat()
                                if guest_account.valid_from
                                else None
                            ),
                            "valid_until": (
                                guest_account.valid_until.isoformat()
                                if guest_account.valid_until
                                else None
                            ),
                            "sponsor_id": guest_account.sponsor_id,
                            "notes": guest_account.notes,
                        }
                        logger.info(f"Guest account updated: ID={guest_account.id}")
                    else:
                        warnings.append("Guest account tidak ditemukan untuk user ini")

                except Exception as e:
                    logger.warning(f"Guest account update failed: {str(e)}")
                    warnings.append(f"Update guest account gagal: {str(e)}")

        # Step 6: Sync ke SSO (fire-and-forget)
        if user.sso_id and (intersection_updates or guest_only_updates):
            try:
                # Untuk guest user: gunakan update_guest_user
                if user.account_type == "guest" and guest_only_updates:
                    sso_payload = {}

                    if valid_from is not None:
                        sso_payload["valid_from"] = (
                            valid_from.isoformat()
                            if hasattr(valid_from, "isoformat")
                            else valid_from
                        )

                    if valid_until is not None:
                        sso_payload["valid_until"] = (
                            valid_until.isoformat()
                            if hasattr(valid_until, "isoformat")
                            else valid_until
                        )

                    if notes is not None:
                        sso_payload["notes"] = notes

                    if sso_payload:
                        await sso_client.update_guest_user(
                            sso_id=user.sso_id, **sso_payload
                        )
                        logger.info(f"SSO guest update success: sso_id={user.sso_id}")

                # Untuk intersection fields: gunakan update_user
                if intersection_updates:
                    sso_payload = {}

                    if first_name is not None:
                        sso_payload["first_name"] = first_name

                    if last_name is not None:
                        sso_payload["last_name"] = last_name

                    if sso_payload:
                        await sso_client.update_user(
                            sso_id=str(user.sso_id), **sso_payload
                        )
                        logger.info(f"SSO user update success: sso_id={user.sso_id}")

            except Exception as e:
                logger.warning(f"SSO sync failed (fire-and-forget): {str(e)}")
                warnings.append(
                    f"SSO sync gagal: {str(e)}. Data dapat di-sync manual nanti."
                )
        elif not user.sso_id:
            warnings.append("User belum punya sso_id, skip SSO sync")

        # Build typed response
        return EmployeeAccountUpdateData(
            employee=EmployeeResponse(**employee_data) if employee_data else None,
            user=UserNestedResponse.model_validate(user),
            guest_account=(
                GuestAccountNestedResponse(**guest_account_data)
                if guest_account_data
                else None
            ),
            updated_fields=updated_fields_breakdown,
            warnings=warnings,
        )

    async def activate_employee_account(
        self,
        user_id: int,
        updated_by: int,
    ) -> List[str]:
        """
        Aktivasi employee beserta user/guest account

        Returns: List of warnings (empty if no warnings)
        Raises: NotFoundException, ValidationException
        """
        warnings = []

        # Step 1: Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        if not user.employee_id:
            raise ValidationException(
                "User tidak memiliki employee_id, tidak bisa aktivasi employee"
            )

        # Step 2: Update employee.is_active=True
        try:
            await self.employee_client.update_employee(
                employee_id=user.employee_id,
                updated_by=updated_by,
                is_active=True,
            )
            logger.info(f"Employee activated: ID={user.employee_id}")
        except Exception as e:
            logger.error(f"Employee activation failed: {str(e)}")
            raise ValidationException(f"Gagal aktivasi employee: {str(e)}")

        # Step 3: Update user.is_active=True
        try:
            await self.user_repo.activate_user(user_id)
            logger.info(f"User activated: ID={user_id}")
        except Exception as e:
            logger.error(f"User activation failed: {str(e)}")
            warnings.append(f"Aktivasi user gagal: {str(e)}")

        # Step 4: Sync ke SSO (fire-and-forget)
        if user.sso_id:
            try:
                await sso_client.activate_user(str(user.sso_id))
                logger.info(f"SSO activation success: sso_id={user.sso_id}")
            except Exception as e:
                logger.warning(f"SSO activation failed (fire-and-forget): {str(e)}")
                warnings.append(f"SSO activation gagal: {str(e)}")
        else:
            warnings.append("User belum punya sso_id, skip SSO sync")

        return warnings

    async def deactivate_employee_account(
        self,
        user_id: int,
        updated_by: int,
    ) -> List[str]:
        """
        Deaktivasi employee beserta user/guest account

        Returns: List of warnings (empty if no warnings)
        Raises: NotFoundException, ValidationException
        """
        warnings = []

        # Step 1: Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        if not user.employee_id:
            raise ValidationException(
                "User tidak memiliki employee_id, tidak bisa deaktivasi employee"
            )

        # Step 2: Update employee.is_active=False
        try:
            await self.employee_client.update_employee(
                employee_id=user.employee_id,
                updated_by=updated_by,
                is_active=False,
            )
            logger.info(f"Employee deactivated: ID={user.employee_id}")
        except Exception as e:
            logger.error(f"Employee deactivation failed: {str(e)}")
            raise ValidationException(f"Gagal deaktivasi employee: {str(e)}")

        # Step 3: Update user.is_active=False
        try:
            await self.user_repo.deactivate_user(user_id)
            logger.info(f"User deactivated: ID={user_id}")
        except Exception as e:
            logger.error(f"User deactivation failed: {str(e)}")
            warnings.append(f"Deaktivasi user gagal: {str(e)}")

        # Step 4: Sync ke SSO (fire-and-forget)
        if user.sso_id:
            try:
                await sso_client.deactivate_user(str(user.sso_id))
                logger.info(f"SSO deactivation success: sso_id={user.sso_id}")
            except Exception as e:
                logger.warning(f"SSO deactivation failed (fire-and-forget): {str(e)}")
                warnings.append(f"SSO deactivation gagal: {str(e)}")
        else:
            warnings.append("User belum punya sso_id, skip SSO sync")

        return warnings

    async def sync_user_to_sso(
        self,
        user_id: int,
    ) -> List[str]:
        """
        Manual sync user ke SSO (retry mechanism)

        Digunakan ketika SSO sync gagal saat create dan perlu di-retry manual

        Flow:
        1. Get user by ID
        2. Validasi user belum punya sso_id
        3. Create user di SSO
        4. Update user.sso_id dengan response dari SSO

        Args:
            user_id: ID user di HRIS

        Returns:
            Dict dengan success message dan sso_id

        Raises:
            NotFoundException: Jika user tidak ditemukan
            ValidationException: Jika user sudah punya sso_id
        """
        # Step 1: Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        # Step 2: Validasi belum punya sso_id
        if user.sso_id:
            raise ValidationException(
                f"User sudah punya sso_id={user.sso_id}, tidak perlu sync lagi"
            )

        # Step 3: Create user di SSO
        try:
            guest_metadata = None

            # Jika guest, ambil guest account data
            if user.account_type == "guest":
                guest_account = await self.guest_repo.get_guest_account_by_user_id(
                    user_id
                )
                if guest_account:
                    guest_metadata = {
                        "guest_type": guest_account.guest_type,
                        "valid_from": (
                            guest_account.valid_from.isoformat()
                            if guest_account.valid_from
                            else None
                        ),
                        "valid_until": (
                            guest_account.valid_until.isoformat()
                            if guest_account.valid_until
                            else None
                        ),
                        "notes": guest_account.notes,
                    }

            sso_response = await sso_client.create_user(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                account_type=user.account_type,
                guest_metadata=guest_metadata,
            )

            # Step 4: Update user.sso_id
            sso_id = sso_response.get("sso_id") or sso_response.get("id")
            if sso_id:
                await self.user_repo.update_user(user_id, sso_id=sso_id)
                logger.info(
                    f"Manual SSO sync success: user_id={user_id}, sso_id={sso_id}"
                )

                # Auto-assign HRIS application to user
                try:
                    await sso_client.assign_application_to_user(
                        sso_id=sso_id,
                        application_id=settings.SSO_HRIS_APPLICATION_ID,
                    )
                    logger.info(
                        f"User {user.email} assigned to HRIS application (app_id: {settings.SSO_HRIS_APPLICATION_ID})"
                    )
                except httpx.HTTPStatusError as e:
                    # Log error but don't fail - application assignment is optional
                    logger.warning(
                        f"Failed to assign HRIS application to user: {e.response.status_code} - {e.response.text}"
                    )
                except Exception as e:
                    # Log error but don't fail
                    logger.warning(
                        f"Failed to assign HRIS application to user: {str(e)}"
                    )
            else:
                raise ValidationException("SSO response tidak mengembalikan sso_id")

            return []  # No warnings, sync successful

        except Exception as e:
            logger.error(f"Manual SSO sync failed: {str(e)}")
            raise ValidationException(f"Gagal sync ke SSO: {str(e)}")

    async def get_employee_with_account(
        self,
        user_id: int,
    ) -> EmployeeAccountListItem:
        """
        Get employee with account by user_id

        Returns: EmployeeAccountListItem
        Raises: NotFoundException
        """
        # Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        # Get employee via gRPC jika ada employee_id
        employee_data = None
        if user.employee_id:
            try:
                employee_data = await self.employee_client.get_employee(
                    user.employee_id
                )

                # Check if employee is soft-deleted
                if employee_data and employee_data.get("deleted_at"):
                    raise NotFoundException(
                        f"Employee {user.employee_id} has been archived/deleted"
                    )

            except Exception as e:
                logger.warning(f"Failed to get employee {user.employee_id}: {str(e)}")

        # Get guest account jika user adalah guest
        guest_account_data = None
        if user.account_type == "guest":
            guest_account = await self.guest_repo.get_guest_account_by_user_id(user_id)
            if guest_account:
                guest_account_data = {
                    "id": guest_account.id,
                    "user_id": guest_account.user_id,
                    "guest_type": guest_account.guest_type,
                    "valid_from": (
                        guest_account.valid_from.isoformat()
                        if guest_account.valid_from
                        else None
                    ),
                    "valid_until": (
                        guest_account.valid_until.isoformat()
                        if guest_account.valid_until
                        else None
                    ),
                    "sponsor_id": guest_account.sponsor_id,
                    "notes": guest_account.notes,
                }

        # Build typed response
        return EmployeeAccountListItem(
            employee=EmployeeResponse(**employee_data) if employee_data else None,
            user=UserNestedResponse.model_validate(user),
            guest_account=(
                GuestAccountNestedResponse(**guest_account_data)
                if guest_account_data
                else None
            ),
        )

    async def list_employees_with_account(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        account_type: Optional[str] = None,
    ) -> tuple[List[EmployeeAccountListItem], Dict[str, Any]]:
        """
        List employees with account (paginated)

        Returns: (items, pagination_dict)
        """
        # Get users dengan filter (exclude users with deleted employees)
        result = await self.user_repo.list_users_paginated(
            page=page,
            limit=limit,
            search=search,
            is_active=is_active,
            has_employee=True,  # Hanya user yang punya employee_id
            org_unit_id=org_unit_id,
            account_type=account_type,
            exclude_deleted_employees=True,  # Filter deleted employees di SQL level
        )

        users = result["users"]
        pagination = result["pagination"]

        # Build response dengan employee dan guest data
        items = []
        for user in users:
            # Get employee via gRPC
            employee_data = None
            if user.employee_id:
                try:
                    employee_data = await self.employee_client.get_employee(
                        user.employee_id
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to get employee {user.employee_id}: {str(e)}"
                    )

            # Get guest account jika user adalah guest
            guest_account_data = None
            if user.account_type == "guest":
                guest_account = await self.guest_repo.get_guest_account_by_user_id(
                    user.id
                )
                if guest_account:
                    guest_account_data = {
                        "id": guest_account.id,
                        "user_id": guest_account.user_id,
                        "guest_type": guest_account.guest_type,
                        "valid_from": (
                            guest_account.valid_from.isoformat()
                            if guest_account.valid_from
                            else None
                        ),
                        "valid_until": (
                            guest_account.valid_until.isoformat()
                            if guest_account.valid_until
                            else None
                        ),
                        "sponsor_id": guest_account.sponsor_id,
                        "notes": guest_account.notes,
                    }

            # Build typed item
            items.append(
                EmployeeAccountListItem(
                    employee=(
                        EmployeeResponse(**employee_data) if employee_data else None
                    ),
                    user=UserNestedResponse.model_validate(user),
                    guest_account=(
                        GuestAccountNestedResponse(**guest_account_data)
                        if guest_account_data
                        else None
                    ),
                )
            )

        return items, pagination

    async def soft_delete_employee_account(
        self,
        user_id: int,
        deleted_by_user_id: int,
    ) -> EmployeeAccountData:
        """
        Soft delete employee account (archive)

        Steps:
        1. Get user and validate
        2. Soft delete employee via gRPC (auto-reassign subordinates)
        3. Deactivate user in HRIS
        4. Deactivate SSO (fire-and-forget)

        Args:
            user_id: ID user yang akan di-soft delete
            deleted_by_user_id: ID user yang melakukan soft delete

        Returns:
            EmployeeAccountData dengan deleted employee

        Raises:
            NotFoundException: User tidak ditemukan
            ValidationException: User tidak punya employee_id
            ConflictException: Employee is org unit head (must reassign first)
        """
        warnings = []

        # 1. Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")

        if not user.employee_id:
            raise ValidationException("User does not have employee_id")

        # 2. Soft delete employee via gRPC
        try:
            deleted_employee_data = await self.employee_client.soft_delete_employee(
                employee_id=user.employee_id, deleted_by_user_id=deleted_by_user_id
            )
            logger.info(f"Employee {user.employee_id} soft deleted successfully")
        except Exception as e:
            logger.error(f"Failed to soft delete employee {user.employee_id}: {str(e)}")
            raise ValidationException(f"Failed to archive employee: {str(e)}")

        # 3. Deactivate user & mark employee as deleted
        try:
            from datetime import datetime

            await self.user_repo.update_user(
                user_id, is_active=False, employee_deleted_at=datetime.now()
            )
            logger.info(f"User {user_id} deactivated and marked as employee deleted")
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {str(e)}")
            warnings.append(f"Employee archived but user deactivation failed: {str(e)}")

        # 4. Deactivate SSO (fire-and-forget)
        if user.sso_id:
            try:
                await sso_client.deactivate_user(str(user.sso_id))
                logger.info(f"SSO user {user.sso_id} deactivated (fire-and-forget)")
            except Exception as e:
                logger.warning(f"Failed to deactivate SSO user {user.sso_id}: {str(e)}")
                warnings.append(f"SSO deactivation failed: {str(e)}")

        # Get guest account jika ada
        guest_account_data = None
        if user.account_type == "guest":
            guest_account = await self.guest_repo.get_guest_account_by_user_id(user_id)
            if guest_account:
                guest_account_data = {
                    "id": guest_account.id,
                    "user_id": guest_account.user_id,
                    "guest_type": guest_account.guest_type,
                    "valid_from": (
                        guest_account.valid_from.isoformat()
                        if guest_account.valid_from
                        else None
                    ),
                    "valid_until": (
                        guest_account.valid_until.isoformat()
                        if guest_account.valid_until
                        else None
                    ),
                    "sponsor_id": guest_account.sponsor_id,
                    "notes": guest_account.notes,
                }

        return EmployeeAccountData(
            employee=EmployeeResponse(**deleted_employee_data),
            user=UserNestedResponse.model_validate(user),
            guest_account=(
                GuestAccountNestedResponse(**guest_account_data)
                if guest_account_data
                else None
            ),
            warnings=warnings,
        )

    async def restore_employee_account(
        self,
        user_id: int,
    ) -> EmployeeAccountData:
        """
        Restore soft-deleted employee account

        Steps:
        1. Get user and validate
        2. Restore employee via gRPC
        3. Activate user in HRIS
        4. Activate SSO (fire-and-forget)

        Args:
            user_id: ID user yang akan di-restore

        Returns:
            EmployeeAccountData dengan restored employee

        Raises:
            NotFoundException: User tidak ditemukan
            ValidationException: User tidak punya employee_id atau employee not deleted
        """
        warnings = []

        # 1. Get user
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")

        if not user.employee_id:
            raise ValidationException("User does not have employee_id")

        # 2. Restore employee via gRPC
        try:
            restored_employee_data = await self.employee_client.restore_employee(
                employee_id=user.employee_id
            )
            logger.info(f"Employee {user.employee_id} restored successfully")
        except Exception as e:
            logger.error(f"Failed to restore employee {user.employee_id}: {str(e)}")
            raise ValidationException(f"Failed to restore employee: {str(e)}")

        # 3. Activate user & clear employee deleted mark
        try:
            await self.user_repo.update_user(
                user_id, is_active=True, employee_deleted_at=None
            )
            logger.info(f"User {user_id} activated and employee deletion mark cleared")
        except Exception as e:
            logger.error(f"Failed to activate user {user_id}: {str(e)}")
            warnings.append(f"Employee restored but user activation failed: {str(e)}")

        # 4. Activate SSO (fire-and-forget)
        if user.sso_id:
            try:
                await sso_client.activate_user(str(user.sso_id))
                logger.info(f"SSO user {user.sso_id} activated (fire-and-forget)")
            except Exception as e:
                logger.warning(f"Failed to activate SSO user {user.sso_id}: {str(e)}")
                warnings.append(f"SSO activation failed: {str(e)}")

        guest_account_data = None
        if user.account_type == "guest":
            guest_account = await self.guest_repo.get_guest_account_by_user_id(user_id)
            if guest_account:
                guest_account_data = {
                    "id": guest_account.id,
                    "user_id": guest_account.user_id,
                    "guest_type": guest_account.guest_type,
                    "valid_from": (
                        guest_account.valid_from.isoformat()
                        if guest_account.valid_from
                        else None
                    ),
                    "valid_until": (
                        guest_account.valid_until.isoformat()
                        if guest_account.valid_until
                        else None
                    ),
                    "sponsor_id": guest_account.sponsor_id,
                    "notes": guest_account.notes,
                }

        return EmployeeAccountData(
            employee=EmployeeResponse(**restored_employee_data),
            user=UserNestedResponse.model_validate(user),
            guest_account=(
                GuestAccountNestedResponse(**guest_account_data)
                if guest_account_data
                else None
            ),
            warnings=warnings,
        )

    async def list_deleted_employees(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[List[EmployeeAccountListItem], Dict[str, Any]]:
        """
        List deleted/archived employees employee_number

        Args:
            page: Page number
            limit: Items per page
            search: Search query (name, email, number)

        Returns:
            (items, pagination_dict)
        """
        # Get deleted employees dari gRPC
        result = await self.employee_client.list_deleted_employees(
            page=page,
            limit=limit,
            search=search,
        )

        employees = result.get("employees", [])
        pagination = result.get("pagination", {})

        # Build response dengan user dan guest data
        items = []
        for employee_data in employees:
            # Get user by employee_id
            user = None
            guest_account_data = None

            try:
                user = await self.user_repo.get_by_employee_id(employee_data["id"])

                # Get guest account jika user adalah guest
                if user and user.account_type == "guest":
                    guest_account = await self.guest_repo.get_guest_account_by_user_id(
                        user.id
                    )
                    if guest_account:
                        guest_account_data = {
                            "id": guest_account.id,
                            "user_id": guest_account.user_id,
                            "guest_type": guest_account.guest_type,
                            "valid_from": (
                                guest_account.valid_from.isoformat()
                                if guest_account.valid_from
                                else None
                            ),
                            "valid_until": (
                                guest_account.valid_until.isoformat()
                                if guest_account.valid_until
                                else None
                            ),
                            "sponsor_id": guest_account.sponsor_id,
                            "notes": guest_account.notes,
                        }
            except Exception as e:
                logger.warning(
                    f"Failed to get user for employee {employee_data['id']}: {str(e)}"
                )

            if user:
                items.append(
                    EmployeeAccountListItem(
                        employee=EmployeeResponse(**employee_data),
                        user=UserNestedResponse.model_validate(user),
                        guest_account=(
                            GuestAccountNestedResponse(**guest_account_data)
                            if guest_account_data
                            else None
                        ),
                    )
                )

        return items, pagination

    async def bulk_insert_employees(
        self,
        items: List[EmployeeBulkItem],
        created_by: int,
        skip_errors: bool = False,
    ) -> BulkInsertResult:
        """
        Bulk insert employees from Excel data

        Args:
            items: List of EmployeeBulkItem dari Excel
            created_by: ID user yang membuat
            skip_errors: Skip item yang error dan lanjutkan processing

        Returns:
            BulkInsertResult dengan detail success/error
        """
        result = BulkInsertResult(
            total_items=len(items),
            success_count=0,
            error_count=0,
            errors=[],
            warnings=[],
            created_ids=[],
        )

        # Cache untuk mapping org_unit_name -> org_unit_id
        org_unit_name_map = {}

        # Resolve org_unit_name to org_unit_id
        for item in items:
            if item.org_unit_name and item.org_unit_name not in org_unit_name_map:
                try:
                    response = await self.org_unit_client.list_org_units(
                        search=item.org_unit_name,
                        limit=10
                    )

                    org_units_list = response.get("org_units", [])

                    # Cari exact match atau first match
                    org_unit = None
                    for ou in org_units_list:
                        if ou.get("name") == item.org_unit_name:
                            org_unit = ou
                            break

                    # Jika tidak ada exact match, ambil yang pertama
                    if not org_unit and org_units_list:
                        org_unit = org_units_list[0]

                    if org_unit:
                        org_unit_name_map[item.org_unit_name] = org_unit.get("id")
                except Exception:
                    # Jika tidak ketemu, akan di-handle per item
                    pass

        # Process each employee
        for item in items:
            try:
                # Resolve org_unit_id
                org_unit_id = org_unit_name_map.get(item.org_unit_name)
                if not org_unit_id:
                    # Try to fetch again dengan search
                    try:
                        response = await self.org_unit_client.list_org_units(
                            search=item.org_unit_name,
                            limit=10
                        )
                        org_units_list = response.get("org_units", [])

                        # Cari exact match
                        org_unit = None
                        for ou in org_units_list:
                            if ou.get("name") == item.org_unit_name:
                                org_unit = ou
                                break

                        # Jika tidak ada exact match, ambil yang pertama
                        if not org_unit and org_units_list:
                            org_unit = org_units_list[0]

                        if org_unit:
                            org_unit_id = org_unit.get("id")
                            org_unit_name_map[item.org_unit_name] = org_unit_id
                    except Exception:
                        pass

                if not org_unit_id:
                    result.error_count += 1
                    result.errors.append(
                        {
                            "row_number": item.row_number,
                            "number": item.number,
                            "error": f"Department '{item.org_unit_name}' tidak ditemukan",
                        }
                    )
                    if not skip_errors:
                        continue
                    continue

                # Check if employee already exists by number or email
                try:
                    existing_by_number = (
                        await self.employee_client.get_employee_by_number(item.number)
                    )
                    if existing_by_number:
                        result.error_count += 1
                        result.errors.append(
                            {
                                "row_number": item.row_number,
                                "number": item.number,
                                "error": f"Nomor karyawan '{item.number}' sudah ada",
                            }
                        )
                        if not skip_errors:
                            continue
                        continue
                except Exception:
                    pass

                try:
                    existing_by_email = (
                        await self.employee_client.get_employee_by_email(item.email)
                    )
                    if existing_by_email:
                        result.error_count += 1
                        result.errors.append(
                            {
                                "row_number": item.row_number,
                                "number": item.number,
                                "error": f"Email '{item.email}' sudah ada",
                            }
                        )
                        if not skip_errors:
                            continue
                        continue
                except Exception:
                    pass

                # Parse dates if provided
                valid_from = None
                valid_until = None
                if item.valid_from:
                    try:
                        valid_from = datetime.fromisoformat(
                            item.valid_from.replace("Z", "+00:00")
                        )
                    except Exception as e:
                        result.warnings.append(
                            f"Row {item.row_number}: Invalid valid_from format: {str(e)}"
                        )

                if item.valid_until:
                    try:
                        valid_until = datetime.fromisoformat(
                            item.valid_until.replace("Z", "+00:00")
                        )
                    except Exception as e:
                        result.warnings.append(
                            f"Row {item.row_number}: Invalid valid_until format: {str(e)}"
                        )

                # Create employee with account
                created = await self.create_employee_with_account(
                    number=item.number,
                    first_name=item.first_name,
                    last_name=item.last_name,
                    email=item.email,
                    org_unit_id=org_unit_id,
                    created_by=created_by,
                    account_type=item.account_type or "user",
                    phone=item.phone,
                    position=item.position,
                    employee_type=item.employee_type,
                    employee_gender=item.employee_gender,
                    supervisor_id=None,  # Supervisor akan di-set di fase kedua jika diperlukan
                    guest_type=None,  # Guest type untuk guest account
                    valid_from=valid_from,
                    valid_until=valid_until,
                    sponsor_id=None,  # Sponsor untuk guest account
                    notes=item.notes,
                )

                result.success_count += 1
                result.created_ids.append(created.employee.id)

            except ValidationException as e:
                result.error_count += 1
                result.errors.append(
                    {
                        "row_number": item.row_number,
                        "number": item.number,
                        "error": f"Validation error: {str(e)}",
                    }
                )
                if not skip_errors:
                    break
            except ConflictException as e:
                result.error_count += 1
                result.errors.append(
                    {
                        "row_number": item.row_number,
                        "number": item.number,
                        "error": f"Conflict: {str(e)}",
                    }
                )
                if not skip_errors:
                    break
            except Exception as e:
                result.error_count += 1
                result.errors.append(
                    {
                        "row_number": item.row_number,
                        "number": item.number,
                        "error": str(e),
                    }
                )
                if not skip_errors:
                    break

        return result
