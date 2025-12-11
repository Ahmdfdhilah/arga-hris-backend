from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, cast, String
from app.core.repositories.base_repository import BaseRepository
from app.modules.users.users.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by(email=email)

    async def get_by_sso_id(self, sso_id: int) -> Optional[User]:
        return await self.get_by(sso_id=sso_id)

    async def get_by_employee_id(self, employee_id: int) -> Optional[User]:
        return await self.get_by(employee_id=employee_id)

    async def create_user(
        self,
        sso_id: int,
        email: str,
        first_name: str,
        last_name: str,
        employee_id: Optional[int] = None,
    ) -> User:
        user_data = {
            "sso_id": sso_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "employee_id": employee_id,
            "is_active": True,
        }
        return await self.create(user_data)

    async def update_user(
        self,
        user_id: int,
        **kwargs,
    ) -> Optional[User]:
        return await self.update(user_id, kwargs)

    async def link_employee(self, user_id: int, employee_id: int) -> Optional[User]:
        return await self.update(user_id, {"employee_id": employee_id})

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        return await self.update(user_id, {"is_active": False})

    async def activate_user(self, user_id: int) -> Optional[User]:
        return await self.update(user_id, {"is_active": True})

    async def list_users_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_employee: Optional[bool] = None,
        org_unit_id: Optional[int] = None,
        account_type: Optional[str] = None,
        exclude_deleted_employees: bool = True,
    ) -> Dict[str, Any]:
        """
        Get paginated list of users with filters

        Args:
            page: Page number (1-based)
            limit: Items per page
            search: Search query (email, first_name, last_name)
            is_active: Filter by active status
            has_employee: Filter by employee linkage (True: has employee_id, False: no employee_id)
            org_unit_id: Filter by org unit ID
            account_type: Filter by account type (regular/guest)

        Returns:
            Dict with 'users' and 'pagination' keys
        """
        offset = (page - 1) * limit

        # Build base query
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        # Apply filters
        filters = []

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

        if has_employee is not None:
            if has_employee:
                filters.append(User.employee_id.isnot(None))
            else:
                filters.append(User.employee_id.is_(None))

        if org_unit_id is not None:
            filters.append(User.org_unit_id == org_unit_id)

        if account_type is not None:
            filters.append(User.account_type == account_type)

        # Exclude users whose employees are soft-deleted
        if exclude_deleted_employees:
            filters.append(User.employee_deleted_at.is_(None))

        # Apply filters to both queries
        if filters:
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
