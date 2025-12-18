"""
Employee Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.orm import selectinload

from app.modules.employees.models.employee import Employee
from app.modules.users.users.models.user import User


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

    async def get_by_user_id(self, user_id: str) -> Optional[Employee]:
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

    async def list_deleted(
        self,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Employee], int]:
        query = select(Employee).where(Employee.deleted_at.is_not(None))

        if search:
            pattern = f"%{search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(pattern),
                    User.email.ilike(pattern),
                    Employee.number.ilike(pattern),
                )
            )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = (
            query.options(*self._base_options())
            .offset(skip)
            .limit(limit)
            .order_by(Employee.deleted_at.desc())
        )
        result = await self.db.execute(query)
        items = list(result.scalars().unique().all())

        return items, total

    async def get_subordinates(
        self,
        supervisor_id: int,
        recursive: bool = False,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Employee], int]:
        if recursive:
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
            count_cte = text("""
                WITH RECURSIVE subordinates AS (
                    SELECT * FROM employees WHERE supervisor_id = :supervisor_id AND deleted_at IS NULL
                    UNION ALL
                    SELECT e.* FROM employees e
                    INNER JOIN subordinates s ON e.supervisor_id = s.id
                    WHERE e.deleted_at IS NULL
                )
                SELECT COUNT(*) FROM subordinates
            """)

            rows = (
                await self.db.execute(
                    data_cte,
                    {
                        "supervisor_id": supervisor_id,
                        "limit": limit,
                        "offset": skip,
                    },
                )
            ).fetchall()

            ids = [r[0] for r in rows]
            items = []
            if ids:
                emp_result = await self.db.execute(
                    select(Employee)
                    .options(*self._base_options())
                    .where(Employee.id.in_(ids))
                )
                items = list(emp_result.scalars().unique().all())

            total = (
                await self.db.execute(count_cte, {"supervisor_id": supervisor_id})
            ).scalar_one()

            return items, total
        else:
            query = select(Employee).where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None),
                )
            )

            # Count query
            count_query = select(func.count()).select_from(query.subquery())
            total = (await self.db.execute(count_query)).scalar_one()

            # Data query
            query = query.options(*self._base_options()).offset(skip).limit(limit)
            result = await self.db.execute(query)
            items = list(result.scalars().unique().all())

            return items, total

    async def list(
        self,
        org_unit_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 10,
        skip: int = 0,
    ) -> Tuple[List[Employee], int]:
        query = select(Employee)

        if org_unit_id:
            query = query.where(Employee.org_unit_id == org_unit_id)

        if is_active is not None:
            query = query.where(Employee.is_active == is_active)

        if search:
            # Join with User to search by name/email
            query = query.join(Employee.user).where(
                or_(
                    Employee.number.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                )
            )

        query = query.where(Employee.deleted_at.is_(None))

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Data query
        query = query.options(*self._base_options()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_all_by_org_unit(
        self,
        org_unit_id: int,
        include_children: bool = False,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Employee], int]:
        if include_children:
            from app.modules.org_units.models.org_unit import OrgUnit

            org = (
                await self.db.execute(select(OrgUnit).where(OrgUnit.id == org_unit_id))
            ).scalar_one_or_none()
            if not org:
                return [], 0

            # Base query logic
            query = (
                select(Employee)
                .join(OrgUnit, Employee.org_unit_id == OrgUnit.id)
                .where(
                    and_(
                        OrgUnit.path.like(f"{org.path}%"), Employee.deleted_at.is_(None)
                    )
                )
            )

            # Count logic
            count_query = select(func.count()).select_from(query.subquery())
            total = (await self.db.execute(count_query)).scalar_one()

            # Data fetch
            query = query.options(*self._base_options()).offset(skip).limit(limit)
            result = await self.db.execute(query)
            items = list(result.scalars().unique().all())

            return items, total
        else:
            query = select(Employee).where(
                and_(
                    Employee.org_unit_id == org_unit_id,
                    Employee.deleted_at.is_(None),
                )
            )

            # Count logic
            count_query = select(func.count()).select_from(query.subquery())
            total = (await self.db.execute(count_query)).scalar_one()

            # Data fetch
            query = query.options(*self._base_options()).offset(skip).limit(limit)
            result = await self.db.execute(query)
            items = list(result.scalars().unique().all())

            return items, total

    async def get_all_by_supervisor(self, supervisor_id: int) -> List[Employee]:
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None),
                )
            )
        )
        return list(result.scalars().unique().all())

    async def batch_get(self, ids: List[int]) -> List[Employee]:
        if not ids:
            return []
        result = await self.db.execute(
            select(Employee).options(*self._base_options()).where(Employee.id.in_(ids))
        )
        return list(result.scalars().unique().all())
