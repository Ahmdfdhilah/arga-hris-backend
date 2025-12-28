from typing import Optional, Tuple, List
from datetime import date
from app.modules.attendances.repositories import AttendanceQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendances.schemas import AttendanceListResponse
from app.core.utils.file_upload import generate_signed_url_for_path


class GetTeamAttendanceUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def _get_all_subordinates(self, employee_id: int) -> List[int]:
        """Get all subordinate IDs recursively"""
        all_subordinates_ids = []
        subordinates = await self.employee_queries.get_subordinates(
            employee_id, recursive=True
        )
        all_subordinates_ids = [e.id for e in subordinates]
        return all_subordinates_ids

    async def execute(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AttendanceListResponse], dict]:
        subordinate_ids = await self._get_all_subordinates(employee_id)

        if not subordinate_ids:
            return [], {
                "page": page,
                "limit": limit,
                "total_items": 0,
            }

        skip = (page - 1) * limit
        attendances, total_items = await self.queries.list_by_employees(
            subordinate_ids, start_date, end_date, status, skip, limit
        )

        attendances_data: List[AttendanceListResponse] = []

        for att in attendances:
            employee = await self.employee_queries.get_by_id(att.employee_id)
            employee_name = employee.user.name if employee and employee.user else None
            employee_code = employee.code if employee else None
            org_unit_name = (
                employee.org_unit.name if employee and employee.org_unit else None
            )

            check_in_url = generate_signed_url_for_path(att.check_in_selfie_path)
            check_out_url = generate_signed_url_for_path(att.check_out_selfie_path)

            response = AttendanceListResponse.from_orm_with_urls(
                attendance=att,
                employee_name=employee_name,
                employee_code=employee_code,
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
