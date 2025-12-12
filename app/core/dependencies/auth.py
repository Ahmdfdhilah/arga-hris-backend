"""Authorization and permission checking for HRIS Service.

Uses SSO gRPC for token validation - all auth is delegated to SSO service.
User profile data comes from SSO, HRIS only stores linking data.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.schemas import CurrentUser
from app.core.exceptions import UnauthorizedException
from app.core.utils.logging import get_logger

logger = get_logger(__name__)


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
    Get the current authenticated user via SSO gRPC.

    Flow:
    1. Validate token via SSO gRPC → Get user profile + SSO role
    2. Find/create HRIS user by sso_id → Get employee_id
    3. Get HRIS-specific roles/permissions
    4. Return combined CurrentUser
    """
    from app.external_clients.grpc.sso_client import SSOAuthGRPCClient
    from app.modules.users.users.repositories.user_repository import UserRepository
    from app.modules.users.rbac.repositories.role_repository import RoleRepository
    from app.external_clients.grpc.employee_client import EmployeeGRPCClient
    from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
    from app.config.database import get_db

    try:
        # Step 1: Validate token via SSO gRPC
        sso_client = SSOAuthGRPCClient()
        validation_result = await sso_client.validate_token(token)

        if not validation_result.get("is_valid"):
            error_msg = validation_result.get("error", "Token tidak valid")
            raise UnauthorizedException(error_msg)

        sso_user = validation_result.get("user")
        if not sso_user:
            raise UnauthorizedException("Token valid tapi data user tidak ditemukan")

        # Extract SSO user data
        sso_id = sso_user.get("id")
        if not sso_id:
            raise UnauthorizedException("Token tidak memiliki identitas pengguna")

        # Step 2: Find or create HRIS user
        db_gen = get_db()
        db = await db_gen.__anext__()

        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        employee_client = EmployeeGRPCClient()
        org_unit_client = OrgUnitGRPCClient()

        user = await user_repo.get_by_sso_id(sso_id)

        if not user:
            # JIT provisioning - create HRIS user
            user = await _create_hris_user(
                user_repo, role_repo, employee_client, org_unit_client,
                sso_id, sso_user
            )
            await db.commit()

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedException("Akun pengguna tidak aktif di HRIS")

        # Step 3: Get HRIS-specific roles and permissions
        user_roles = await role_repo.get_user_roles(user.id)
        user_permissions = await role_repo.get_user_permissions(user.id)

        # Step 4: Build CurrentUser from SSO + HRIS data
        return CurrentUser(
            # HRIS data
            id=user.id,
            employee_id=user.employee_id,
            org_unit_id=user.org_unit_id,
            # SSO data
            sso_id=sso_id,
            name=sso_user.get("name") or "",
            email=sso_user.get("email"),
            avatar_url=sso_user.get("avatar_url"),
            sso_role=sso_user.get("role", "user"),
            # HRIS RBAC
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
    
    # Create user with just sso_id
    user = await user_repo.create_from_sso(sso_id=sso_id)

    # Assign default role
    try:
        role = await role_repo.get_role_by_name("employee")
        if role:
            await role_repo.assign_role(user.id, role.id)
    except Exception as e:
        logger.warning(f"Failed to assign role to user {user.id}: {str(e)}")

    # Try to auto-link to employee by email from SSO
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
