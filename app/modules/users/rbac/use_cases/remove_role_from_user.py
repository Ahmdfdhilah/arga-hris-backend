"""
Use Case: Remove Role from User

Remove role dari user berdasarkan nama role.
"""

from app.modules.users.rbac.repositories import RoleQueries, RoleCommands
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.schemas.responses import RoleAssignmentResponse
from app.core.exceptions import NotFoundException


class RemoveRoleFromUserUseCase:
    """Remove role from user."""

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
        self, user_id: str, role_name: str
    ) -> RoleAssignmentResponse:
        """Execute role removal."""
        user = await self.user_queries.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")
        role = await self.role_queries.get_role_by_name(role_name)
        if not role:
            raise NotFoundException(f"Role '{role_name}' tidak ditemukan")

        await self.role_commands.remove_role(user_id, role.id)

        return RoleAssignmentResponse(user_id=user_id, role_name=role_name)
