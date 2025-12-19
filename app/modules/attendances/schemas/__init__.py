"""Attendance schemas."""

from app.modules.attendances.schemas.requests import (
    CheckInRequest,
    CheckOutRequest,
    AttendanceCreateRequest,
    AttendanceUpdateRequest,
    BulkMarkPresentRequest,
    MarkPresentByIdRequest,
)
from app.modules.attendances.schemas.responses import (
    AttendanceResponse,
    AttendanceListResponse,
    AttendanceRecordInReport,
    EmployeeAttendanceReport,
    EmployeeAttendanceOverview,
    BulkMarkPresentSummary,
    LeaveDetailsResponse,
    AttendanceStatusCheckResponse,
)
from app.modules.attendances.schemas.shared import (
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
