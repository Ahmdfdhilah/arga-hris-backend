"""
Auth Module Dependencies

Dependency injection for auth-related services and repositories.
"""

from typing import Annotated
from fastapi import Depends

from app.core.dependencies.database import get_db, get_redis
from app.modules.auth.repositories.token_repository import TokenRepository
from app.modules.auth.repositories.user_cache_repository import UserCacheRepository
from app.modules.auth.services.token_service import TokenService
from app.modules.auth.services.auth_service import AuthService
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.guests.repositories.guest_repository import GuestRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient


# Repository Dependencies

def get_token_repository(
    redis=Depends(get_redis),
) -> TokenRepository:
    """Get TokenRepository instance"""
    return TokenRepository(redis)


def get_user_cache_repository(
    redis=Depends(get_redis),
) -> UserCacheRepository:
    """Get UserCacheRepository instance"""
    return UserCacheRepository(redis)


# Service Dependencies

def get_token_service(
    token_repo: TokenRepository = Depends(get_token_repository),
) -> TokenService:
    """Get TokenService instance"""
    return TokenService(token_repo)


def get_auth_service(
    token_service: TokenService = Depends(get_token_service),
    user_cache_repo: UserCacheRepository = Depends(get_user_cache_repository),
    db=Depends(get_db),
) -> AuthService:
    """Get AuthService instance"""
    user_repo = UserRepository(db)
    guest_repo = GuestRepository(db)
    role_repo = RoleRepository(db)
    employee_grpc_client = EmployeeGRPCClient()
    org_unit_client = OrgUnitGRPCClient()
    return AuthService(token_service, user_cache_repo, user_repo, guest_repo, role_repo, employee_grpc_client, org_unit_client)


# Type Aliases for cleaner dependency injection

TokenRepositoryDep = Annotated[TokenRepository, Depends(get_token_repository)]
UserCacheRepositoryDep = Annotated[UserCacheRepository, Depends(get_user_cache_repository)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
