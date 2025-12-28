"""
Use Case: Create Assignment

Creates a new employee assignment dengan status pending.
Akan di-link ke leave request.
"""

from typing import Optional

from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)
from app.modules.employee_assignments.schemas.requests import AssignmentCreateRequest
from app.modules.employee_assignments.schemas.responses import AssignmentResponse
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
)

from app.modules.employee_assignments.utils import AssignmentEventUtil


class CreateAssignmentUseCase:
    """Create new employee assignment."""

    def __init__(
        self,
        queries: AssignmentQueries,
        commands: AssignmentCommands,
        employee_queries: EmployeeQueries,
        org_unit_queries: OrgUnitQueries,
        leave_request_queries: LeaveRequestQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.org_unit_queries = org_unit_queries
        self.leave_request_queries = leave_request_queries

    async def execute(
        self,
        request: AssignmentCreateRequest,
        created_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Execute assignment creation."""
        employee = await self.employee_queries.get_by_id(request.employee_id)
        if not employee:
            raise NotFoundException(
                f"Employee dengan ID {request.employee_id} tidak ditemukan"
            )
        replaced_employee = await self.employee_queries.get_by_id(
            request.replaced_employee_id
        )
        if not replaced_employee:
            raise NotFoundException(
                f"Employee yang digantikan dengan ID {request.replaced_employee_id} tidak ditemukan"
            )

        if request.employee_id == request.replaced_employee_id:
            raise BadRequestException("Tidak bisa menggantikan diri sendiri")

        org_unit = await self.org_unit_queries.get_by_id(request.org_unit_id)
        if not org_unit:
            raise NotFoundException(
                f"Org unit dengan ID {request.org_unit_id} tidak ditemukan"
            )

        leave_request = await self.leave_request_queries.get_by_id(
            request.leave_request_id
        )
        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {request.leave_request_id} tidak ditemukan"
            )

        existing = await self.queries.check_overlapping(
            employee_id=request.employee_id,
            replaced_employee_id=request.replaced_employee_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        if existing:
            raise ConflictException(
                f"Assignment sudah ada untuk periode {request.start_date} - {request.end_date}"
            )

        assignment = EmployeeAssignment(
            employee_id=request.employee_id,
            replaced_employee_id=request.replaced_employee_id,
            org_unit_id=request.org_unit_id,
            start_date=request.start_date,
            end_date=request.end_date,
            status="pending",
            leave_request_id=request.leave_request_id,
            reason=request.reason,
            created_by=created_by,
        )

        created = await self.commands.create(assignment)
        created = await self.queries.get_by_id(created.id)

        await AssignmentEventUtil.publish("created", created)

        return AssignmentResponse.from_orm_with_relationships(created)
