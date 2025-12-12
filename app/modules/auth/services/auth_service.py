"""
Auth Service - Simplified for SSO Integration

Auth is now delegated to SSO service. This service handles:
- Logout via SSO gRPC
- Token validation via SSO gRPC
- Getting current user info
"""

from typing import Dict, Any

from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.modules.auth.schemas import (
    CurrentUserResponse,
    TokenInfoResponse,
    RefreshCacheResponse,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.core.schemas import CurrentUser

import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations - delegates to SSO"""

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        employee_grpc_client: EmployeeGRPCClient,
        org_unit_client: OrgUnitGRPCClient,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.employee_grpc_client = employee_grpc_client
        self.org_unit_client = org_unit_client

    async def logout(self, token: str) -> None:
        """
        Logout user - no-op in HRIS.
        Single device logout should be done directly to SSO by frontend.
        """
        return None

    async def logout_all_sessions(self, user_id: int) -> None:
        """
        Logout user from all devices via SSO gRPC.
        """
        from app.external_clients.grpc.sso_client import SSOAuthGRPCClient

        user = await self.user_repo.get(user_id)
        if not user or not user.sso_id:
            logger.warning(f"Cannot logout user {user_id}: no SSO ID")
            return None

        try:
            sso_client = SSOAuthGRPCClient()
            result = await sso_client.logout(
                user_id=user.sso_id,
                global_logout=True
            )
            if result.get("success"):
                logger.info(f"User {user_id} logged out from all sessions")
            else:
                logger.warning(f"SSO logout failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"Failed to logout via SSO: {str(e)}")

        return None

    async def validate_token(self, token: str) -> bool:
        """Validate token via SSO gRPC."""
        from app.external_clients.grpc.sso_client import SSOAuthGRPCClient

        try:
            sso_client = SSOAuthGRPCClient()
            result = await sso_client.validate_token(token)
            return result.get("is_valid", False)
        except Exception:
            return False

    async def get_current_user_info(self, current_user: CurrentUser) -> CurrentUserResponse:
        """Get current user information for API response."""
        return CurrentUserResponse(
            id=current_user.id,
            sso_id=current_user.sso_id,
            name=current_user.name,
            email=current_user.email,
            avatar_url=current_user.avatar_url,
            sso_role=current_user.sso_role,
            employee_id=current_user.employee_id,
            org_unit_id=current_user.org_unit_id,
            roles=current_user.roles,
            permissions=current_user.permissions,
            is_active=current_user.is_active,
        )

    async def refresh_user_cache(self, user_id: int) -> RefreshCacheResponse:
        """Refresh user cache - deprecated, no-op."""
        return RefreshCacheResponse(
            user_id=user_id,
            refreshed=False,
            note="Caching disabled - data comes from SSO"
        )

    async def get_token_info(self, token: str) -> TokenInfoResponse:
        """Get token info - minimal implementation."""
        from jose import jwt
        
        try:
            payload = jwt.get_unverified_claims(token)
            return TokenInfoResponse(
                user_id=payload.get("sub"),
                jti=payload.get("jti"),
                exp=payload.get("exp"),
                is_blacklisted=False,  # SSO handles this
            )
        except Exception:
            return TokenInfoResponse()
