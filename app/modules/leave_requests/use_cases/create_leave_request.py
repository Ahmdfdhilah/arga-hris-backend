from datetime import date
from typing import Optional

from app.modules.leave_requests.schemas.requests import LeaveRequestCreateRequest
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    ReplacementInfo,
)
from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.employee_assignments.repositories import (
    AssignmentCommands,
    AssignmentQueries,
)
from app.core.exceptions import NotFoundException, BadRequestException
from app.modules.leave_requests.utils.total_days import (
    validate_no_overlapping_leave,
    validate_leave_dates,
)
from app.core.utils.workforce import calculate_working_days


class CreateLeaveRequestUseCase:
    def __init__(
        self,
        queries: LeaveRequestQueries,
        commands: LeaveRequestCommands,
        employee_queries: EmployeeQueries,
        assignment_commands: Optional[AssignmentCommands] = None,
        assignment_queries: Optional[AssignmentQueries] = None,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.assignment_commands = assignment_commands
        self.assignment_queries = assignment_queries

    async def execute(
        self, request: LeaveRequestCreateRequest, created_by_user_id: str
    ) -> LeaveRequestResponse:
        # Get employee info
        emp = await self.employee_queries.get_by_id(request.employee_id)
        if not emp:
            raise NotFoundException(
                f"Employee dengan ID {request.employee_id} tidak ditemukan"
            )

        employee_type = emp.type

        # Check if employee is currently assigned as replacement for someone
        if self.assignment_queries:
            active_assignments = await self.assignment_queries.get_active_for_employee(
                employee_id=request.employee_id,
                as_of_date=request.start_date,
            )
            # Check if any assignment overlaps with the leave request period
            for assignment in active_assignments:
                if (
                    assignment.start_date <= request.end_date
                    and assignment.end_date >= request.start_date
                ):
                    replaced_name = "karyawan lain"
                    if (
                        assignment.replaced_employee
                        and assignment.replaced_employee.user
                    ):
                        replaced_name = assignment.replaced_employee.user.name
                    raise BadRequestException(
                        f"Tidak dapat mengajukan cuti. Anda sedang ditugaskan sebagai pengganti {replaced_name} "
                        f"dari {assignment.start_date} sampai {assignment.end_date}."
                    )

        # Validate replacement employee if provided
        replacement_emp = None
        if request.replacement_employee_id:
            replacement_emp = await self.employee_queries.get_by_id(
                request.replacement_employee_id
            )
            if not replacement_emp:
                raise NotFoundException(
                    f"Replacement employee dengan ID {request.replacement_employee_id} tidak ditemukan"
                )

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
            "replacement_employee_id": request.replacement_employee_id,
        }

        leave_request = await self.commands.create(leave_request_data)

        # Create assignment if replacement provided
        assignment = None
        if request.replacement_employee_id and self.assignment_commands:
            # Determine initial status - active immediately if starts today
            today = date.today()
            initial_status = "active" if request.start_date <= today else "pending"

            assignment_data = {
                "employee_id": request.replacement_employee_id,
                "replaced_employee_id": request.employee_id,
                "org_unit_id": emp.org_unit_id,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "status": initial_status,
                "leave_request_id": leave_request.id,
                "reason": f"Pengganti untuk cuti: {request.reason}",
                "created_by": created_by_user_id,
            }
            assignment = await self.assignment_commands.create(assignment_data)

            # Update leave_request with assignment_id
            await self.commands.update(
                leave_request.id, {"assignment_id": assignment.id}
            )

        # Build response with replacement info
        replacement_info = None
        if replacement_emp:
            replacement_info = ReplacementInfo(
                employee_id=replacement_emp.id,
                employee_name=replacement_emp.user.name
                if replacement_emp.user
                else None,
                employee_number=replacement_emp.number,
                assignment_id=assignment.id if assignment else None,
                assignment_status=assignment.status if assignment else None,
            )

        return LeaveRequestResponse(
            id=leave_request.id,
            employee_id=leave_request.employee_id,
            leave_type=leave_request.leave_type,
            start_date=leave_request.start_date,
            end_date=leave_request.end_date,
            total_days=leave_request.total_days,
            reason=leave_request.reason,
            replacement=replacement_info,
            created_by=str(leave_request.created_by)
            if leave_request.created_by
            else None,
            created_at=leave_request.created_at,
            updated_at=leave_request.updated_at,
        )
