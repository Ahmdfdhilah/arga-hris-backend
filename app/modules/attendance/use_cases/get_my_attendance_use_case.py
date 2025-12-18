from typing import Optional, Tuple, List
from datetime import date
from app.modules.attendance.repositories import AttendanceQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendance.schemas import AttendanceListResponse
from app.core.utils.file_upload import generate_signed_url_for_path
from app.core.utils.datetime import get_date_range_from_type


class GetMyAttendanceUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def execute(
        self,
        employee_id: int,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AttendanceListResponse], dict]:
        if type:
            start_date, end_date = get_date_range_from_type(type)

        skip = (page - 1) * limit
        attendances = await self.queries.list_by_employee(
            employee_id, start_date, end_date, skip, limit
        )
        total_items = await self.queries.count_by_employee(
            employee_id, start_date, end_date
        )

        # Optimization: Get employee once
        employee = await self.employee_queries.get_by_id(employee_id)
        employee_name = employee.user.name if employee and employee.user else None
        employee_number = employee.employee_number if employee else None
        org_unit_name = (
            employee.org_unit.name if employee and employee.org_unit else None
        )

        attendances_data: List[AttendanceListResponse] = []
        for att in attendances:
            check_in_url = generate_signed_url_for_path(att.check_in_selfie_path)
            check_out_url = generate_signed_url_for_path(att.check_out_selfie_path)
            response = AttendanceListResponse.from_orm_with_urls(
                attendance=att,
                employee_name=employee_name,
                employee_number=employee_number,
                org_unit_name=org_unit_name,
                check_in_url=check_in_url,
                check_out_url=check_out_url,
            )
            attendances_data.append(response)

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total_items,
        }
        return attendances_data, pagination
