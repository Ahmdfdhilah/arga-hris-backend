"""
Employee Repository - Database operations for Employee model

Full-featured repository with CRUD, search, hierarchy queries, and soft delete support.
Now includes User relationship for profile data.
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_, text
from sqlalchemy.orm import selectinload, joinedload
from app.core.utils.datetime import get_utc_now
from app.modules.employees.models.employee import Employee
from app.modules.users.users.models.user import User


class EmployeeFilters:
    """Filter parameters for employee queries"""
    def __init__(
        self,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ):
        self.org_unit_id = org_unit_id
        self.is_active = is_active
        self.search = search


class PaginationParams:
    """Pagination parameters"""
    def __init__(self, page: int = 1, limit: int = 10):
        self.page = max(1, page)
        self.limit = min(max(1, limit), 100)
    
    def get_offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationResult:
    """Pagination result metadata"""
    def __init__(self, page: int, limit: int, total_items: int):
        self.page = page
        self.limit = limit
        self.total_items = total_items
        self.total_pages = (total_items + limit - 1) // limit if limit > 0 else 0
    
    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "limit": self.limit,
            "total_items": self.total_items,
            "total_pages": self.total_pages
        }


class EmployeeRepository:
    """Repository for Employee model with full CRUD and advanced queries"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_options(self):
        """Standard options for loading relationships"""
        return [
            selectinload(Employee.user),
            selectinload(Employee.org_unit),
            selectinload(Employee.supervisor).selectinload(Employee.user),
        ]

    async def create(self, employee: Employee) -> Employee:
        """Create a new employee"""
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID with relationships loaded"""
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(
                and_(
                    Employee.id == employee_id,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID including soft-deleted"""
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Employee]:
        """Get employee by user ID"""
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(
                and_(
                    Employee.user_id == user_id,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, number: str) -> Optional[Employee]:
        """Get employee by employee number"""
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(
                and_(
                    Employee.number == number,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email (via user)"""
        result = await self.db.execute(
            select(Employee)
            .join(User, Employee.user_id == User.id)
            .options(*self._base_options())
            .where(
                and_(
                    User.email == email,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, employee: Employee) -> Employee:
        """Update an employee"""
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def delete(self, employee_id: int, user_id: int) -> bool:
        """Soft delete an employee"""
        employee = await self.get_by_id(employee_id)
        if not employee:
            return False
        
        employee.deleted_at = get_utc_now()
        employee.deleted_by = user_id
        employee.is_active = False
        await self.db.commit()
        return True

    async def hard_delete(self, employee_id: int) -> bool:
        """Permanently delete an employee"""
        employee = await self.get_by_id_with_deleted(employee_id)
        if not employee:
            return False
        
        await self.db.delete(employee)
        await self.db.commit()
        return True

    async def restore(self, employee_id: int) -> Optional[Employee]:
        """Restore a soft-deleted employee"""
        employee = await self.get_by_id_with_deleted(employee_id)
        if not employee or not employee.is_deleted():
            return None
        
        employee.deleted_at = None
        employee.deleted_by = None
        employee.is_active = True
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def list(
        self,
        params: PaginationParams,
        filters: EmployeeFilters,
        include_details: bool = True
    ) -> Tuple[List[Employee], PaginationResult]:
        """List employees with filters and pagination"""
        query = select(Employee).where(Employee.deleted_at.is_(None))
        count_query = select(func.count(Employee.id)).where(Employee.deleted_at.is_(None))
        
        if filters.org_unit_id is not None:
            query = query.where(Employee.org_unit_id == filters.org_unit_id)
            count_query = count_query.where(Employee.org_unit_id == filters.org_unit_id)
        
        if filters.is_active is not None:
            query = query.where(Employee.is_active == filters.is_active)
            count_query = count_query.where(Employee.is_active == filters.is_active)
        
        if filters.search:
            search_pattern = f"%{filters.search}%"
            # Join with User for name/email search
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.number.ilike(search_pattern)
                )
            )
            count_query = count_query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.number.ilike(search_pattern)
                )
            )
        
        # Count total
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Add pagination and load relationships
        if include_details:
            query = query.options(*self._base_options())
        
        query = query.offset(params.get_offset()).limit(params.limit)
        result = await self.db.execute(query)
        employees = list(result.scalars().unique().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return employees, pagination

    async def list_deleted(
        self,
        params: PaginationParams,
        search: Optional[str] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        """List soft-deleted employees"""
        query = select(Employee).where(Employee.deleted_at.is_not(None))
        count_query = select(func.count(Employee.id)).where(Employee.deleted_at.is_not(None))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.number.ilike(search_pattern)
                )
            )
            count_query = count_query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.number.ilike(search_pattern)
                )
            )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        query = query.options(*self._base_options()).offset(
            params.get_offset()
        ).limit(params.limit).order_by(Employee.deleted_at.desc())
        
        result = await self.db.execute(query)
        employees = list(result.scalars().unique().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return employees, pagination

    async def get_subordinates(
        self,
        supervisor_id: int,
        recursive: bool = False,
        params: Optional[PaginationParams] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        """Get subordinates of a supervisor"""
        if params is None:
            params = PaginationParams()
        
        if recursive:
            # Use recursive CTE for hierarchical query
            cte_query = text("""
                WITH RECURSIVE subordinates AS (
                    SELECT * FROM employees WHERE supervisor_id = :supervisor_id AND deleted_at IS NULL
                    UNION ALL
                    SELECT e.* FROM employees e
                    INNER JOIN subordinates s ON e.supervisor_id = s.id
                    WHERE e.deleted_at IS NULL
                )
                SELECT COUNT(*) FROM subordinates
            """)
            
            count_result = await self.db.execute(cte_query, {"supervisor_id": supervisor_id})
            total = count_result.scalar_one()
            
            data_query = text("""
                WITH RECURSIVE subordinates AS (
                    SELECT * FROM employees WHERE supervisor_id = :supervisor_id AND deleted_at IS NULL
                    UNION ALL
                    SELECT e.* FROM employees e
                    INNER JOIN subordinates s ON e.supervisor_id = s.id
                    WHERE e.deleted_at IS NULL
                )
                SELECT id FROM subordinates
                LIMIT :limit OFFSET :offset
            """)
            
            result = await self.db.execute(
                data_query,
                {
                    "supervisor_id": supervisor_id,
                    "limit": params.limit,
                    "offset": params.get_offset()
                }
            )
            rows = result.fetchall()
            
            employee_ids = [row[0] for row in rows]
            if employee_ids:
                employees_result = await self.db.execute(
                    select(Employee)
                    .options(*self._base_options())
                    .where(Employee.id.in_(employee_ids))
                )
                employees = list(employees_result.scalars().unique().all())
            else:
                employees = []
        else:
            count_query = select(func.count(Employee.id)).where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None)
                )
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar_one()
            
            query = select(Employee).options(*self._base_options()).where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None)
                )
            ).offset(params.get_offset()).limit(params.limit)
            
            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return employees, pagination

    async def get_by_org_unit(
        self,
        org_unit_id: int,
        include_children: bool = False,
        params: Optional[PaginationParams] = None
    ) -> Tuple[List[Employee], PaginationResult]:
        """Get employees by organization unit"""
        if params is None:
            params = PaginationParams()
        
        if include_children:
            from app.modules.org_units.models.org_unit import OrgUnit
            
            org_unit_result = await self.db.execute(
                select(OrgUnit).where(OrgUnit.id == org_unit_id)
            )
            org_unit = org_unit_result.scalar_one_or_none()
            
            if not org_unit:
                return [], PaginationResult(params.page, params.limit, 0)
            
            count_query = text("""
                SELECT COUNT(e.id) 
                FROM employees e
                JOIN org_units o ON e.org_unit_id = o.id
                WHERE o.path LIKE :path_pattern AND e.deleted_at IS NULL
            """)
            total_result = await self.db.execute(count_query, {"path_pattern": f"{org_unit.path}%"})
            total = total_result.scalar_one()
            
            query = select(Employee).options(*self._base_options()).join(
                OrgUnit, Employee.org_unit_id == OrgUnit.id
            ).where(
                and_(
                    OrgUnit.path.like(f"{org_unit.path}%"),
                    Employee.deleted_at.is_(None)
                )
            ).offset(params.get_offset()).limit(params.limit)
            
            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())
        else:
            count_query = select(func.count(Employee.id)).where(
                and_(
                    Employee.org_unit_id == org_unit_id,
                    Employee.deleted_at.is_(None)
                )
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar_one()
            
            query = select(Employee).options(*self._base_options()).where(
                and_(
                    Employee.org_unit_id == org_unit_id,
                    Employee.deleted_at.is_(None)
                )
            ).offset(params.get_offset()).limit(params.limit)
            
            result = await self.db.execute(query)
            employees = list(result.scalars().unique().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return employees, pagination

    async def get_all_by_supervisor(self, supervisor_id: int) -> List[Employee]:
        """Get all direct subordinates (no pagination, for bulk operations)"""
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return list(result.scalars().unique().all())

    async def bulk_update_supervisor(
        self,
        employee_ids: List[int],
        new_supervisor_id: Optional[int],
        updated_by: int
    ) -> int:
        """Bulk update supervisor for multiple employees"""
        result = await self.db.execute(
            update(Employee)
            .where(Employee.id.in_(employee_ids))
            .values(
                supervisor_id=new_supervisor_id,
                updated_by=updated_by
            )
        )
        await self.db.commit()
        return result.rowcount

    async def count_subordinates(self, supervisor_id: int) -> int:
        """Count direct subordinates of a supervisor"""
        result = await self.db.execute(
            select(func.count(Employee.id))
            .where(
                and_(
                    Employee.supervisor_id == supervisor_id,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one()

    async def batch_get(self, ids: List[int]) -> List[Employee]:
        """Get multiple employees by IDs"""
        if not ids:
            return []
        
        result = await self.db.execute(
            select(Employee)
            .options(*self._base_options())
            .where(Employee.id.in_(ids))
        )
        return list(result.scalars().unique().all())

    async def count(self, filters: EmployeeFilters) -> int:
        """Count employees with filters"""
        query = select(func.count(Employee.id)).where(Employee.deleted_at.is_(None))
        
        if filters.org_unit_id is not None:
            query = query.where(Employee.org_unit_id == filters.org_unit_id)
        
        if filters.is_active is not None:
            query = query.where(Employee.is_active == filters.is_active)
        
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.outerjoin(User, Employee.user_id == User.id).where(
                or_(
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.number.ilike(search_pattern)
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar_one()
