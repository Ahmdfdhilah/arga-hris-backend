from datetime import date
from typing import Optional

from app.modules.leave_requests.models.leave_request import LeaveRequest
from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)
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
        emp = await self.employee_queries.get_by_id(request.employee_id)
        if not emp:
            raise NotFoundException(
                f"Employee dengan ID {request.employee_id} tidak ditemukan"
            )

        employee_type = emp.type

        if self.assignment_queries:
            active_assignments = await self.assignment_queries.get_active_for_employee(
                employee_id=request.employee_id,
                as_of_date=request.start_date,
            )
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

        replacement_emp = None
        if request.replacement_employee_id:
            replacement_emp = await self.employee_queries.get_by_id(
                request.replacement_employee_id
            )
            if not replacement_emp:
                raise NotFoundException(
                    f"Replacement employee dengan ID {request.replacement_employee_id} tidak ditemukan"
                )

        validate_leave_dates(request.start_date, request.end_date)

        await validate_no_overlapping_leave(
            leave_queries=self.queries,
            employee_id=request.employee_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        total_days = calculate_working_days(
            request.start_date, request.end_date, employee_type
        )

        leave_request = LeaveRequest(
            employee_id=request.employee_id,
            leave_type=request.leave_type.value,
            start_date=request.start_date,
            end_date=request.end_date,
            total_days=total_days,
            reason=request.reason,
            created_by=created_by_user_id,
            replacement_employee_id=request.replacement_employee_id,
        )

        created_leave = await self.commands.create(leave_request)

        assignment = None
        if request.replacement_employee_id and self.assignment_commands:
            today = date.today()
            initial_status = "active" if request.start_date <= today else "pending"

            assignment = EmployeeAssignment(
                employee_id=request.replacement_employee_id,
                replaced_employee_id=request.employee_id,
                org_unit_id=emp.org_unit_id,
                start_date=request.start_date,
                end_date=request.end_date,
                status=initial_status,
                leave_request_id=created_leave.id,
                reason=f"Pengganti untuk cuti: {request.reason}",
                created_by=created_by_user_id,
            )
            created_assignment = await self.assignment_commands.create(assignment)

            created_leave.assignment_id = created_assignment.id
            await self.commands.update(created_leave)
            
        replacement_info = None
        if replacement_emp:
            replacement_info = ReplacementInfo(
                employee_id=replacement_emp.id,
                employee_name=replacement_emp.user.name
                if replacement_emp.user
                else None,
                employee_number=replacement_emp.code,
                assignment_id=created_assignment.id if created_assignment else None,
                assignment_status=created_assignment.status
                if created_assignment
                else None,
            )

        return LeaveRequestResponse(
            id=created_leave.id,
            employee_id=created_leave.employee_id,
            leave_type=created_leave.leave_type,
            start_date=created_leave.start_date,
            end_date=created_leave.end_date,
            total_days=created_leave.total_days,
            reason=created_leave.reason,
            replacement=replacement_info,
            created_by=str(created_leave.created_by)
            if created_leave.created_by
            else None,
            created_at=created_leave.created_at,
            updated_at=created_leave.updated_at,
        )
