"""
Use Case: Assign Multiple Roles

Assign multiple roles ke user sekaligus.
"""

from typing import List

from app.modules.users.rbac.repositories import RoleQueries, RoleCommands
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.schemas.responses import MultipleRoleAssignmentResponse
from app.core.exceptions import NotFoundException


class AssignMultipleRolesUseCase:
    """Assign multiple roles to user."""

    def __init__(
        self,
        role_queries: RoleQueries,
        role_commands: RoleCommands,
        user_queries: UserQueries,
    ):
        self.role_queries = role_queries
        self.role_commands = role_commands
        self.user_queries = user_queries

    async def execute(
        self, user_id: str, role_names: List[str]
    ) -> MultipleRoleAssignmentResponse:
        """Execute multiple role assignment."""
        # Validate user exists
        user = await self.user_queries.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        # Validate all roles exist and assign
        for role_name in role_names:
            role = await self.role_queries.get_role_by_name(role_name)
            if not role:
                raise NotFoundException(f"Role '{role_name}' tidak ditemukan")
            await self.role_commands.assign_role(user_id, role.id)

        return MultipleRoleAssignmentResponse(user_id=user_id, roles=role_names)
