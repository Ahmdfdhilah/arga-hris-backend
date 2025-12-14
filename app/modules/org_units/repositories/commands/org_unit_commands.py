"""
OrgUnit Command Repository - Write operations
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.datetime import get_utc_now
from app.modules.org_units.models.org_unit import OrgUnit


class OrgUnitCommands:
    """Write operations for OrgUnit model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_unit: OrgUnit) -> OrgUnit:
        self.db.add(org_unit)
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit

    async def update(self, org_unit: OrgUnit) -> OrgUnit:
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit

    async def delete(self, org_unit_id: int, user_id: int) -> bool:
        from app.modules.org_units.repositories.queries import OrgUnitQueries
        
        queries = OrgUnitQueries(self.db)
        org_unit = await queries.get_by_id(org_unit_id)
        if not org_unit:
            return False

        org_unit.deleted_at = get_utc_now()
        org_unit.deleted_by = user_id
        org_unit.is_active = False
        await self.db.commit()
        return True

    async def hard_delete(self, org_unit_id: int) -> bool:
        from app.modules.org_units.repositories.queries import OrgUnitQueries
        
        queries = OrgUnitQueries(self.db)
        org_unit = await queries.get_by_id_with_deleted(org_unit_id)
        if not org_unit:
            return False

        await self.db.delete(org_unit)
        await self.db.commit()
        return True

    async def restore(self, org_unit_id: int) -> Optional[OrgUnit]:
        from app.modules.org_units.repositories.queries import OrgUnitQueries
        
        queries = OrgUnitQueries(self.db)
        org_unit = await queries.get_by_id_with_deleted(org_unit_id)
        if not org_unit or not org_unit.is_deleted():
            return None

        if org_unit.parent_id:
            parent = await queries.get_by_id_with_deleted(org_unit.parent_id)
            if parent and parent.is_deleted():
                return None

        org_unit.deleted_at = None
        org_unit.deleted_by = None
        org_unit.is_active = True
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit
