from typing import Optional, Tuple, List
from datetime import date
from app.modules.attendance.repositories import AttendanceQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendance.schemas import AttendanceListResponse
from app.config.constants import AttendanceConstants
from app.core.exceptions.client_error import BadRequestException
from app.core.utils.file_upload import generate_signed_url_for_path
from app.core.utils.datetime import get_date_range_from_type


class GetAllAttendancesUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def execute(
        self,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        org_unit_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AttendanceListResponse], dict]:
        if type:
            start_date, end_date = get_date_range_from_type(type)

        if status and status not in AttendanceConstants.VALID_STATUSES:
            raise BadRequestException(
                f"Status tidak valid. Harus salah satu dari: {', '.join(AttendanceConstants.VALID_STATUSES)}"
            )

        employee_ids = [employee_id] if employee_id else None

        skip = (page - 1) * limit

        attendances = await self.queries.list_all(
            employee_ids=employee_ids,
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=skip,
            limit=limit,
        )

        total_items = await self.queries.count_all(
            employee_ids=employee_ids,
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
        )

        attendances_data: List[AttendanceListResponse] = []
        for att in attendances:
            employee = await self.employee_queries.get_by_id(att.employee_id)
            employee_name = employee.user.name if employee and employee.user else None
            employee_number = employee.employee_number if employee else None
            org_unit_name = (
                employee.org_unit.name if employee and employee.org_unit else None
            )

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
