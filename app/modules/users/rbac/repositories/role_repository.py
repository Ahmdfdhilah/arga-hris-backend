"""
Role Repository - Combined read/write operations for backward compatibility

This is a shim that combines RoleQueries and RoleCommands for code that
imports RoleRepository directly. Prefer using RoleQueries/RoleCommands directly.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.users.rbac.models.role import Role
from app.modules.users.rbac.models.permission import Permission
from app.modules.users.rbac.models.user_role import UserRole
from app.modules.users.rbac.models.role_permission import RolePermission


class RoleRepository:
    """Combined repository for Role/Permission operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === Query methods ===

    async def get_user_roles(self, user_id: str) -> List[str]:
        """Get list of role names for a user"""
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get list of permission codes for a user"""
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

    # === Command methods ===

    async def assign_role(self, user_id: str, role_id: int) -> None:
        """Assign a role to a user"""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()

    async def remove_role(self, user_id: str, role_id: int) -> None:
        """Remove a role from a user"""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()
