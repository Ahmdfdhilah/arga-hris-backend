"""
Auth Service

High-level authentication and authorization service.
Combines token verification, user data fetching, and caching.
"""

from typing import Dict, Any

from app.modules.auth.services.token_service import TokenService
from app.modules.auth.repositories.user_cache_repository import UserCacheRepository
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.guests.repositories.guest_repository import GuestRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.modules.auth.schemas import (
    CurrentUserResponse,
    TokenInfoResponse,
    RefreshCacheResponse,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.core.exceptions import UnauthorizedException, NotFoundException, ConflictException
from app.core.schemas import CurrentUser

import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""

    def __init__(
        self,
        token_service: TokenService,
        user_cache_repo: UserCacheRepository,
        user_repo: UserRepository,
        guest_repo: GuestRepository,
        role_repo: RoleRepository,
        employee_grpc_client: EmployeeGRPCClient,
        org_unit_client: OrgUnitGRPCClient,
    ):
        """
        Initialize AuthService

        Args:
            token_service: TokenService instance
            user_cache_repo: UserCacheRepository instance
            user_repo: UserRepository instance
            guest_repo: GuestRepository instance
            role_repo: RoleRepository instance
            employee_grpc_client: EmployeeGRPCClient instance
            org_unit_client: OrgUnitGRPCClient instance
        """
        self.token_service = token_service
        self.user_cache_repo = user_cache_repo
        self.user_repo = user_repo
        self.guest_repo = guest_repo
        self.role_repo = role_repo
        self.employee_grpc_client = employee_grpc_client
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
            # List semua org units (dengan pagination besar untuk catch semua)
            # Idealnya backend menyediakan endpoint khusus untuk cek ini
            result = await self.org_unit_client.list_org_units(
                page=1,
                limit=1000,  # Ambil banyak untuk memastikan semua ter-cover
                is_active=True,
            )

            org_units = result.get("org_units", [])

            # Cek apakah employee_id ada di salah satu head_id
            for org_unit in org_units:
                if org_unit.get("head_id") == employee_id:
                    logger.info(f"Employee {employee_id} is head of org_unit {org_unit.get('id')} ({org_unit.get('name')})")
                    return True

            return False

        except Exception as e:
            logger.warning(f"Failed to check if employee {employee_id} is org unit head: {str(e)}")
            # Return False jika gagal cek, tidak menggagalkan proses
            return False

    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user from token (NO CACHE - always fresh data)

        Hybrid Provisioning Strategy:
        1. Verify token and check blacklist
        2. Try to find user by sso_id (exact match)
        3. If not found, try email-based linking (for pre-created users)
        4. If still not found, create new user (JIT provisioning)
        5. Return user data with roles and permissions (fresh from DB)

        Args:
            token: JWT token string

        Returns:
            User data with roles and permissions

        Raises:
            UnauthorizedException: If token invalid
        """
        # Step 1: Verify token and check blacklist
        payload = await self.token_service.verify_and_check_blacklist(token)

        # Extract identifiers
        sso_id_raw = payload.get("sso_id") or payload.get("sub")
        email = payload.get("email")

        if not sso_id_raw:
            raise UnauthorizedException("Token tidak memiliki identitas pengguna")

        # Convert sso_id to integer (it may come as string from JWT)
        try:
            sso_id = int(sso_id_raw)
        except (ValueError, TypeError):
            raise UnauthorizedException(f"Invalid sso_id format: {sso_id_raw}")

        # Step 2: Try exact SSO ID match
        user = await self.user_repo.get_by_sso_id(sso_id)

        # Step 3: If not found, try email-based linking (pre-created users)
        if not user and email:
            user = await self._link_user_by_email(sso_id, email)

        # Step 4: If still not found, create new user (JIT provisioning)
        if not user:
            user = await self._create_user_from_token(payload)

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedException("Akun pengguna tidak aktif")

        # Check if guest user has expired
        if user.account_type == "guest":
            from datetime import datetime, timezone
            guest_account = await self.guest_repo.get_guest_account_by_user_id(user.id)
            if guest_account and guest_account.valid_until:
                now = datetime.now(timezone.utc)
                valid_until = guest_account.valid_until
                # Make valid_until timezone-aware if it isn't
                if valid_until.tzinfo is None:
                    valid_until = valid_until.replace(tzinfo=timezone.utc)
                if now > valid_until:
                    raise UnauthorizedException("Akun guest telah kadaluarsa")

        # Step 5: Get complete user data
        user_data = await self._get_user_data(user.id)

        return user_data

    async def _get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get user data from DB (NO CACHE - always fresh)

        Args:
            user_id: User ID

        Returns:
            Complete user data with roles and permissions
        """
        # Fetch from DB directly (no cache check)
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"Pengguna dengan ID {user_id} tidak ditemukan")

        # Get roles and permissions (fresh from DB)
        user_roles = await self.role_repo.get_user_roles(user_id)
        user_permissions = await self.role_repo.get_user_permissions(user_id)

        # Build user data
        user_data = {
            "id": user.id,
            "sso_id": user.sso_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "employee_id": user.employee_id,
            "roles": user_roles if user_roles else [],
            "permissions": user_permissions if user_permissions else [],
            "is_active": user.is_active,
        }

        return user_data

    async def logout(self, token: str) -> None:
        """
        Logout user (no-op in HRIS service)
        Token blacklist is handled by frontend calling SSO directly

        Since we no longer cache user data, logout in HRIS service doesn't need to do anything.
        All token invalidation is handled by SSO service.

        Args:
            token: JWT token string

        Returns:
            None
        """
        # No-op: We don't cache user data anymore, and token blacklist is handled by SSO
        return None

    async def logout_all_sessions(self, user_id: int) -> None:
        """
        Logout user from all devices
        Use case: password change, security breach

        Args:
            user_id: User ID

        Returns:
            None
        """
        # Revoke all user tokens
        await self.token_service.revoke_all_user_tokens(str(user_id))

        # Note: No cache invalidation needed since we don't cache user data anymore
        return None

    async def refresh_user_cache(self, user_id: int) -> RefreshCacheResponse:
        """
        Refresh user cache (deprecated - no longer using cache)

        This method is kept for backward compatibility but does nothing
        since we no longer cache user data.

        Args:
            user_id: User ID

        Returns:
            RefreshCacheResponse
        """
        return RefreshCacheResponse(
            user_id=user_id,
            refreshed=False,
            note="Caching is disabled"
        )

    async def get_token_info(self, token: str) -> TokenInfoResponse:
        """
        Get token information without full verification
        Useful for debugging

        Args:
            token: JWT token string

        Returns:
            TokenInfoResponse dengan token info
        """
        payload = await self.token_service.verify_token(token)

        jti = payload.get("jti")
        is_blacklisted = False
        if jti:
            is_blacklisted = await self.token_service.token_repo.is_token_blacklisted(
                jti
            )

        user_id = payload.get("sub") or payload.get("sso_id")
        return TokenInfoResponse(
            user_id=str(user_id) if user_id else None,
            jti=jti,
            exp=payload.get("exp"),
            is_blacklisted=is_blacklisted,
        )

    async def validate_token(self, token: str) -> bool:
        """
        Simple token validation
        Returns True/False instead of raising exception

        Args:
            token: JWT token string

        Returns:
            True if valid, False otherwise
        """
        return await self.token_service.is_token_valid(token)

    async def get_current_user_info(
        self, current_user: CurrentUser
    ) -> CurrentUserResponse:
        """
        Get current user information with response

        Args:
            current_user: Current user data from dependency

        Returns:
            CurrentUserResponse dengan user information
        """
        return CurrentUserResponse(
            id=current_user.id,
            sso_id=current_user.sso_id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            full_name=current_user.full_name,
            employee_id=current_user.employee_id,
            roles=current_user.roles,
            permissions=current_user.permissions,
            is_active=current_user.is_active,
    )

    async def _link_user_by_email(self, sso_id: int, email: str):
        """
        Link existing HRIS user to SSO account via email matching

        This enables admin to pre-create users in HRIS before SSO account exists.
        When user first logs in, system auto-links by email.

        Args:
            sso_id: SSO user identifier from JWT (SSO User.id as integer)
            email: User email from JWT

        Returns:
            User object if found and linked, None otherwise

        Raises:
            ConflictException: If email already linked to different SSO ID
        """
        # Find user by email
        user = await self.user_repo.get_by_email(email)

        if not user:
            return None

        # Safety check: prevent overwriting existing sso_id
        if user.sso_id:
            if user.sso_id != sso_id:
                raise ConflictException(
                    f"Email {email} sudah terhubung dengan akun SSO yang berbeda. "
                    f"Silakan hubungi administrator."
                )
            # Already linked to this sso_id, return user
            return user

        # Safe to link: sso_id is NULL
        user.sso_id = sso_id

        # Update name if empty (use data from JWT)
        if not user.first_name:
            user.first_name = email.split("@")[0].split(".")[0].title()
        if not user.last_name and "." in email.split("@")[0]:
            user.last_name = email.split("@")[0].split(".")[1].title()

        # Save to database
        await self.user_repo.update(user.id, {
            "sso_id": user.sso_id,
            "first_name": user.first_name,
            "last_name": user.last_name
        })

        # FIX: If user is guest but guest_account doesn't exist, create it from JWT
        if user.account_type == "guest":
            existing_guest_account = await self.guest_repo.get_guest_account_by_user_id(user.id)

            if not existing_guest_account:
                # Try to create guest_account from JWT payload if available
                # This happens when admin pre-created guest user in HRIS but not yet in SSO
                # Then user was created in SSO and now logging in for first time
                try:
                    from datetime import datetime, timezone, timedelta

                    # Default values for guest_account if not in JWT
                    guest_type = "guest"
                    valid_from = datetime.now(timezone.utc)
                    valid_until = datetime.now(timezone.utc) + timedelta(days=30)

                    guest_account_data = {
                        "user_id": user.id,
                        "guest_type": guest_type,
                        "valid_from": valid_from,
                        "valid_until": valid_until,
                        "sponsor_id": None,
                        "notes": "Auto-created on first login"
                    }
                    await self.guest_repo.create_guest_account(guest_account_data)
                except Exception as e:
                    # Log but don't fail the login
                    print(f"Failed to create guest_account for user {user.id}: {str(e)}")

        return user

    async def _create_user_from_token(self, payload: Dict[str, Any]):
        """
        Create new user from JWT token (JIT Provisioning)
        Auto-detect guest users and assign appropriate role

        Args:
            payload: JWT token payload

        Returns:
            Newly created user object
        """
        from datetime import datetime
        from dateutil import parser

        sso_id = payload.get("sso_id") or payload.get("sub")
        email = payload.get("email")
        first_name = payload.get("first_name", "")
        last_name = payload.get("last_name", "")

        if sso_id is None:
            raise UnauthorizedException("Token tidak memiliki sso_id atau sub")

        account_type = payload.get("account_type", "regular")

        # Extract guest metadata if present
        guest_metadata = payload.get("guest_metadata", {})
        guest_type = guest_metadata.get("guest_type")
        guest_valid_from_str = guest_metadata.get("valid_from")
        guest_valid_until_str = guest_metadata.get("valid_until")
        guest_sponsor_email = guest_metadata.get("sponsor_email")

        # Parse datetime strings
        guest_valid_from = None
        guest_valid_until = None
        if guest_valid_from_str:
            try:
                guest_valid_from = parser.isoparse(guest_valid_from_str)
            except Exception:
                pass
        if guest_valid_until_str:
            try:
                guest_valid_until = parser.isoparse(guest_valid_until_str)
            except Exception:
                pass

        # Find sponsor user
        guest_sponsor_id = None
        if guest_sponsor_email:
            try:
                sponsor = await self.user_repo.get_by_email(guest_sponsor_email)
                guest_sponsor_id = sponsor.id if sponsor else None
            except Exception:
                pass

        # Fallback: extract name from email if not provided
        if not first_name and email:
            first_name = email.split("@")[0].split(".")[0].title()
        if not last_name and email and "." in email.split("@")[0]:
            last_name = email.split("@")[0].split(".")[1].title()

        # Create user data
        user_data = {
            "sso_id": sso_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "account_type": account_type,
            "is_active": True,
        }

        # Create user in database
        user = await self.user_repo.create(user_data)

        # Create guest account if guest user
        if account_type == "guest" and guest_valid_until:
            try:
                guest_account_data = {
                    "user_id": user.id,
                    "guest_type": guest_type or "guest",
                    "valid_from": guest_valid_from or datetime.utcnow(),
                    "valid_until": guest_valid_until,
                    "sponsor_id": guest_sponsor_id,
                    "notes": None
                }
                await self.guest_repo.create_guest_account(guest_account_data)
            except Exception:
                pass

        # Assign role based on account type
        try:
            if account_type == "guest":
                role = await self.role_repo.get_role_by_name("guest")
            else:
                role = await self.role_repo.get_role_by_name("employee")

            if role:
                await self.role_repo.assign_role(user.id, role.id)
        except Exception as e:
            logger.warning(f"Failed to assign role to user {user.id}: {str(e)}")
            pass  # Continue even if role assignment fails

        # Try to auto-link to employee by email (skip for guests)
        if email and account_type != "guest":
            try:
                # Search for employee by email in workforce database
                employee_data = await self.employee_grpc_client.get_employee_by_email(email)

                if employee_data:
                    employee_id_raw = employee_data.get("id")

                    if employee_id_raw is not None:
                        employee_id = int(employee_id_raw)

                        # Check if this employee is already linked to another user
                        existing_user = await self.user_repo.get_by_employee_id(employee_id)

                        if not existing_user:
                            # Safe to link: employee not yet linked to any user
                            await self.user_repo.link_employee(user.id, employee_id)
                            user.employee_id = employee_id
                            logger.info(f"User {user.id} successfully linked to employee {employee_id}")

                            # Check if employee is org unit head and assign role
                            try:
                                is_head = await self._is_employee_org_unit_head(employee_id)
                                if is_head:
                                    org_unit_head_role = await self.role_repo.get_role_by_name("org_unit_head")
                                    if org_unit_head_role:
                                        await self.role_repo.assign_role(user.id, org_unit_head_role.id)
                                        logger.info(f"Org unit head role assigned to user {user.id} (employee {employee_id})")
                            except Exception as e:
                                logger.warning(f"Failed to check/assign org unit head role: {str(e)}")

                        # If employee already linked to another user, skip linking silently
            except Exception as e:
                # Log but don't fail the login process
                logger.warning(f"Failed to auto-link employee for user {user.id} (email: {email}): {str(e)}")
                pass

        return user
