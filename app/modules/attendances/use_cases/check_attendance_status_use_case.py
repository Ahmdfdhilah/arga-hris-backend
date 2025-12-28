from datetime import date
from app.modules.attendances.repositories import AttendanceQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.attendances.schemas import (
    AttendanceStatusCheckResponse,
    LeaveDetailsResponse,
)
from app.modules.attendances.utils.validators import (
    is_working_day,
    get_working_day_violation_reason,
)


class CheckAttendanceStatusUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
        leave_queries: LeaveRequestQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries
        self.leave_queries = leave_queries

    async def execute(self, employee_id: int) -> AttendanceStatusCheckResponse:
        today = date.today()

        employee = await self.employee_queries.get_by_id(employee_id)
        employee_type = employee.type if employee else None

        working_day = is_working_day(today, employee_type)

        leave_request = await self.leave_queries.is_on_leave(employee_id, today)
        is_on_leave = leave_request is not None

        can_attend = working_day and not is_on_leave

        reason = None
        if not working_day:
            reason = get_working_day_violation_reason(today, employee_type)
        elif is_on_leave:
            reason = f"Anda sedang cuti ({leave_request.leave_type}) dari {leave_request.start_date.strftime('%d-%m-%Y')} sampai {leave_request.end_date.strftime('%d-%m-%Y')}."

        leave_details = None
        if is_on_leave:
            leave_details = LeaveDetailsResponse(
                leave_type=leave_request.leave_type,
                start_date=leave_request.start_date.strftime("%Y-%m-%d"),
                end_date=leave_request.end_date.strftime("%Y-%m-%d"),
                total_days=leave_request.total_days,
                reason=leave_request.reason,
            )

        return AttendanceStatusCheckResponse(
            can_attend=can_attend,
            reason=reason,
            is_on_leave=is_on_leave,
            is_working_day=working_day,
            employee_type=employee_type,
            leave_details=leave_details,
        )
