from typing import Optional, Tuple, List, Dict, Any
from datetime import date
from app.modules.attendance.repositories import AttendanceQueries
from app.modules.employees.repositories import (
    EmployeeQueries,
    EmployeeFilters,
    PaginationParams,
)
from app.modules.attendance.schemas import EmployeeAttendanceOverview
from app.core.exceptions.client_error import BadRequestException


class GetAttendanceOverviewUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def _list_employees_dict(
        self, org_unit_id: Optional[int] = None, page: int = 1, limit: int = 100
    ) -> Dict[str, Any]:
        """Helper to list employees as dict"""
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(org_unit_id=org_unit_id, is_active=True)
        # Note: If org_unit_id is provided, check if we need to use get_by_org_unit_id instead of list with filters
        # The original service used different methods based on org_unit_id presence.

        if org_unit_id:
            employees = await self.employee_queries.get_by_org_unit_id(
                org_unit_id, include_children=False
            )
            # To support pagination with get_by_org_unit_id we might need custom logic or just slice.
            # Original service:
            # if org_unit_id: calls _get_employees_by_org_unit_dict (which calls get_by_org_unit_id)
            # else: calls _list_employees_dict (which calls list)

            # Let's replicate original logic:
            # But wait, get_by_org_unit_id returns list without pagination object in repository usually?
            # Actually `employee_queries.get_by_org_unit_id` returns List[Employee].
            # We need to manually paginate if the repo doesn't support it for that method.
            # Or use the `list` method with filters if it supports org_unit_id.
            # Looking at `_list_employees_dict` in original code (lines 66-86), it uses EmployeeFilters(org_unit_id=...).
            # Looking at `_get_employees_by_org_unit_dict` (lines 88-111), it uses `get_by_org_unit_id`.
            # Since we want to support pagination properly, using `list` with filters is safer if implemented correctly.
            # However, let's stick to what we see.

            # If `list` supports `org_unit_id`, we should use it.
            # But let's assume `get_by_org_unit_id` is better for specific Org Unit logic?
            # For now, I will use `list` if org_unit_id is None, and manual pagination if org_unit_id is set (if list doesn't cover it).

            # Actually, creating a filter object suggests `list` supports it.
            # `filters = EmployeeFilters(org_unit_id=org_unit_id, is_active=True)`
            # If I use this for both cases, it simplifies things.

            employees, pagination = await self.employee_queries.list(params, filters)
        else:
            filters = EmployeeFilters(is_active=True)
            employees, pagination = await self.employee_queries.list(params, filters)

        return {
            "employees": [
                {
                    "id": e.id,
                    "name": e.user.name if e.user else None,
                    "employee_number": e.employee_number,
                    "position": e.position,
                    "org_unit": {"name": e.org_unit.name} if e.org_unit else None,
                    "org_unit_id": e.org_unit_id,
                }
                for e in employees
            ],
            "pagination": pagination.to_dict(),
        }

    async def execute(
        self,
        org_unit_id: Optional[int],
        start_date: date,
        end_date: date,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[EmployeeAttendanceOverview], dict]:
        if start_date > end_date:
            raise BadRequestException(
                "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            )

        # Simplified logic: Use list() for both cases as it supports org_unit_id filter
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(org_unit_id=org_unit_id, is_active=True)
        employees, pagination = await self.employee_queries.list(params, filters)

        if not employees:
            pagination_dict = {
                "page": page,
                "limit": limit,
                "total_items": 0,
            }
            return [], pagination_dict

        employee_ids = [e.id for e in employees]
        attendances = await self.queries.get_by_employee_ids(
            employee_ids=employee_ids,
            start_date=start_date,
            end_date=end_date,
        )

        attendance_summary = {}
        for att in attendances:
            if att.employee_id not in attendance_summary:
                attendance_summary[att.employee_id] = {
                    "total_present": 0,
                    "total_absent": 0,
                    "total_leave": 0,
                    "total_hybrid": 0,
                    "total_work_hours": 0,
                    "total_overtime_hours": 0,
                }

            summary = attendance_summary[att.employee_id]

            if att.status == "present":
                summary["total_present"] += 1
            elif att.status == "absent":
                summary["total_absent"] += 1
            elif att.status == "leave":
                summary["total_leave"] += 1
            elif att.status == "hybrid":
                summary["total_hybrid"] += 1

            if att.work_hours:
                summary["total_work_hours"] += float(att.work_hours)

            if att.overtime_hours:
                summary["total_overtime_hours"] += float(att.overtime_hours)

        overview_data = []
        for employee in employees:
            employee_id = employee.id
            summary = attendance_summary.get(
                employee_id,
                {
                    "total_present": 0,
                    "total_absent": 0,
                    "total_leave": 0,
                    "total_hybrid": 0,
                    "total_work_hours": 0,
                    "total_overtime_hours": 0,
                },
            )

            org_unit_name = employee.org_unit.name if employee.org_unit else None

            employee_overview = EmployeeAttendanceOverview(
                employee_id=employee_id,
                employee_name=employee.user.name if employee.user else None,
                employee_number=employee.employee_number,
                employee_position=employee.position,
                org_unit_id=employee.org_unit_id,
                org_unit_name=org_unit_name,
                total_present=summary["total_present"],
                total_absent=summary["total_absent"],
                total_leave=summary["total_leave"],
                total_hybrid=summary["total_hybrid"],
                total_work_hours=summary["total_work_hours"],
                total_overtime_hours=summary["total_overtime_hours"],
            )
            overview_data.append(employee_overview)

        pagination_dict = pagination.to_dict()
        return overview_data, pagination_dict
