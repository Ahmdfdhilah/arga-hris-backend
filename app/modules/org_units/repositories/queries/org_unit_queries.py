"""
OrgUnit Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.orm import selectinload

from app.modules.org_units.models.org_unit import OrgUnit


@dataclass
class OrgUnitFilters:
    parent_id: Optional[int] = None
    type_: Optional[str] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


@dataclass
class PaginationParams:
    page: int = 1
    limit: int = 10

    def __post_init__(self):
        self.page = max(1, self.page)
        self.limit = min(max(1, self.limit), 100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass
class PaginationResult:
    page: int
    limit: int
    total_items: int

    @property
    def total_pages(self) -> int:
        return (
            (self.total_items + self.limit - 1) // self.limit if self.limit > 0 else 0
        )

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "limit": self.limit,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
        }


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
        self, params: PaginationParams, filters: OrgUnitFilters
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_(None))
        count_query = select(func.count(OrgUnit.id)).where(OrgUnit.deleted_at.is_(None))

        if filters.parent_id is not None:
            query = query.where(OrgUnit.parent_id == filters.parent_id)
            count_query = count_query.where(OrgUnit.parent_id == filters.parent_id)
        if filters.type_ is not None:
            query = query.where(OrgUnit.type == filters.type_)
            count_query = count_query.where(OrgUnit.type == filters.type_)
        if filters.is_active is not None:
            query = query.where(OrgUnit.is_active == filters.is_active)
            count_query = count_query.where(OrgUnit.is_active == filters.is_active)
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )
            count_query = count_query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )

        total = (await self.db.execute(count_query)).scalar_one()
        query = (
            query.options(*self._base_options())
            .offset(params.offset)
            .limit(params.limit)
        )
        result = await self.db.execute(query)

        return list(result.scalars().all()), PaginationResult(
            params.page, params.limit, total
        )

    async def list_deleted(
        self, params: PaginationParams, search: Optional[str] = None
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_not(None))
        count_query = select(func.count(OrgUnit.id)).where(
            OrgUnit.deleted_at.is_not(None)
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )
            count_query = count_query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )

        total = (await self.db.execute(count_query)).scalar_one()
        query = (
            query.options(*self._base_options())
            .offset(params.offset)
            .limit(params.limit)
            .order_by(OrgUnit.deleted_at.desc())
        )
        result = await self.db.execute(query)

        return list(result.scalars().all()), PaginationResult(
            params.page, params.limit, total
        )

    async def get_children(
        self,
        parent_id: int,
        recursive: bool = False,
        params: Optional[PaginationParams] = None,
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        if params is None:
            params = PaginationParams()

        if recursive:
            parent = await self.get_by_id(parent_id)
            if not parent:
                return [], PaginationResult(params.page, params.limit, 0)

            count_query = select(func.count(OrgUnit.id)).where(
                and_(
                    OrgUnit.path.like(f"{parent.path}.%"), OrgUnit.deleted_at.is_(None)
                )
            )
            total = (await self.db.execute(count_query)).scalar_one()

            query = (
                select(OrgUnit)
                .options(*self._base_options())
                .where(
                    and_(
                        OrgUnit.path.like(f"{parent.path}.%"),
                        OrgUnit.deleted_at.is_(None),
                    )
                )
                .offset(params.offset)
                .limit(params.limit)
            )
            result = await self.db.execute(query)
            org_units = list(result.scalars().all())
        else:
            count_query = select(func.count(OrgUnit.id)).where(
                and_(OrgUnit.parent_id == parent_id, OrgUnit.deleted_at.is_(None))
            )
            total = (await self.db.execute(count_query)).scalar_one()

            query = (
                select(OrgUnit)
                .options(*self._base_options())
                .where(
                    and_(OrgUnit.parent_id == parent_id, OrgUnit.deleted_at.is_(None))
                )
                .offset(params.offset)
                .limit(params.limit)
            )
            result = await self.db.execute(query)
            org_units = list(result.scalars().all())

        return org_units, PaginationResult(params.page, params.limit, total)

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
                    Employee.is_active == True,
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

    async def count(self, filters: OrgUnitFilters) -> int:
        query = select(func.count(OrgUnit.id)).where(OrgUnit.deleted_at.is_(None))
        if filters.parent_id is not None:
            query = query.where(OrgUnit.parent_id == filters.parent_id)
        if filters.type_ is not None:
            query = query.where(OrgUnit.type == filters.type_)
        if filters.is_active is not None:
            query = query.where(OrgUnit.is_active == filters.is_active)
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.where(
                or_(OrgUnit.name.ilike(pattern), OrgUnit.code.ilike(pattern))
            )
        return (await self.db.execute(query)).scalar_one()
