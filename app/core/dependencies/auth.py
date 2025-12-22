"""Authorization and permission checking for HRIS Service.

Hybrid approach:
- Local JWT validation with public key from JWKS (fast, cached)
- gRPC to SSO only for JIT provisioning (first-time user)
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from app.config.settings import settings
from app.core.schemas import CurrentUser
from app.core.exceptions import UnauthorizedException
from app.core.utils.logging import get_logger
from app.core.security.jwks_client import get_jwks_client

logger = get_logger(__name__)


def _get_public_key() -> str:
    """Get public key from JWKS client (cached, with fallback)."""
    return get_jwks_client().get_public_key()


def _verify_token_locally(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, _get_public_key(), algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        token_client_id = payload.get("client_id")
        if token_client_id != settings.CLIENT_ID:
            raise UnauthorizedException(
                f"Token not valid for this application. Expected '{settings.CLIENT_ID}', got '{token_client_id}'"
            )

        return payload
    except JWTError as e:
        raise UnauthorizedException(f"Invalid token: {str(e)}")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )


jwt_bearer = JWTBearer()


async def get_current_user(
    token: str = Depends(jwt_bearer),
) -> CurrentUser:
    """
    Get current user with local JWT validation (hybrid approach).

    1. Validate token locally with public key (no network call)
    2. Find/create HRIS user by id (SSO UUID)
    3. Get HRIS-specific roles/permissions
    """
    from app.modules.users.users.repositories import UserQueries, UserCommands
    from app.modules.users.rbac.repositories import RoleQueries, RoleCommands
    from app.modules.employees.repositories import EmployeeQueries
    from app.config.database import get_db_context

    try:
        payload = _verify_token_locally(token)

        user_id = payload.get("sub")  
        if not user_id:
            raise UnauthorizedException("Token missing user ID")

        sso_user = {
            "id": user_id,
            "name": payload.get("name"),
            "role": payload.get("role", "user"),
            "email": None,
            "avatar_url": None,
        }

        async with get_db_context() as db:
            user_queries = UserQueries(db)
            user_commands = UserCommands(db)
            role_queries = RoleQueries(db)
            role_commands = RoleCommands(db)
            employee_queries = EmployeeQueries(db)

            user = await user_queries.get_by_id(user_id)  

            if not user:
                user = await _create_hris_user(
                    user_commands, role_queries, role_commands, user_id, sso_user
                )
                await db.commit()

            if not user.is_active:
                raise UnauthorizedException("Akun pengguna tidak aktif di HRIS")

            user_roles = await role_queries.get_user_roles(user.id)
            user_permissions = await role_queries.get_user_permissions(user.id)

            employee = await employee_queries.get_by_user_id(user.id)

            return CurrentUser(
                id=user.id,  
                employee_id=employee.id if employee else None,
                org_unit_id=employee.org_unit_id if employee else None,
                name=sso_user.get("name") or "",
                email=sso_user.get("email"),
                avatar_url=sso_user.get("avatar_url"),
                sso_role=sso_user.get("role", "user"),
                roles=user_roles or [],
                permissions=user_permissions or [],
                is_active=user.is_active,
            )

    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _create_hris_user(
    user_commands, role_queries, role_commands, user_id: str, sso_user: dict
):
    """Create HRIS user on first login (JIT provisioning)."""

    user = await user_commands.create_from_sso(
        sso_id=user_id,  
        name=sso_user.get("name") or "",
    )

    try:
        role = await role_queries.get_role_by_name("employee")
        if role:
            await role_commands.assign_role(user.id, role.id)
    except Exception as e:
        logger.warning(f"Failed to assign role to user {user.id}: {str(e)}")

    return user


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user
