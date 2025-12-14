"""
Employee Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.orm import selectinload

from app.modules.employees.models.employee import Employee
from app.modules.users.users.models.user import User


@dataclass
class EmployeeFilters:
    """Filter parameters for employee queries"""
    org_unit_id: Optional[int] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


@dataclass
class PaginationParams:
    """Pagination parameters"""
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
    """Pagination result metadata"""
    page: int
    limit: int
    total_items: int

    @property
    def total_pages(self) -> int:
        return (self.total_items + self.limit - 1) // self.limit if self.limit > 0 else 0

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "limit": self.limit,
            "total_items": self.total_items,
            "total_pages": self.total_pages
        }


class EmployeeQueries:
    """Read-only operations for Employee model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_options(self):
        return [
            selectinload(Employee.user),
            selectinload(Employee.org_unit),
            selectinload(Employee.supervisor).selectinload(Employee.user),
        ]

    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(and_(Employee.id == employee_id, Employee.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, employee_id: int) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(and_(Employee.user_id == user_id, Employee.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, number: str) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(and_(Employee.number == number, Employee.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Employee]:
        result = await self.db.execute(
            select(Employee)
            .join(User, Employee.user_id == User.id)
            .options(*self._base_options())
            .where(and_(User.email == email, Employee.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        params: PaginationParams,
        filters: EmployeeFilters,
    ) -> Tuple[List[Employee], PaginationResult]:
        query = select(Employee).where(Employee.deleted_at.is_(None))
        count_query = select(func.count(Employee.id)).where(Employee.deleted_at.is_(None))

        if filters.org_unit_id is not None:
            query = query.where(Employee.org_unit_id == filters.org_unit_id)
            count_query = count_query.where(Employee.org_unit_id == filters.org_unit_id)

        if filters.is_active is not None:
            query = query.where(Employee.is_active == filters.is_active)
            count_query = count_query.where(Employee.is_active == filters.is_active)

        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern), Employee.number.ilike(pattern))
            )
            count_query = count_query.outerjoin(User, Employee.user_id == User.id).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern), Employee.number.ilike(pattern))
            )

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.options(*self._base_options()).offset(params.offset).limit(params.limit)
        result = await self.db.execute(query)
        employees = list(result.scalars().unique().all())

        return employees, PaginationResult(params.page, params.limit, total)

    async def list_deleted(
        self,
        params: PaginationParams,
        search: Optional[str] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        query = select(Employee).where(Employee.deleted_at.is_not(None))
        count_query = select(func.count(Employee.id)).where(Employee.deleted_at.is_not(None))

        if search:
            pattern = f"%{search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern), Employee.number.ilike(pattern))
            )
            count_query = count_query.outerjoin(User, Employee.user_id == User.id).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern), Employee.number.ilike(pattern))
            )

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.options(*self._base_options()).offset(params.offset).limit(params.limit).order_by(Employee.deleted_at.desc())
        result = await self.db.execute(query)
        employees = list(result.scalars().unique().all())

        return employees, PaginationResult(params.page, params.limit, total)

    async def get_subordinates(
        self,
        supervisor_id: int,
        recursive: bool = False,
        params: Optional[PaginationParams] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        if params is None:
            params = PaginationParams()

        if recursive:
            cte = text("""
                WITH RECURSIVE subordinates AS (
                    SELECT * FROM employees WHERE supervisor_id = :supervisor_id AND deleted_at IS NULL
                    UNION ALL
                    SELECT e.* FROM employees e
                    INNER JOIN subordinates s ON e.supervisor_id = s.id
                    WHERE e.deleted_at IS NULL
                )
                SELECT COUNT(*) FROM subordinates
            """)
            total = (await self.db.execute(cte, {"supervisor_id": supervisor_id})).scalar_one()

            data_cte = text("""
                WITH RECURSIVE subordinates AS (
                    SELECT * FROM employees WHERE supervisor_id = :supervisor_id AND deleted_at IS NULL
                    UNION ALL
                    SELECT e.* FROM employees e
                    INNER JOIN subordinates s ON e.supervisor_id = s.id
                    WHERE e.deleted_at IS NULL
                )
                SELECT id FROM subordinates LIMIT :limit OFFSET :offset
            """)
            rows = (await self.db.execute(data_cte, {
                "supervisor_id": supervisor_id, "limit": params.limit, "offset": params.offset
            })).fetchall()

            ids = [r[0] for r in rows]
            if ids:
                emp_result = await self.db.execute(
                    select(Employee).options(*self._base_options()).where(Employee.id.in_(ids))
                )
                employees = list(emp_result.scalars().unique().all())
            else:
                employees = []
        else:
            count_query = select(func.count(Employee.id)).where(
                and_(Employee.supervisor_id == supervisor_id, Employee.deleted_at.is_(None))
            )
            total = (await self.db.execute(count_query)).scalar_one()

            query = select(Employee).options(*self._base_options()).where(
                and_(Employee.supervisor_id == supervisor_id, Employee.deleted_at.is_(None))
            ).offset(params.offset).limit(params.limit)
            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())

        return employees, PaginationResult(params.page, params.limit, total)

    async def get_by_org_unit(
        self,
        org_unit_id: int,
        include_children: bool = False,
        params: Optional[PaginationParams] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        if params is None:
            params = PaginationParams()

        if include_children:
            from app.modules.org_units.models.org_unit import OrgUnit

            org = (await self.db.execute(select(OrgUnit).where(OrgUnit.id == org_unit_id))).scalar_one_or_none()
            if not org:
                return [], PaginationResult(params.page, params.limit, 0)

            cnt = text("""
                SELECT COUNT(e.id) FROM employees e
                JOIN org_units o ON e.org_unit_id = o.id
                WHERE o.path LIKE :pattern AND e.deleted_at IS NULL
            """)
            total = (await self.db.execute(cnt, {"pattern": f"{org.path}%"})).scalar_one()

            query = select(Employee).options(*self._base_options()).join(
                OrgUnit, Employee.org_unit_id == OrgUnit.id
            ).where(and_(OrgUnit.path.like(f"{org.path}%"), Employee.deleted_at.is_(None))).offset(params.offset).limit(params.limit)

            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())
        else:
            count_query = select(func.count(Employee.id)).where(
                and_(Employee.org_unit_id == org_unit_id, Employee.deleted_at.is_(None))
            )
            total = (await self.db.execute(count_query)).scalar_one()

            query = select(Employee).options(*self._base_options()).where(
                and_(Employee.org_unit_id == org_unit_id, Employee.deleted_at.is_(None))
            ).offset(params.offset).limit(params.limit)

            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())

        return employees, PaginationResult(params.page, params.limit, total)

    async def get_all_by_supervisor(self, supervisor_id: int) -> List[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(and_(Employee.supervisor_id == supervisor_id, Employee.deleted_at.is_(None)))
        )
        return list(result.scalars().unique().all())

    async def batch_get(self, ids: List[int]) -> List[Employee]:
        if not ids:
            return []
        result = await self.db.execute(
            select(Employee).options(*self._base_options()).where(Employee.id.in_(ids))
        )
        return list(result.scalars().unique().all())

    async def count(self, filters: EmployeeFilters) -> int:
        query = select(func.count(Employee.id)).where(Employee.deleted_at.is_(None))

        if filters.org_unit_id is not None:
            query = query.where(Employee.org_unit_id == filters.org_unit_id)
        if filters.is_active is not None:
            query = query.where(Employee.is_active == filters.is_active)
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern), Employee.number.ilike(pattern))
            )

        return (await self.db.execute(query)).scalar_one()

    async def count_subordinates(self, supervisor_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Employee.id)).where(
                and_(Employee.supervisor_id == supervisor_id, Employee.deleted_at.is_(None))
            )
        )
        return result.scalar_one()
