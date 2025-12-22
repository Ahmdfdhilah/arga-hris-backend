from typing import Optional, Tuple, List, Dict, Any
from datetime import date
from app.modules.attendances.repositories import AttendanceQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendances.schemas import EmployeeAttendanceOverview
from app.core.exceptions.client_error import BadRequestException


class GetAttendanceOverviewUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

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

        skip = (page - 1) * limit
        employees, total = await self.employee_queries.list(
            org_unit_id=org_unit_id,
            is_active=True,
            limit=limit,
            skip=skip,
        )

        if not employees:
            pagination_dict = {
                "page": page,
                "limit": limit,
                "total_items": 0,
                "total_pages": 0,
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
                employee_code=employee.code,
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

        total_pages = (total + limit - 1) // limit if total > 0 else 0
        pagination_dict = {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": total_pages,
        }
        return overview_data, pagination_dict
