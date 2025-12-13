"""
User Repository - Profile data replica from SSO

Stores user profile data synced from SSO Master.
Employee relationship is now the other direction: Employee.user_id → User.id
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime
from app.core.repositories.base_repository import BaseRepository
from app.modules.users.users.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_sso_id(self, sso_id: str) -> Optional[User]:
        """Get user by SSO ID (UUID string)."""
        return await self.get_by(sso_id=sso_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.get_by(email=email)

    async def create_from_sso_response(
        self,
        sso_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        avatar_path: Optional[str] = None,
    ) -> User:
        """Create user from SSO response data (immediate sync)."""
        user_data = {
            "sso_id": sso_id,
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "avatar_path": avatar_path,
            "is_active": True,
            "synced_at": datetime.utcnow(),
        }
        return await self.create(user_data)

    async def sync_from_sso(
        self,
        sso_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        avatar_path: Optional[str] = None,
    ) -> User:
        """
        Sync user from SSO - upsert operation.
        Creates if not exists, updates if exists.
        """
        existing = await self.get_by_sso_id(sso_id)
        
        update_data = {"synced_at": datetime.utcnow()}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if gender is not None:
            update_data["gender"] = gender
        if avatar_path is not None:
            update_data["avatar_path"] = avatar_path
        
        if existing:
            return await self.update(existing.id, update_data)
        else:
            update_data["sso_id"] = sso_id
            update_data["is_active"] = True
            if name is None:
                update_data["name"] = ""  # Required field
            return await self.create(update_data)

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
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of users."""
        offset = (page - 1) * limit

        stmt = select(User)
        count_stmt = select(func.count(User.id))

        filters = []

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

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
        if not sso_ids:
            return []
        stmt = select(User).where(User.sso_id.in_(sso_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_users_needing_sync(self, older_than_hours: int = 24) -> List[User]:
        """Get users that haven't been synced recently."""
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        stmt = select(User).where(
            or_(
                User.synced_at.is_(None),
                User.synced_at < threshold
            )
        ).where(User.is_active == True)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
