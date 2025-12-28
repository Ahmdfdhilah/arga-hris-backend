"""
User Command Repository - Write operations
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.modules.users.users.models.user import User


class UserCommands:
    """Write operations for User model (SSO replica)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """Create new user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update user."""
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_from_sso(
        self,
        sso_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        avatar_path: Optional[str] = None,
    ) -> User:
        """Create user from SSO data. sso_id becomes user.id."""
        user = User(
            id=sso_id, 
            name=name,
            email=email,
            phone=phone,
            gender=gender,
            avatar_path=avatar_path,
            is_active=True,
            synced_at=datetime.utcnow(),
        )
        return await self.create(user)

    async def sync_from_sso(
        self,
        sso_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        avatar_path: Optional[str] = None,
    ) -> User:
        """Sync user from SSO (upsert). sso_id is the user.id."""
        from app.modules.users.users.repositories.queries import UserQueries

        queries = UserQueries(self.db)
        existing = await queries.get_by_id(sso_id)  

        if existing:
            existing.synced_at = datetime.utcnow()
            if name is not None:
                existing.name = name
            if email is not None:
                existing.email = email
            if phone is not None:
                existing.phone = phone
            if gender is not None:
                existing.gender = gender
            if avatar_path is not None:
                existing.avatar_path = avatar_path
            return await self.update(existing)
        else:
            new_user = User(
                id=sso_id,
                name=name if name is not None else "",
                email=email,
                phone=phone,
                gender=gender,
                avatar_path=avatar_path,
                is_active=True,
                synced_at=datetime.utcnow(),
            )
            return await self.create(new_user)

    async def deactivate(self, user_id: str) -> Optional[User]:
        """Deactivate user by ID."""
        from app.modules.users.users.repositories.queries import UserQueries

        queries = UserQueries(self.db)
        user = await queries.get_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        return await self.update(user)

    async def activate(self, user_id: str) -> Optional[User]:
        """Activate user by ID."""
        from app.modules.users.users.repositories.queries import UserQueries

        queries = UserQueries(self.db)
        user = await queries.get_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        return await self.update(user)
