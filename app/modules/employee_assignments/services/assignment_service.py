"""
Assignment Service - Facade / Orchestrator
"""

from typing import Optional, Tuple, List
from datetime import date

from app.modules.employee_assignments.schemas.requests import (
    AssignmentCreateRequest,
    AssignmentCancelRequest,
)
from app.modules.employee_assignments.schemas.responses import (
    AssignmentResponse,
    AssignmentListItemResponse,
)
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.modules.employee_assignments.use_cases import (
    CreateAssignmentUseCase,
    ActivateAssignmentUseCase,
    ExpireAssignmentUseCase,
    CancelAssignmentUseCase,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.core.exceptions import NotFoundException


class AssignmentService:
    """Facade untuk assignment operations."""

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

        # Wire use cases
        self.create_uc = CreateAssignmentUseCase(
            queries, commands, employee_queries, org_unit_queries, leave_request_queries
        )
        self.activate_uc = ActivateAssignmentUseCase(queries, commands)
        self.expire_uc = ExpireAssignmentUseCase(queries, commands)
        self.cancel_uc = CancelAssignmentUseCase(queries, commands)

    async def create(
        self,
        request: AssignmentCreateRequest,
        created_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Create new assignment."""
        return await self.create_uc.execute(request, created_by)

    async def get_by_id(self, assignment_id: int) -> AssignmentResponse:
        """Get assignment by ID."""
        assignment = await self.queries.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundException(
                f"Assignment dengan ID {assignment_id} tidak ditemukan"
            )
        return AssignmentResponse.from_orm_with_relationships(assignment)

    async def list(
        self,
        status: Optional[str] = None,
        employee_id: Optional[int] = None,
        replaced_employee_id: Optional[int] = None,
        org_unit_id: Optional[int] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AssignmentListItemResponse], int]:
        """List assignments dengan filters."""
        skip = (page - 1) * limit

        items, total = await self.queries.list(
            status=status,
            employee_id=employee_id,
            replaced_employee_id=replaced_employee_id,
            org_unit_id=org_unit_id,
            start_date_from=start_date_from,
            start_date_to=start_date_to,
            skip=skip,
            limit=limit,
        )

        responses = [AssignmentListItemResponse.from_assignment(item) for item in items]

        return responses, total

    async def cancel(
        self,
        assignment_id: int,
        request: Optional[AssignmentCancelRequest] = None,
        updated_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Cancel assignment."""
        return await self.cancel_uc.execute(assignment_id, request, updated_by)

    async def activate(
        self,
        assignment_id: int,
        updated_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Activate assignment (for scheduler)."""
        return await self.activate_uc.execute(assignment_id, updated_by)

    async def expire(
        self,
        assignment_id: int,
        updated_by: Optional[str] = None,
    ) -> AssignmentResponse:
        """Expire assignment (for scheduler)."""
        return await self.expire_uc.execute(assignment_id, updated_by)
