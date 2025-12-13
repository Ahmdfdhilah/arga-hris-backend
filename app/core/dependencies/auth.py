"""Authorization and permission checking for HRIS Service.

Hybrid approach:
- Local JWT validation with public key (fast, no network)
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

logger = get_logger(__name__)

_public_key: Optional[str] = None


def _load_public_key() -> str:
    global _public_key
    if _public_key is None:
        with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
            _public_key = f.read()
    return _public_key


def _verify_token_locally(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")
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
    2. Find/create HRIS user by sso_id
    3. Get HRIS-specific roles/permissions
    """
    from app.modules.users.users.repositories.user_repository import UserRepository
    from app.modules.users.rbac.repositories.role_repository import RoleRepository
    from app.external_clients.grpc.employee_client import EmployeeGRPCClient
    from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
    from app.config.database import get_db

    try:
        payload = _verify_token_locally(token)
        
        sso_id = payload.get("sub")
        if not sso_id:
            raise UnauthorizedException("Token missing user ID")
        
        sso_user = {
            "id": sso_id,
            "name": payload.get("name"),
            "role": payload.get("role", "user"),
            "email": None,
            "avatar_url": None,
        }
        
        db_gen = get_db()
        db = await db_gen.__anext__()

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        employee_client = EmployeeGRPCClient()
        org_unit_client = OrgUnitGRPCClient()

        user = await user_repo.get_by_sso_id(sso_id)

        if not user:
            user = await _create_hris_user(
                user_repo, role_repo, employee_client, org_unit_client,
                sso_id, sso_user
            )
            await db.commit()

        if not user.is_active:
            raise UnauthorizedException("Akun pengguna tidak aktif di HRIS")

        user_roles = await role_repo.get_user_roles(user.id)
        user_permissions = await role_repo.get_user_permissions(user.id)

        return CurrentUser(
            id=user.id,
            employee_id=user.employee_id,
            org_unit_id=user.org_unit_id,
            sso_id=sso_id,
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


async def _create_hris_user(user_repo, role_repo, employee_client, org_unit_client, sso_id: str, sso_user: dict):
    """Create HRIS user on first login (JIT provisioning)."""
    
    user = await user_repo.create_from_sso(sso_id=sso_id)

    try:
        role = await role_repo.get_role_by_name("employee")
        if role:
            await role_repo.assign_role(user.id, role.id)
    except Exception as e:
        logger.warning(f"Failed to assign role to user {user.id}: {str(e)}")

    email = sso_user.get("email")
    if email:
        try:
            employee_data = await employee_client.get_employee_by_email(email)
            if employee_data:
                employee_id = int(employee_data.get("id"))
                org_unit_id = employee_data.get("org_unit_id")
                
                # Check if this employee is already linked to another user
                existing = await user_repo.get_by_employee_id(employee_id)
                if not existing:
                    await user_repo.link_employee(user.id, employee_id, org_unit_id)
                    user.employee_id = employee_id
                    user.org_unit_id = org_unit_id
                    logger.info(f"User {user.id} linked to employee {employee_id}")

                    # Check if org unit head
                    await _check_and_assign_org_unit_head_role(
                        role_repo, org_unit_client, user.id, employee_id
                    )
        except Exception as e:
            logger.warning(f"Failed to auto-link employee: {str(e)}")

    return user


async def _check_and_assign_org_unit_head_role(role_repo, org_unit_client, user_id: int, employee_id: int):
    """Check if employee is org unit head and assign role."""
    try:
        result = await org_unit_client.list_org_units(page=1, limit=1000, is_active=True)
        org_units = result.get("org_units", [])

        for org_unit in org_units:
            if org_unit.get("head_id") == employee_id:
                org_unit_head_role = await role_repo.get_role_by_name("org_unit_head")
                if org_unit_head_role:
                    await role_repo.assign_role(user_id, org_unit_head_role.id)
                    logger.info(f"Org unit head role assigned to user {user_id}")
                break
    except Exception as e:
        logger.warning(f"Failed to check/assign org unit head role: {str(e)}")


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user
