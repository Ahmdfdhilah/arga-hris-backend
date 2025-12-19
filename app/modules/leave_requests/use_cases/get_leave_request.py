from typing import Optional
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    ReplacementInfo,
)
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.employee_assignments.repositories import AssignmentQueries
from app.core.exceptions import NotFoundException


class GetLeaveRequestUseCase:
    def __init__(
        self,
        queries: LeaveRequestQueries,
        employee_queries: Optional[EmployeeQueries] = None,
        assignment_queries: Optional[AssignmentQueries] = None,
    ):
        self.queries = queries
        self.employee_queries = employee_queries
        self.assignment_queries = assignment_queries

    async def execute(self, leave_request_id: int) -> LeaveRequestResponse:
        leave_request = await self.queries.get_by_id(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        # Build replacement info if replacement_employee_id exists
        replacement_info = None
        if leave_request.replacement_employee_id and self.employee_queries:
            replacement_emp = await self.employee_queries.get_by_id(
                leave_request.replacement_employee_id
            )
            if replacement_emp:
                assignment_status = None
                if leave_request.assignment_id and self.assignment_queries:
                    assignment = await self.assignment_queries.get_by_id(
                        leave_request.assignment_id
                    )
                    assignment_status = assignment.status if assignment else None

                replacement_info = ReplacementInfo(
                    employee_id=replacement_emp.id,
                    employee_name=replacement_emp.user.name
                    if replacement_emp.user
                    else None,
                    employee_number=replacement_emp.number,
                    assignment_id=leave_request.assignment_id,
                    assignment_status=assignment_status,
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
