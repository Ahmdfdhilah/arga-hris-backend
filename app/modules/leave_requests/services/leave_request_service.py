from typing import Optional, List, Tuple
from datetime import date

from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.employee_assignments.repositories import (
    AssignmentCommands,
    AssignmentQueries,
)
from app.modules.leave_requests.schemas.requests import (
    LeaveRequestCreateRequest,
    LeaveRequestUpdateRequest,
)
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    LeaveRequestListResponse,
)

from app.modules.leave_requests.use_cases.create_leave_request import (
    CreateLeaveRequestUseCase,
)
from app.modules.leave_requests.use_cases.get_leave_request import (
    GetLeaveRequestUseCase,
)
from app.modules.leave_requests.use_cases.update_leave_request import (
    UpdateLeaveRequestUseCase,
)
from app.modules.leave_requests.use_cases.delete_leave_request import (
    DeleteLeaveRequestUseCase,
)
from app.modules.leave_requests.use_cases.list_leave_requests import (
    ListMyLeaveRequestsUseCase,
    ListAllLeaveRequestsUseCase,
    ListTeamLeaveRequestsUseCase,
)


class LeaveRequestService:
    """Facade Service for Leave Request Use Cases"""

    def __init__(
        self,
        queries: LeaveRequestQueries,
        commands: LeaveRequestCommands,
        employee_queries: EmployeeQueries,
        assignment_commands: AssignmentCommands,
        assignment_queries: AssignmentQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.assignment_commands = assignment_commands
        self.assignment_queries = assignment_queries

        # Initialize Use Cases
        self.create_uc = CreateLeaveRequestUseCase(
            queries, commands, employee_queries, assignment_commands, assignment_queries
        )
        self.get_uc = GetLeaveRequestUseCase(
            queries, employee_queries, assignment_queries
        )
        self.update_uc = UpdateLeaveRequestUseCase(queries, commands, employee_queries)
        self.delete_uc = DeleteLeaveRequestUseCase(queries, commands)
        self.list_my_uc = ListMyLeaveRequestsUseCase(queries)
        self.list_all_uc = ListAllLeaveRequestsUseCase(
            queries, employee_queries, assignment_queries
        )
        self.list_team_uc = ListTeamLeaveRequestsUseCase(
            queries, employee_queries, assignment_queries
        )

    async def create_leave_request(
        self, request: LeaveRequestCreateRequest, created_by_user_id: str
    ) -> LeaveRequestResponse:
        return await self.create_uc.execute(request, created_by_user_id)

    async def get_leave_request_by_id(
        self, leave_request_id: int
    ) -> LeaveRequestResponse:
        return await self.get_uc.execute(leave_request_id)

    async def update_leave_request(
        self,
        leave_request_id: int,
        request: LeaveRequestUpdateRequest,
    ) -> LeaveRequestResponse:
        return await self.update_uc.execute(leave_request_id, request)

    async def delete_leave_request(self, leave_request_id: int) -> None:
        await self.delete_uc.execute(leave_request_id)

    async def get_my_leave_requests(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestResponse], int]:
        return await self.list_my_uc.execute(
            employee_id, start_date, end_date, leave_type, page, limit
        )

    async def list_all_leave_requests(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestListResponse], int]:
        return await self.list_all_uc.execute(
            employee_id, start_date, end_date, leave_type, page, limit
        )

    async def get_team_leave_requests(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[LeaveRequestListResponse], int]:
        return await self.list_team_uc.execute(
            employee_id, start_date, end_date, leave_type, page, limit
        )
