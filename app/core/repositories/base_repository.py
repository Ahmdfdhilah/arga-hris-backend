from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    def _get_id_column(self) -> Any:
        """Helper to get id column with proper typing"""
        return cast(Any, self.model).id

    async def get(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self._get_id_column() == id)
        )
        return result.scalar_one_or_none()

    async def get_by(self, **filters) -> Optional[ModelType]:
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        query = select(self.model)

        if filters:
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = select(func.count(self._get_id_column()))

        if filters:
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = cast(ModelType, cast(Any, self.model)(**obj_in))
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        await self.db.execute(
            update(self.model)
            .where(self._get_id_column() == id)
            .values(**obj_in)
        )
        await self.db.commit()
        return await self.get(id)

    async def delete(self, id: Any) -> bool:
        result = await self.db.execute(
            delete(self.model).where(self._get_id_column() == id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def exists(self, **filters) -> bool:
        query = select(func.count(self._get_id_column()))
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar_one() > 0
