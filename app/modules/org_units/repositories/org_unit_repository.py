"""
OrgUnit Repository - Database operations for OrgUnit model

Full-featured repository with CRUD, hierarchy queries, and soft delete support.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_, text
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.core.utils.datetime import get_utc_now
from app.modules.org_units.models.org_unit import OrgUnit


class OrgUnitFilters:
    """Filter parameters for org unit queries"""
    def __init__(
        self,
        parent_id: Optional[int] = None,
        type_: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ):
        self.parent_id = parent_id
        self.type_ = type_
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
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "page": self.page,
            "limit": self.limit,
            "total_items": self.total_items,
            "total_pages": self.total_pages
        }


class OrgUnitRepository:
    """Repository for OrgUnit model with full CRUD and hierarchy queries"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_unit: OrgUnit) -> OrgUnit:
        """Create a new org unit"""
        self.db.add(org_unit)
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit

    async def get_by_id(self, org_unit_id: int) -> Optional[OrgUnit]:
        """Get org unit by ID with relationships loaded"""
        result = await self.db.execute(
            select(OrgUnit)
            .options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            )
            .where(
                and_(
                    OrgUnit.id == org_unit_id,
                    OrgUnit.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_deleted(self, org_unit_id: int) -> Optional[OrgUnit]:
        """Get org unit by ID including soft-deleted"""
        result = await self.db.execute(
            select(OrgUnit)
            .options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            )
            .where(OrgUnit.id == org_unit_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[OrgUnit]:
        """Get org unit by code"""
        result = await self.db.execute(
            select(OrgUnit)
            .options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            )
            .where(
                and_(
                    OrgUnit.code == code,
                    OrgUnit.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, org_unit: OrgUnit) -> OrgUnit:
        """Update an org unit"""
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit

    async def delete(self, org_unit_id: int, user_id: int) -> bool:
        """Soft delete an org unit"""
        org_unit = await self.get_by_id(org_unit_id)
        if not org_unit:
            return False
        
        org_unit.deleted_at = get_utc_now()
        org_unit.deleted_by = user_id
        org_unit.is_active = False
        await self.db.commit()
        return True

    async def hard_delete(self, org_unit_id: int) -> bool:
        """Permanently delete an org unit"""
        org_unit = await self.get_by_id_with_deleted(org_unit_id)
        if not org_unit:
            return False
        
        await self.db.delete(org_unit)
        await self.db.commit()
        return True

    async def restore(self, org_unit_id: int) -> Optional[OrgUnit]:
        """Restore a soft-deleted org unit"""
        org_unit = await self.get_by_id_with_deleted(org_unit_id)
        if not org_unit or not org_unit.is_deleted():
            return None
        
        # Check if parent is deleted
        if org_unit.parent_id:
            parent = await self.get_by_id_with_deleted(org_unit.parent_id)
            if parent and parent.is_deleted():
                return None  # Cannot restore if parent is deleted
        
        org_unit.deleted_at = None
        org_unit.deleted_by = None
        org_unit.is_active = True
        await self.db.commit()
        await self.db.refresh(org_unit)
        return org_unit

    async def list(
        self,
        params: PaginationParams,
        filters: OrgUnitFilters
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        """List org units with filters and pagination"""
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_(None))
        
        if filters.parent_id is not None:
            query = query.where(OrgUnit.parent_id == filters.parent_id)
        
        if filters.type_ is not None:
            query = query.where(OrgUnit.type == filters.type_)
        
        if filters.is_active is not None:
            query = query.where(OrgUnit.is_active == filters.is_active)
        
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    OrgUnit.name.ilike(search_pattern),
                    OrgUnit.code.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(OrgUnit.id)).where(OrgUnit.deleted_at.is_(None))
        if filters.parent_id is not None:
            count_query = count_query.where(OrgUnit.parent_id == filters.parent_id)
        if filters.type_ is not None:
            count_query = count_query.where(OrgUnit.type == filters.type_)
        if filters.is_active is not None:
            count_query = count_query.where(OrgUnit.is_active == filters.is_active)
        if filters.search:
            search_pattern = f"%{filters.search}%"
            count_query = count_query.where(
                or_(
                    OrgUnit.name.ilike(search_pattern),
                    OrgUnit.code.ilike(search_pattern)
                )
            )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Add pagination and load relationships
        query = query.options(
            selectinload(OrgUnit.parent),
            selectinload(OrgUnit.head)
        ).offset(params.get_offset()).limit(params.limit)
        
        result = await self.db.execute(query)
        org_units = list(result.scalars().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return org_units, pagination

    async def list_deleted(
        self,
        params: PaginationParams,
        search: Optional[str] = None
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        """List soft-deleted org units"""
        query = select(OrgUnit).where(OrgUnit.deleted_at.is_not(None))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    OrgUnit.name.ilike(search_pattern),
                    OrgUnit.code.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(OrgUnit.id)).where(OrgUnit.deleted_at.is_not(None))
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                or_(
                    OrgUnit.name.ilike(search_pattern),
                    OrgUnit.code.ilike(search_pattern)
                )
            )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        query = query.options(
            selectinload(OrgUnit.parent),
            selectinload(OrgUnit.head)
        ).offset(params.get_offset()).limit(params.limit).order_by(OrgUnit.deleted_at.desc())
        
        result = await self.db.execute(query)
        org_units = list(result.scalars().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return org_units, pagination

    async def get_children(
        self,
        parent_id: int,
        recursive: bool = False,
        params: Optional[PaginationParams] = None
    ) -> Tuple[List[OrgUnit], PaginationResult]:
        """Get children of an org unit"""
        if params is None:
            params = PaginationParams()
        
        if recursive:
            # Get parent to use its path
            parent = await self.get_by_id(parent_id)
            if not parent:
                return [], PaginationResult(params.page, params.limit, 0)
            
            # Query all descendants using path
            count_query = select(func.count(OrgUnit.id)).where(
                and_(
                    OrgUnit.path.like(f"{parent.path}.%"),
                    OrgUnit.deleted_at.is_(None)
                )
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar_one()
            
            query = select(OrgUnit).options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            ).where(
                and_(
                    OrgUnit.path.like(f"{parent.path}.%"),
                    OrgUnit.deleted_at.is_(None)
                )
            ).offset(params.get_offset()).limit(params.limit)
            
            result = await self.db.execute(query)
            org_units = list(result.scalars().all())
        else:
            # Simple direct children query
            count_query = select(func.count(OrgUnit.id)).where(
                and_(
                    OrgUnit.parent_id == parent_id,
                    OrgUnit.deleted_at.is_(None)
                )
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar_one()
            
            query = select(OrgUnit).options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            ).where(
                and_(
                    OrgUnit.parent_id == parent_id,
                    OrgUnit.deleted_at.is_(None)
                )
            ).offset(params.get_offset()).limit(params.limit)
            
            result = await self.db.execute(query)
            org_units = list(result.scalars().all())
        
        pagination = PaginationResult(params.page, params.limit, total)
        return org_units, pagination

    async def get_ancestors(self, org_unit_id: int) -> List[OrgUnit]:
        """Get all ancestors of an org unit using recursive CTE"""
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
            .options(selectinload(OrgUnit.parent), selectinload(OrgUnit.head))
            .where(OrgUnit.id.in_(ancestor_ids))
            .order_by(OrgUnit.level)
        )
        return list(org_units_result.scalars().all())

    async def get_tree(
        self,
        root_id: Optional[int] = None,
        max_depth: int = 10
    ) -> List[OrgUnit]:
        """Get org unit tree from root"""
        query = select(OrgUnit).options(
            selectinload(OrgUnit.parent),
            selectinload(OrgUnit.head)
        ).where(OrgUnit.deleted_at.is_(None))
        
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
        """Get all org units where employee is head"""
        result = await self.db.execute(
            select(OrgUnit)
            .where(
                and_(
                    OrgUnit.head_id == employee_id,
                    OrgUnit.deleted_at.is_(None)
                )
            )
        )
        return list(result.scalars().all())

    async def is_head_of_any_unit(self, employee_id: int) -> bool:
        """Check if employee is head of any org unit"""
        result = await self.db.execute(
            select(func.count(OrgUnit.id))
            .where(
                and_(
                    OrgUnit.head_id == employee_id,
                    OrgUnit.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one() > 0

    async def get_unique_types(self) -> List[str]:
        """Get all unique org unit types"""
        result = await self.db.execute(
            select(OrgUnit.type)
            .where(
                and_(
                    OrgUnit.type.is_not(None),
                    OrgUnit.type != '',
                    OrgUnit.deleted_at.is_(None)
                )
            )
            .distinct()
        )
        return [row[0] for row in result.fetchall()]

    async def count_active_employees(self, org_unit_id: int) -> int:
        """Count active employees in an org unit"""
        from app.modules.employees.models.employee import Employee
        
        result = await self.db.execute(
            select(func.count(Employee.id))
            .where(
                and_(
                    Employee.org_unit_id == org_unit_id,
                    Employee.is_active == True,
                    Employee.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one()

    async def count_active_children(self, org_unit_id: int) -> int:
        """Count active child org units"""
        result = await self.db.execute(
            select(func.count(OrgUnit.id))
            .where(
                and_(
                    OrgUnit.parent_id == org_unit_id,
                    OrgUnit.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one()

    async def batch_get(self, ids: List[int]) -> List[OrgUnit]:
        """Get multiple org units by IDs"""
        if not ids:
            return []
        
        result = await self.db.execute(
            select(OrgUnit)
            .options(
                selectinload(OrgUnit.parent),
                selectinload(OrgUnit.head)
            )
            .where(OrgUnit.id.in_(ids))
        )
        return list(result.scalars().all())

    async def count(self, filters: OrgUnitFilters) -> int:
        """Count org units with filters"""
        query = select(func.count(OrgUnit.id)).where(OrgUnit.deleted_at.is_(None))
        
        if filters.parent_id is not None:
            query = query.where(OrgUnit.parent_id == filters.parent_id)
        
        if filters.type_ is not None:
            query = query.where(OrgUnit.type == filters.type_)
        
        if filters.is_active is not None:
            query = query.where(OrgUnit.is_active == filters.is_active)
        
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    OrgUnit.name.ilike(search_pattern),
                    OrgUnit.code.ilike(search_pattern)
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar_one()
