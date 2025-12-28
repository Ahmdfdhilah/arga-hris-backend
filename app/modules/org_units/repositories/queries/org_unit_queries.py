"""
OrgUnit Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.orm import selectinload

from app.modules.org_units.models.org_unit import OrgUnit


class OrgUnitQueries:
    """Read operations for OrgUnit model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_options(self):
        from app.modules.employees.models.employee import Employee

        return [
            selectinload(OrgUnit.parent),
            selectinload(OrgUnit.head).selectinload(Employee.user),
        ]

    async def get_by_id(self, org_unit_id: int) -> Optional[OrgUnit]:
        result = await self.db.execute(
            select(OrgUnit)
            .options(*self._base_options())
            .where(and_(OrgUnit.id == org_unit_id, OrgUnit.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, org_unit_id: int) -> Optional[OrgUnit]:
        result = await self.db.execute(
            select(OrgUnit)
            .options(*self._base_options())
            .where(OrgUnit.id == org_unit_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[OrgUnit]:
        result = await self.db.execute(
            select(OrgUnit)
            .options(*self._base_options())
            .where(and_(OrgUnit.code == code, OrgUnit.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        parent_id: Optional[int] = None,
        type_filter: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[OrgUnit], int]:
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_(None))

        if parent_id is not None:
            query = query.where(OrgUnit.parent_id == parent_id)
        if type_filter is not None:
            query = query.where(OrgUnit.type == type_filter)
        if is_active is not None:
            query = query.where(OrgUnit.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = query.options(*self._base_options()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_deleted(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[OrgUnit], int]:
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_not(None))

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.options(*self._base_options())
            .offset(skip)
            .limit(limit)
            .order_by(OrgUnit.deleted_at.desc())
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_children(
        self,
        parent_id: int,
        recursive: bool = False,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[OrgUnit], int]:
        if recursive:
            parent = await self.get_by_id(parent_id)
            if not parent:
                return [], 0  # Return empty tuple

            query = select(OrgUnit).where(
                and_(
                    OrgUnit.path.like(f"{parent.path}.%"),
                    OrgUnit.deleted_at.is_(None),
                )
            )
        else:
            query = select(OrgUnit).where(
                and_(OrgUnit.parent_id == parent_id, OrgUnit.deleted_at.is_(None))
            )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = query.options(*self._base_options()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_ancestors(self, org_unit_id: int) -> List[OrgUnit]:
        query = text("""
            WITH RECURSIVE ancestors AS (
                SELECT * FROM org_units WHERE id = :org_unit_id
                UNION ALL
                SELECT ou.* FROM org_units ou
                INNER JOIN ancestors a ON ou.id = a.parent_id
                WHERE ou.deleted_at IS NULL
            )
            SELECT id FROM ancestors WHERE id != :org_unit_id
        """)
        result = await self.db.execute(query, {"org_unit_id": org_unit_id})
        ancestor_ids = [row[0] for row in result.fetchall()]

        if not ancestor_ids:
            return []

        org_units_result = await self.db.execute(
            select(OrgUnit)
            .options(*self._base_options())
            .where(OrgUnit.id.in_(ancestor_ids))
            .order_by(OrgUnit.level)
        )
        return list(org_units_result.scalars().all())

    async def get_tree(
        self, root_id: Optional[int] = None, max_depth: int = 10
    ) -> List[OrgUnit]:
        query = (
            select(OrgUnit)
            .options(*self._base_options())
            .where(OrgUnit.deleted_at.is_(None))
        )

        if root_id is not None:
            root = await self.get_by_id(root_id)
            if not root:
                return []
            query = query.where(OrgUnit.path.like(f"{root.path}%"))

        if max_depth > 0:
            query = query.where(OrgUnit.level <= max_depth)

        query = query.order_by(OrgUnit.path)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_units_where_employee_is_head(self, employee_id: int) -> List[OrgUnit]:
        result = await self.db.execute(
            select(OrgUnit).where(
                and_(OrgUnit.head_id == employee_id, OrgUnit.deleted_at.is_(None))
            )
        )
        return list(result.scalars().all())

    async def is_head_of_any_unit(self, employee_id: int) -> bool:
        result = await self.db.execute(
            select(func.count(OrgUnit.id)).where(
                and_(OrgUnit.head_id == employee_id, OrgUnit.deleted_at.is_(None))
            )
        )
        return result.scalar_one() > 0

    async def get_unique_types(self) -> List[str]:
        result = await self.db.execute(
            select(OrgUnit.type)
            .where(
                and_(
                    OrgUnit.type.is_not(None),
                    OrgUnit.type != "",
                    OrgUnit.deleted_at.is_(None),
                )
            )
            .distinct()
        )
        return [row[0] for row in result.fetchall()]

    async def count_active_employees(self, org_unit_id: int) -> int:
        from app.modules.employees.models.employee import Employee

        result = await self.db.execute(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.org_unit_id == org_unit_id,
                    Employee.is_active.is_(True),
                    Employee.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one()

    async def count_active_children(self, org_unit_id: int) -> int:
        result = await self.db.execute(
            select(func.count(OrgUnit.id)).where(
                and_(OrgUnit.parent_id == org_unit_id, OrgUnit.deleted_at.is_(None))
            )
        )
        return result.scalar_one()

    async def batch_get(self, ids: List[int]) -> List[OrgUnit]:
        if not ids:
            return []
        result = await self.db.execute(
            select(OrgUnit).options(*self._base_options()).where(OrgUnit.id.in_(ids))
        )
        return list(result.scalars().all())
