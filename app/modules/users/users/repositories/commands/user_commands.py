"""
User Command Repository - Write operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.modules.users.users.models.user import User


class UserCommands:
    """Write operations for User model (SSO replica)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        from app.modules.users.users.repositories.queries import UserQueries
        
        queries = UserQueries(self.db)
        user = await queries.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in data.items():
            setattr(user, key, value)
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
        data = {
            "sso_id": sso_id,
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "avatar_path": avatar_path,
            "is_active": True,
            "synced_at": datetime.utcnow(),
        }
        return await self.create(data)

    async def sync_from_sso(
        self,
        sso_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        avatar_path: Optional[str] = None,
    ) -> User:
        from app.modules.users.users.repositories.queries import UserQueries
        
        queries = UserQueries(self.db)
        existing = await queries.get_by_sso_id(sso_id)

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
                update_data["name"] = ""
            return await self.create(update_data)

    async def deactivate(self, user_id: int) -> Optional[User]:
        return await self.update(user_id, {"is_active": False})

    async def activate(self, user_id: int) -> Optional[User]:
        return await self.update(user_id, {"is_active": True})
