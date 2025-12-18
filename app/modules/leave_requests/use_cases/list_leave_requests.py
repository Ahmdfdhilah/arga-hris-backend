from typing import Optional, List, Tuple
from datetime import date
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    LeaveRequestListResponse,
)
from app.modules.leave_requests.schemas.shared import LeaveType
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import BadRequestException


class ListMyLeaveRequestsUseCase:
    def __init__(self, queries: LeaveRequestQueries):
        self.queries = queries

    async def execute(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestResponse], int]:
        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests, total_items = await self.queries.list_by_employee(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        items = [LeaveRequestResponse.model_validate(lr) for lr in leave_requests]
        return items, total_items


class ListAllLeaveRequestsUseCase:
    def __init__(self, queries: LeaveRequestQueries, employee_queries: EmployeeQueries):
        self.queries = queries
        self.employee_queries = employee_queries

    async def execute(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestListResponse], int]:
        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests, total_items = await self.queries.list_all(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        items = []
        for lr in leave_requests:
            emp = await self.employee_queries.get_by_id(lr.employee_id)
            employee_name = emp.user.name if emp and emp.user else None
            employee_number = emp.employee_number if emp else None

            items.append(
                LeaveRequestListResponse(
                    id=lr.id,
                    employee_id=lr.employee_id,
                    employee_name=employee_name,
                    employee_number=employee_number,
                    leave_type=LeaveType(lr.leave_type),
                    start_date=lr.start_date,
                    end_date=lr.end_date,
                    total_days=lr.total_days,
                    reason=lr.reason,
                    created_at=lr.created_at,
                    updated_at=lr.updated_at,
                )
            )

        return items, total_items


class ListTeamLeaveRequestsUseCase:
    def __init__(self, queries: LeaveRequestQueries, employee_queries: EmployeeQueries):
        self.queries = queries
        self.employee_queries = employee_queries

    async def execute(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestListResponse], int]:
        # Get all subordinates recursively
        # Fixed: get_subordinates returns (items, total)
        subordinates, _ = await self.employee_queries.get_subordinates(
            employee_id, recursive=True
        )

        subordinate_ids = [e.id for e in subordinates]

        if not subordinate_ids:
            return [], 0

        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests, total_items = await self.queries.list_by_employees(
            employee_ids=subordinate_ids,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        items = []
        for lr in leave_requests:
            # We can map from subordinates list directly to save DB calls if we optimize
            # But simplistic approach first:
            emp = next((e for e in subordinates if e.id == lr.employee_id), None)
            employee_name = emp.user.name if emp and emp.user else None
            employee_number = emp.employee_number if emp else None

            items.append(
                LeaveRequestListResponse(
                    id=lr.id,
                    employee_id=lr.employee_id,
                    employee_name=employee_name,
                    employee_number=employee_number,
                    leave_type=LeaveType(lr.leave_type),
                    start_date=lr.start_date,
                    end_date=lr.end_date,
                    total_days=lr.total_days,
                    reason=lr.reason,
                    created_at=lr.created_at,
                    updated_at=lr.updated_at,
                )
            )

        return items, total_items
