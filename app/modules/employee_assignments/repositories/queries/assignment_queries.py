"""
Assignment Query Repository - Read operations
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)


class AssignmentQueries:
    """Read operations for EmployeeAssignment"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, assignment_id: int, load_relationships: bool = True
    ) -> Optional[EmployeeAssignment]:
        """Get assignment by ID dengan optional eager loading."""
        query = select(EmployeeAssignment).where(EmployeeAssignment.id == assignment_id)

        if load_relationships:
            query = query.options(
                selectinload(EmployeeAssignment.employee),
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
                selectinload(EmployeeAssignment.leave_request),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        status: Optional[str] = None,
        employee_id: Optional[int] = None,
        replaced_employee_id: Optional[int] = None,
        org_unit_id: Optional[int] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 10,
        load_relationships: bool = True,
    ) -> Tuple[List[EmployeeAssignment], int]:
        """List assignments dengan filters dan pagination."""
        query = select(EmployeeAssignment)

        # Filters
        if status:
            query = query.where(EmployeeAssignment.status == status)
        if employee_id:
            query = query.where(EmployeeAssignment.employee_id == employee_id)
        if replaced_employee_id:
            query = query.where(
                EmployeeAssignment.replaced_employee_id == replaced_employee_id
            )
        if org_unit_id:
            query = query.where(EmployeeAssignment.org_unit_id == org_unit_id)
        if start_date_from:
            query = query.where(EmployeeAssignment.start_date >= start_date_from)
        if start_date_to:
            query = query.where(EmployeeAssignment.start_date <= start_date_to)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        # Eager loading
        if load_relationships:
            query = query.options(
                selectinload(EmployeeAssignment.employee),
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
                selectinload(EmployeeAssignment.leave_request),
            )

        # Order dan pagination
        query = (
            query.order_by(EmployeeAssignment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_pending_to_activate(
        self, as_of_date: date
    ) -> List[EmployeeAssignment]:
        """Get assignments yang perlu di-activate (status=pending, start_date <= today)."""
        query = (
            select(EmployeeAssignment)
            .where(
                and_(
                    EmployeeAssignment.status == "pending",
                    EmployeeAssignment.start_date <= as_of_date,
                )
            )
            .options(
                selectinload(EmployeeAssignment.employee),
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
                selectinload(EmployeeAssignment.leave_request),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_to_expire(self, as_of_date: date) -> List[EmployeeAssignment]:
        """Get assignments yang perlu di-expire (status=active, end_date < today)."""
        query = (
            select(EmployeeAssignment)
            .where(
                and_(
                    EmployeeAssignment.status == "active",
                    EmployeeAssignment.end_date < as_of_date,
                )
            )
            .options(
                selectinload(EmployeeAssignment.employee),
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
                selectinload(EmployeeAssignment.leave_request),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_leave_request_id(
        self, leave_request_id: int
    ) -> Optional[EmployeeAssignment]:
        """Get assignment berdasarkan leave request ID."""
        query = (
            select(EmployeeAssignment)
            .where(EmployeeAssignment.leave_request_id == leave_request_id)
            .options(
                selectinload(EmployeeAssignment.employee),
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
                selectinload(EmployeeAssignment.leave_request),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_for_employee(
        self, employee_id: int, as_of_date: date
    ) -> List[EmployeeAssignment]:
        """Get active assignments dimana employee menggantikan seseorang."""
        query = (
            select(EmployeeAssignment)
            .where(
                and_(
                    EmployeeAssignment.employee_id == employee_id,
                    EmployeeAssignment.status == "active",
                    EmployeeAssignment.start_date <= as_of_date,
                    EmployeeAssignment.end_date >= as_of_date,
                )
            )
            .options(
                selectinload(EmployeeAssignment.replaced_employee),
                selectinload(EmployeeAssignment.org_unit),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def check_overlapping(
        self,
        employee_id: int,
        replaced_employee_id: int,
        start_date: date,
        end_date: date,
        exclude_id: Optional[int] = None,
    ) -> Optional[EmployeeAssignment]:
        """Check apakah ada assignment yang overlap."""
        query = select(EmployeeAssignment).where(
            and_(
                EmployeeAssignment.employee_id == employee_id,
                EmployeeAssignment.replaced_employee_id == replaced_employee_id,
                EmployeeAssignment.status.in_(["pending", "active"]),
                # Overlap check: new.start <= existing.end AND new.end >= existing.start
                EmployeeAssignment.start_date <= end_date,
                EmployeeAssignment.end_date >= start_date,
            )
        )
        if exclude_id:
            query = query.where(EmployeeAssignment.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
