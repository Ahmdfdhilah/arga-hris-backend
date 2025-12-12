"""
Auth Module Dependencies - Simplified for SSO Integration

Most auth logic is now in core/dependencies/auth.py which calls SSO gRPC.
This module provides AuthService for additional operations.
"""

from typing import Annotated
from fastapi import Depends

from app.core.dependencies.database import get_db
from app.modules.auth.services.auth_service import AuthService
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient


def get_auth_service(
    db=Depends(get_db),
) -> AuthService:
    """Get AuthService instance"""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    employee_grpc_client = EmployeeGRPCClient()
    org_unit_client = OrgUnitGRPCClient()
    return AuthService(user_repo, role_repo, employee_grpc_client, org_unit_client)


# Type Alias for dependency injection
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
