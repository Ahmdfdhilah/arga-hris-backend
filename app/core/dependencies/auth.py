"""Authorization and permission checking for HRIS Service.

Hybrid approach:
- Local JWT validation with public key from JWKS (fast, cached)
- gRPC to SSO only for JIT provisioning (first-time user)
"""

from fastapi import Depends, HTTPException, status
from typing import Optional

from app.core.schemas import CurrentUser
from app.core.exceptions import UnauthorizedException
from app.core.utils.logging import get_logger
from app.core.security.jwt import jwt_bearer, verify_token_locally
from app.modules.users.users.use_cases.create_user_from_sso import (
    CreateUserFromSSOUseCase,
    CreateUserFromSSODTO,
)

logger = get_logger(__name__)


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
        payload = verify_token_locally(token)

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Token missing user ID")
        
        sso_name = payload.get("name")
        sso_role = payload.get("role", "user")
        sso_email = payload.get("email")
        sso_avatar = payload.get("avatar_url")

        async with get_db_context() as db:
            user_queries = UserQueries(db)
            user_commands = UserCommands(db)
            role_queries = RoleQueries(db)
            role_commands = RoleCommands(db)
            employee_queries = EmployeeQueries(db)

            user = await user_queries.get_by_id(user_id)

            if not user:
                use_case = CreateUserFromSSOUseCase(
                    user_commands, role_queries, role_commands
                )
                dto = CreateUserFromSSODTO(
                    id=user_id,
                    name=sso_name or "",
                    email=sso_email,
                    role=sso_role,
                    avatar_url=sso_avatar,
                )
                user = await use_case.execute(dto)
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
                name=sso_name or "",
                email=sso_email,
                avatar_url=sso_avatar,
                sso_role=sso_role,
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


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user
