"""
Role Command Repository - Write operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.users.rbac.models.user_role import UserRole


class RoleCommands:
    """Write operations for Role/Permission"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_role(self, user_id: str, role_id: int) -> None:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()

    async def remove_role(self, user_id: str, role_id: int) -> None:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()
