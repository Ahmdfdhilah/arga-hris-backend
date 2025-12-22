"""
Use Case: List Permissions

Get all available permissions.
"""

from typing import List

from app.modules.users.rbac.repositories import RoleQueries
from app.modules.users.rbac.schemas.responses import PermissionResponse


class ListPermissionsUseCase:
    """List all permissions."""

    def __init__(self, role_queries: RoleQueries):
        self.role_queries = role_queries

    async def execute(self) -> List[PermissionResponse]:
        """Execute list permissions."""
        permissions = await self.role_queries.get_all_permissions()
        return [PermissionResponse.model_validate(perm) for perm in permissions]
