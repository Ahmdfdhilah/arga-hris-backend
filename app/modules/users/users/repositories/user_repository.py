"""User Repository - Simplified for SSO integration"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.repositories.base_repository import BaseRepository
from app.modules.users.users.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_sso_id(self, sso_id: str) -> Optional[User]:
        """Get user by SSO ID (UUID string)."""
        return await self.get_by(sso_id=sso_id)

    async def get_by_employee_id(self, employee_id: int) -> Optional[User]:
        """Get user by employee ID."""
        return await self.get_by(employee_id=employee_id)

    async def create_from_sso(self, sso_id: str, employee_id: Optional[int] = None) -> User:
        """Create user from SSO login."""
        user_data = {
            "sso_id": sso_id,
            "employee_id": employee_id,
            "is_active": True,
        }
        return await self.create(user_data)

    async def link_employee(self, user_id: int, employee_id: int, org_unit_id: Optional[int] = None) -> Optional[User]:
        """Link user to employee."""
        update_data = {"employee_id": employee_id}
        if org_unit_id:
            update_data["org_unit_id"] = org_unit_id
        return await self.update(user_id, update_data)

    async def unlink_employee(self, user_id: int) -> Optional[User]:
        """Unlink user from employee."""
        return await self.update(user_id, {"employee_id": None, "org_unit_id": None})

    async def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate user."""
        return await self.update(user_id, {"is_active": False})

    async def activate(self, user_id: int) -> Optional[User]:
        """Activate user."""
        return await self.update(user_id, {"is_active": True})

    async def list_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        is_active: Optional[bool] = None,
        has_employee: Optional[bool] = None,
        org_unit_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of users."""
        offset = (page - 1) * limit

        stmt = select(User)
        count_stmt = select(func.count(User.id))

        filters = []

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if has_employee is not None:
            if has_employee:
                filters.append(User.employee_id.isnot(None))
            else:
                filters.append(User.employee_id.is_(None))

        if org_unit_id is not None:
            filters.append(User.org_unit_id == org_unit_id)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        users = list(result.scalars().all())

        count_result = await self.db.execute(count_stmt)
        total_items = count_result.scalar() or 0

        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

        return {
            "users": users,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages,
            },
        }

    async def get_by_sso_ids(self, sso_ids: List[str]) -> List[User]:
        """Get users by multiple SSO IDs."""
        stmt = select(User).where(User.sso_id.in_(sso_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
