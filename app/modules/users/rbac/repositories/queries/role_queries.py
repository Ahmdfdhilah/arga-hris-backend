"""
Role Query Repository - Read operations
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.users.rbac.models.role import Role
from app.modules.users.rbac.models.permission import Permission
from app.modules.users.rbac.models.user_role import UserRole
from app.modules.users.rbac.models.role_permission import RolePermission


class RoleQueries:
    """Read operations for Role/Permission"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_roles(self, user_id: str) -> List[str]:
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: str) -> List[str]:
        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == role_name))
        return result.scalar_one_or_none()

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_all_roles(self) -> List[Role]:
        result = await self.db.execute(select(Role).order_by(Role.name))
        return list(result.scalars().all())

    async def get_all_permissions(self) -> List[Permission]:
        result = await self.db.execute(select(Permission).order_by(Permission.code))
        return list(result.scalars().all())
