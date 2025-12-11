from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.modules.users.users.models.user import User
from app.modules.users.guests.models.guest_account import GuestAccount


class GuestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_guest_users_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Get paginated list of guest users with guest_account eager loaded

        Args:
            page: Page number (1-based)
            limit: Items per page
            search: Search query (email, first_name, last_name)
            is_active: Filter by active status

        Returns:
            Dict with 'users' and 'pagination' keys
        """
        offset = (page - 1) * limit

        # Build base query with eager loading of guest_account
        stmt = select(User).options(selectinload(User.guest_account))
        count_stmt = select(func.count(User.id))

        # Apply filters
        filters = [User.account_type == "guest"]

        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                )
            )

        if is_active is not None:
            filters.append(User.is_active == is_active)

        # Apply filters to both queries
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))

        # Add ordering and pagination
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)

        # Execute queries
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

    async def create_guest_account(self, guest_account_data: Dict[str, Any]) -> GuestAccount:
        """Create a guest account"""
        guest_account = GuestAccount(**guest_account_data)
        self.db.add(guest_account)
        await self.db.commit()
        await self.db.refresh(guest_account)
        return guest_account

    async def get_guest_account_by_user_id(self, user_id: int) -> Optional[GuestAccount]:
        """Get guest account by user_id"""
        stmt = select(GuestAccount).where(GuestAccount.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_guest_account(self, user_id: int) -> Optional[User]:
        """Get user with guest account relationship loaded"""
        stmt = select(User).options(selectinload(User.guest_account)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_guest_account(self, user_id: int, update_data: Dict[str, Any]) -> Optional[GuestAccount]:
        """Update guest account"""
        guest_account = await self.get_guest_account_by_user_id(user_id)
        if not guest_account:
            return None

        for key, value in update_data.items():
            if hasattr(guest_account, key) and value is not None:
                setattr(guest_account, key, value)

        await self.db.commit()
        await self.db.refresh(guest_account)
        return guest_account
