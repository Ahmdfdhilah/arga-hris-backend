"""
User Query Repository - Read operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta

from app.modules.users.users.models.user import User


class UserQueries:
    """Read operations for User model (SSO replica)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_sso_id(self, sso_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.sso_id == sso_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        filters = []
        if is_active is not None:
            filters.append(User.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            filters.append(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        users = list(result.scalars().all())

        total_items = (await self.db.execute(count_stmt)).scalar() or 0
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
        if not sso_ids:
            return []
        result = await self.db.execute(select(User).where(User.sso_id.in_(sso_ids)))
        return list(result.scalars().all())

    async def get_users_needing_sync(self, older_than_hours: int = 24) -> List[User]:
        threshold = datetime.utcnow() - timedelta(hours=older_than_hours)
        stmt = select(User).where(
            or_(User.synced_at.is_(None), User.synced_at < threshold)
        ).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
