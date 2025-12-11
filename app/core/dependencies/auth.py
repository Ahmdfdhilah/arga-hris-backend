"""Authorization and permission checking for HRIS Service."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.schemas import CurrentUser


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            return credentials
        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )


jwt_bearer = JWTBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(jwt_bearer),
) -> CurrentUser:
    """
    Get the current authenticated user from the token.

    This function:
    1. Verifies JWT token signature
    2. Checks if token is blacklisted (logout)
    3. Checks if user is globally revoked
    4. Fetches user data from cache or DB
    5. Returns complete user data with roles and permissions
    """
    token = credentials.credentials

    from app.modules.auth.services.auth_service import AuthService
    from app.modules.auth.services.token_service import TokenService
    from app.modules.auth.repositories.token_repository import TokenRepository
    from app.modules.auth.repositories.user_cache_repository import UserCacheRepository
    from app.modules.users.users.repositories.user_repository import UserRepository
    from app.modules.users.guests.repositories.guest_repository import GuestRepository
    from app.modules.users.rbac.repositories.role_repository import RoleRepository
    from app.external_clients.grpc.employee_client import EmployeeGRPCClient
    from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
    from app.config.database import get_db
    from app.config.redis import get_redis
    from app.core.exceptions import UnauthorizedException

    try:
        redis_gen = get_redis()
        redis = await redis_gen.__anext__()

        db_gen = get_db()
        db = await db_gen.__anext__()

        token_repo = TokenRepository(redis)
        user_cache_repo = UserCacheRepository(redis)
        token_service = TokenService(token_repo)
        user_repo = UserRepository(db)
        guest_repo = GuestRepository(db)
        role_repo = RoleRepository(db)
        employee_grpc_client = EmployeeGRPCClient()
        org_unit_client = OrgUnitGRPCClient()
        auth_service = AuthService(
            token_service,
            user_cache_repo,
            user_repo,
            guest_repo,
            role_repo,
            employee_grpc_client,
            org_unit_client,
        )

        user_data = await auth_service.get_current_user(token)
        return CurrentUser.model_validate(user_data)

    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
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
