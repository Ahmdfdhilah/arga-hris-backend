"""
Role Service - Facade for RBAC use cases
"""

from typing import List

from app.modules.users.rbac.repositories import RoleQueries, RoleCommands
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.use_cases import (
    AssignRoleToUserUseCase,
    RemoveRoleFromUserUseCase,
    AssignMultipleRolesUseCase,
    GetUserRolesPermissionsUseCase,
    ListRolesUseCase,
    ListPermissionsUseCase,
)
from app.modules.users.rbac.schemas.responses import (
    RoleResponse,
    PermissionResponse,
    UserRolesPermissionsResponse,
    RoleAssignmentResponse,
    MultipleRoleAssignmentResponse,
)
from app.core.schemas import DataResponse, create_success_response


class RoleService:
    """Facade for RBAC operations"""

    def __init__(
        self,
        role_queries: RoleQueries,
        role_commands: RoleCommands,
        user_queries: UserQueries,
    ):
        # Initialize use cases
        self.assign_role_uc = AssignRoleToUserUseCase(
            role_queries, role_commands, user_queries
        )
        self.remove_role_uc = RemoveRoleFromUserUseCase(
            role_queries, role_commands, user_queries
        )
        self.assign_multiple_roles_uc = AssignMultipleRolesUseCase(
            role_queries, role_commands, user_queries
        )
        self.get_user_roles_permissions_uc = GetUserRolesPermissionsUseCase(
            role_queries, user_queries
        )
        self.list_roles_uc = ListRolesUseCase(role_queries)
        self.list_permissions_uc = ListPermissionsUseCase(role_queries)

    async def assign_role_by_name(
        self, user_id: str, role_name: str
    ) -> DataResponse[RoleAssignmentResponse]:
        """Assign role to user"""
        result = await self.assign_role_uc.execute(user_id, role_name)
        return create_success_response(
            message=f"Role '{role_name}' berhasil di-assign ke user", data=result
        )

    async def remove_role_by_name(
        self, user_id: str, role_name: str
    ) -> DataResponse[RoleAssignmentResponse]:
        """Remove role from user"""
        result = await self.remove_role_uc.execute(user_id, role_name)
        return create_success_response(
            message=f"Role '{role_name}' berhasil di-remove dari user", data=result
        )

    async def assign_multiple_roles(
        self, user_id: str, role_names: List[str]
    ) -> DataResponse[MultipleRoleAssignmentResponse]:
        """Assign multiple roles to user"""
        result = await self.assign_multiple_roles_uc.execute(user_id, role_names)
        return create_success_response(
            message="Multiple roles berhasil di-assign ke user", data=result
        )

    async def get_user_roles_and_permissions(
        self, user_id: str
    ) -> DataResponse[UserRolesPermissionsResponse]:
        """Get user roles and permissions"""
        result = await self.get_user_roles_permissions_uc.execute(user_id)
        return create_success_response(
            message="User roles dan permissions berhasil diambil", data=result
        )

    async def get_all_roles(self) -> DataResponse[List[RoleResponse]]:
        """Get all available roles"""
        result = await self.list_roles_uc.execute()
        return create_success_response(message="Roles berhasil diambil", data=result)

    async def get_all_permissions(self) -> DataResponse[List[PermissionResponse]]:
        """Get all available permissions"""
        result = await self.list_permissions_uc.execute()
        return create_success_response(
            message="Permissions berhasil diambil", data=result
        )
