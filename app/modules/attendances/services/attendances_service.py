from typing import Optional, Tuple, List
from datetime import date
from fastapi import UploadFile, Request

from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.attendances.schemas import (
    CheckInRequest,
    CheckOutRequest,
    BulkMarkPresentRequest,
    AttendanceResponse
)
from app.modules.attendances.schemas.responses import (
    EmployeeAttendanceReport,
    EmployeeAttendanceOverview,
    AttendanceListResponse,
    BulkMarkPresentSummary,
    AttendanceStatusCheckResponse,
)

from app.modules.attendances.use_cases.check_in_use_case import CheckInUseCase
from app.modules.attendances.use_cases.check_out_use_case import CheckOutUseCase
from app.modules.attendances.use_cases.get_my_attendance_use_case import (
    GetMyAttendanceUseCase,
)
from app.modules.attendances.use_cases.get_team_attendance_use_case import (
    GetTeamAttendanceUseCase,
)
from app.modules.attendances.use_cases.get_all_attendances_use_case import (
    GetAllAttendancesUseCase,
)
from app.modules.attendances.use_cases.get_attendance_use_case import (
    GetAttendanceUseCase,
)
from app.modules.attendances.use_cases.get_attendance_report_use_case import (
    GetAttendanceReportUseCase,
)
from app.modules.attendances.use_cases.get_attendance_overview_use_case import (
    GetAttendanceOverviewUseCase,
)
from app.modules.attendances.use_cases.check_attendance_status_use_case import (
    CheckAttendanceStatusUseCase,
)
from app.modules.attendances.use_cases.bulk_mark_present_use_case import (
    BulkMarkPresentUseCase,
)
from app.modules.attendances.use_cases.mark_present_by_id_use_case import (
    MarkPresentByIdUseCase,
)


class AttendanceService:
    """Facade Service for Attendance Management"""

    def __init__(
        self,
        queries: AttendanceQueries,
        commands: AttendanceCommands,
        employee_queries: EmployeeQueries,
        leave_queries: LeaveRequestQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.leave_queries = leave_queries

        # Initialize Use Cases
        self.check_in_uc = CheckInUseCase(
            queries, commands, employee_queries, leave_queries
        )
        self.check_out_uc = CheckOutUseCase(
            queries, commands, employee_queries, leave_queries
        )
        self.get_my_attendance_uc = GetMyAttendanceUseCase(queries, employee_queries)
        self.get_team_attendance_uc = GetTeamAttendanceUseCase(
            queries, employee_queries
        )
        self.get_all_attendances_uc = GetAllAttendancesUseCase(
            queries, employee_queries
        )
        self.get_attendance_uc = GetAttendanceUseCase(queries)
        self.get_attendance_report_uc = GetAttendanceReportUseCase(
            queries, employee_queries
        )
        self.get_attendance_overview_uc = GetAttendanceOverviewUseCase(
            queries, employee_queries
        )
        self.check_attendance_status_uc = CheckAttendanceStatusUseCase(
            queries, employee_queries, leave_queries
        )
        self.bulk_mark_present_uc = BulkMarkPresentUseCase(
            queries, commands, employee_queries
        )
        self.mark_present_by_id_uc = MarkPresentByIdUseCase(queries, commands)

    async def check_in(
        self,
        employee_id: int,
        request: CheckInRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> AttendanceResponse:
        return await self.check_in_uc.execute(employee_id, request, request_obj, selfie)

    async def check_out(
        self,
        employee_id: int,
        request: CheckOutRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> Tuple[AttendanceResponse, str]:
        return await self.check_out_uc.execute(
            employee_id, request, request_obj, selfie
        )

    async def get_my_attendance(
        self,
        employee_id: int,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AttendanceListResponse], dict]:
        return await self.get_my_attendance_uc.execute(
            employee_id, type, start_date, end_date, page, limit
        )

    async def get_team_attendance(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[AttendanceListResponse], dict]:
        return await self.get_team_attendance_uc.execute(
            employee_id, start_date, end_date, status, page, limit
        )

    async def get_all_attendances(
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
        return await self.get_all_attendances_uc.execute(
            type, start_date, end_date, org_unit_id, employee_id, status, page, limit
        )

    async def get_attendance_by_id(self, attendance_id: int) -> AttendanceResponse:
        return await self.get_attendance_uc.execute(attendance_id)

    async def get_attendance_report(
        self,
        org_unit_id: int,
        start_date: date,
        end_date: date,
    ) -> List[EmployeeAttendanceReport]:
        return await self.get_attendance_report_uc.execute(
            org_unit_id, start_date, end_date
        )

    async def get_attendance_overview(
        self,
        org_unit_id: Optional[int],
        start_date: date,
        end_date: date,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[EmployeeAttendanceOverview], dict]:
        return await self.get_attendance_overview_uc.execute(
            org_unit_id, start_date, end_date, page, limit
        )

    async def check_attendance_status(
        self, employee_id: int
    ) -> AttendanceStatusCheckResponse:
        return await self.check_attendance_status_uc.execute(employee_id)

    async def bulk_mark_present(
        self,
        request: BulkMarkPresentRequest,
        created_by: str,
    ) -> BulkMarkPresentSummary:
        return await self.bulk_mark_present_uc.execute(request, created_by)

    async def mark_present_by_id(
        self,
        attendance_id: int,
        current_user_employee_id: int,
        admin_name: str,
        notes: Optional[str] = None,
    ) -> AttendanceResponse:
        return await self.mark_present_by_id_uc.execute(
            attendance_id, current_user_employee_id, admin_name, notes
        )
