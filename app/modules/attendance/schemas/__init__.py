"""Attendance schemas."""

from app.modules.attendance.schemas.requests import (
    CheckInRequest,
    CheckOutRequest,
    AttendanceCreateRequest,
    AttendanceUpdateRequest,
    BulkMarkPresentRequest,
    MarkPresentByIdRequest,
)
from app.modules.attendance.schemas.responses import (
    AttendanceResponse,
    AttendanceListResponse,
    AttendanceRecordInReport,
    EmployeeAttendanceReport,
    EmployeeAttendanceOverview,
    BulkMarkPresentSummary,
    LeaveDetailsResponse,
    AttendanceStatusCheckResponse,
)
from app.modules.attendance.schemas.shared import (
    AttendanceStatus,
)

__all__ = [
    # Requests
    "CheckInRequest",
    "CheckOutRequest",
    "AttendanceCreateRequest",
    "AttendanceUpdateRequest",
    "BulkMarkPresentRequest",
    "MarkPresentByIdRequest",
    # Responses
    "AttendanceResponse",
    "AttendanceListResponse",
    "AttendanceRecordInReport",
    "EmployeeAttendanceReport",
    "EmployeeAttendanceOverview",
    "BulkMarkPresentSummary",
    "LeaveDetailsResponse",
    "AttendanceStatusCheckResponse",
    # Shared (dipakai di requests dan responses)
    "AttendanceStatus",
]
