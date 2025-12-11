from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.users.rbac.models.role import Role
from app.modules.users.rbac.models.permission import Permission
from app.modules.users.rbac.models.user_role import UserRole
from app.modules.users.rbac.models.role_permission import RolePermission


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Get list of role names for a user"""
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        roles = result.scalars().all()
        return list(roles)

    async def get_user_permissions(self, user_id: int) -> List[str]:
        """Get list of permission codes for a user (flattened from all roles)"""
        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self.db.execute(stmt)
        permissions = result.scalars().all()
        return list(permissions)

    async def assign_role(self, user_id: int, role_id: int) -> None:
        """Assign a role to a user"""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()

    async def remove_role(self, user_id: int, role_id: int) -> None:
        """Remove a role from a user"""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name"""
        stmt = select(Role).where(Role.name == role_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        stmt = select(Role).order_by(Role.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions"""
        stmt = select(Permission).order_by(Permission.code)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
