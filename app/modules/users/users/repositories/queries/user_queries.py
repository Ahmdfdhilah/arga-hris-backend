"""
User Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta

from app.modules.users.users.models.user import User


class UserQueries:
    """Read operations for User model (SSO replica)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (UUID from SSO)"""
        result = await self.db.execute(select(User).where(User.id == user_id))
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
    ) -> Tuple[List[User], int]:
        offset = (page - 1) * limit
        stmt = select(User)

        # Build filters
        conditions = []
        if is_active is not None:
            conditions.append(User.is_active.is_(is_active))
        if search:
            pattern = f"%{search}%"
            conditions.append(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await self.db.execute(count_stmt)).scalar_one()

        # Data query
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        users = list(result.scalars().all())

        return users, total_items

    async def get_by_ids(self, user_ids: List[str]) -> List[User]:
        """Get multiple users by IDs"""
        if not user_ids:
            return []
        result = await self.db.execute(select(User).where(User.id.in_(user_ids)))
        return list(result.scalars().all())

    async def get_users_needing_sync(self, older_than_hours: int = 24) -> List[User]:
        threshold = datetime.utcnow() - timedelta(hours=older_than_hours)
        stmt = (
            select(User)
            .where(or_(User.synced_at.is_(None), User.synced_at < threshold))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
