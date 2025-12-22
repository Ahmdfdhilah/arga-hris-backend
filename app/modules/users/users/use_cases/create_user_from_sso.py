"""
Use Case for creating user from SSO data (JIT Provisioning).
"""

from dataclasses import dataclass
from typing import Optional

from app.core.utils.logging import get_logger
from app.modules.users.users.models import User
from app.modules.users.users.repositories import UserCommands
from app.modules.users.rbac.repositories import RoleQueries, RoleCommands


logger = get_logger(__name__)


@dataclass
class CreateUserFromSSODTO:
    id: str  # SSO ID
    name: str
    email: Optional[str] = None
    role: str = "user"  # SSO Role
    avatar_url: Optional[str] = None


class CreateUserFromSSOUseCase:
    def __init__(
        self,
        user_commands: UserCommands,
        role_queries: RoleQueries,
        role_commands: RoleCommands,
    ):
        self.user_commands = user_commands
        self.role_queries = role_queries
        self.role_commands = role_commands

    async def execute(self, data: CreateUserFromSSODTO) -> User:
        """
        Create HRIS user from SSO data.
        
        1. Creates basic user record
        2. Assigns default 'employee' role
        """
        # Create user
        user = await self.user_commands.create_from_sso(
            sso_id=data.id,
            name=data.name,
            email=data.email,
            avatar_path=data.avatar_url,
        )

        try:
            role = await self.role_queries.get_role_by_name("employee")
            if role:
                await self.role_commands.assign_role(user.id, role.id)
            else:
                logger.warning("Default role 'employee' not found during JIT provisioning")
        except Exception as e:
            logger.warning(f"Failed to assign role to user {user.id}: {str(e)}")

        return user
