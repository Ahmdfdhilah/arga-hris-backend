from app.modules.leave_requests.schemas.requests import LeaveRequestCreateRequest
from app.modules.leave_requests.schemas.responses import LeaveRequestResponse
from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import NotFoundException
from app.modules.leave_requests.utils.total_days import (
    calculate_working_days,
    validate_no_overlapping_leave,
    validate_leave_dates,
)


class CreateLeaveRequestUseCase:
    def __init__(
        self,
        queries: LeaveRequestQueries,
        commands: LeaveRequestCommands,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries

    async def execute(
        self, request: LeaveRequestCreateRequest, created_by_user_id: int
    ) -> LeaveRequestResponse:
        # Get employee info
        emp = await self.employee_queries.get_by_id(request.employee_id)
        if not emp:
            raise NotFoundException(
                f"Employee dengan ID {request.employee_id} tidak ditemukan"
            )

        employee_type = emp.employee_type

        # Validate dates
        validate_leave_dates(request.start_date, request.end_date)

        # Check overlap
        await validate_no_overlapping_leave(
            leave_queries=self.queries,
            employee_id=request.employee_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # Calculate days
        total_days = calculate_working_days(
            request.start_date, request.end_date, employee_type
        )

        leave_request_data = {
            "employee_id": request.employee_id,
            "leave_type": request.leave_type.value,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "total_days": total_days,
            "reason": request.reason,
            "created_by": created_by_user_id,
        }

        leave_request = await self.commands.create(leave_request_data)

        return LeaveRequestResponse.model_validate(leave_request)
