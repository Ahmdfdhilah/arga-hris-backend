from app.modules.leave_requests.schemas.requests import LeaveRequestUpdateRequest
from app.modules.leave_requests.schemas.responses import LeaveRequestResponse
from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import NotFoundException, BadRequestException
from app.modules.leave_requests.utils.total_days import (
    validate_no_overlapping_leave,
    validate_leave_dates,
)
from app.core.utils.workforce import calculate_working_days


class UpdateLeaveRequestUseCase:
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
        self,
        leave_request_id: int,
        request: LeaveRequestUpdateRequest,
        updated_by_user_id: str,
    ) -> LeaveRequestResponse:
        leave_request = await self.queries.get_by_id(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        update_data = request.model_dump(exclude_none=True)

        if not update_data:
            raise BadRequestException("Tidak ada data yang akan diupdate")

        new_start_date = update_data.get("start_date", leave_request.start_date)
        new_end_date = update_data.get("end_date", leave_request.end_date)

        validate_leave_dates(new_start_date, new_end_date)

        if "start_date" in update_data or "end_date" in update_data:
            await validate_no_overlapping_leave(
                leave_queries=self.queries,
                employee_id=leave_request.employee_id,
                start_date=new_start_date,
                end_date=new_end_date,
                exclude_leave_request_id=leave_request_id,
            )

            emp = await self.employee_queries.get_by_id(leave_request.employee_id)
            if not emp:
                raise NotFoundException(
                    f"Employee {leave_request.employee_id} not found"
                )

            employee_type = emp.type

            if "start_date" in update_data:
                leave_request.start_date = update_data["start_date"]
            if "end_date" in update_data:
                leave_request.end_date = update_data["end_date"]

            leave_request.total_days = calculate_working_days(
                new_start_date, new_end_date, employee_type
            )

        if "leave_type" in update_data:
            leave_request.leave_type = update_data["leave_type"].value
        if "reason" in update_data:
            leave_request.reason = update_data["reason"]
        if "replacement_employee_id" in update_data:
            leave_request.replacement_employee_id = update_data[
                "replacement_employee_id"
            ]

        leave_request.updated_by = updated_by_user_id

        updated = await self.commands.update(leave_request)

        return LeaveRequestResponse.model_validate(updated)
