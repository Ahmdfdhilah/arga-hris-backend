"""
Use Case: List Roles

Get all available roles.
"""

from typing import List

from app.modules.users.rbac.repositories import RoleQueries
from app.modules.users.rbac.schemas.responses import RoleResponse


class ListRolesUseCase:
    """List all roles."""

    def __init__(self, role_queries: RoleQueries):
        self.role_queries = role_queries

    async def execute(self) -> List[RoleResponse]:
        """Execute list roles."""
        roles = await self.role_queries.get_all_roles()
        return [RoleResponse.model_validate(role) for role in roles]
