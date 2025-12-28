"""
Use Case: Get User Roles & Permissions

Get list roles dan permissions yang dimiliki user.
"""

from app.modules.users.rbac.repositories import RoleQueries
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.schemas.responses import UserRolesPermissionsResponse
from app.core.exceptions import NotFoundException


class GetUserRolesPermissionsUseCase:
    """Get user roles and permissions."""

    def __init__(
        self,
        role_queries: RoleQueries,
        user_queries: UserQueries,
    ):
        self.role_queries = role_queries
        self.user_queries = user_queries

    async def execute(self, user_id: str) -> UserRolesPermissionsResponse:
        """Execute get user roles & permissions."""
        # Validate user exists
        user = await self.user_queries.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        # Get roles and permissions
        roles = await self.role_queries.get_user_roles(user_id)
        permissions = await self.role_queries.get_user_permissions(user_id)

        return UserRolesPermissionsResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.name,  # User model has 'name' not 'full_name'
            roles=roles,
            permissions=permissions,
        )
