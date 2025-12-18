from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_serializer
from app.modules.attendance.schemas.shared import AttendanceStatus


class AttendanceResponse(BaseModel):
    """Response schema untuk attendance."""

    id: int
    employee_id: int
    org_unit_id: Optional[int] = None
    attendance_date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    work_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    created_by: Optional[str] = None
    check_in_submitted_at: Optional[datetime] = None
    check_in_submitted_ip: Optional[str] = None
    check_in_notes: Optional[str] = None
    check_in_selfie_path: Optional[str] = Field(None, exclude=True)
    check_in_latitude: Optional[Decimal] = None
    check_in_longitude: Optional[Decimal] = None
    check_in_location_name: Optional[str] = None
    check_out_submitted_at: Optional[datetime] = None
    check_out_submitted_ip: Optional[str] = None
    check_out_notes: Optional[str] = None
    check_out_selfie_path: Optional[str] = Field(None, exclude=True)
    check_out_latitude: Optional[Decimal] = None
    check_out_longitude: Optional[Decimal] = None
    check_out_location_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    check_in_selfie_url: Optional[str] = None
    check_out_selfie_url: Optional[str] = None

    @field_serializer("work_hours", "overtime_hours")
    def serialize_hours(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    @field_serializer(
        "check_in_latitude",
        "check_in_longitude",
        "check_out_latitude",
        "check_out_longitude",
    )
    def serialize_coordinates(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal coordinates to float for JSON compatibility."""
        return float(value) if value is not None else None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_urls(
        cls,
        attendance,
        check_in_url: Optional[str] = None,
        check_out_url: Optional[str] = None,
    ):
        """Create response from ORM model with generated URLs"""
        response = cls.model_validate(attendance)
        response.check_in_selfie_url = check_in_url
        response.check_out_selfie_url = check_out_url
        return response


class AttendanceListResponse(BaseModel):
    """Response schema untuk attendance list dengan employee dan org unit info."""

    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_number: Optional[str] = None
    org_unit_id: Optional[int] = None
    org_unit_name: Optional[str] = None
    attendance_date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    work_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    check_in_submitted_at: Optional[datetime] = None
    check_in_submitted_ip: Optional[str] = None
    check_in_notes: Optional[str] = None
    check_in_selfie_path: Optional[str] = Field(None, exclude=True)
    check_in_latitude: Optional[Decimal] = None
    check_in_longitude: Optional[Decimal] = None
    check_in_location_name: Optional[str] = None
    check_out_submitted_at: Optional[datetime] = None
    check_out_submitted_ip: Optional[str] = None
    check_out_notes: Optional[str] = None
    check_out_selfie_path: Optional[str] = Field(None, exclude=True)
    check_out_latitude: Optional[Decimal] = None
    check_out_longitude: Optional[Decimal] = None
    check_out_location_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    check_in_selfie_url: Optional[str] = None
    check_out_selfie_url: Optional[str] = None

    @field_serializer("work_hours", "overtime_hours")
    def serialize_hours(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    @field_serializer(
        "check_in_latitude",
        "check_in_longitude",
        "check_out_latitude",
        "check_out_longitude",
    )
    def serialize_coordinates(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal coordinates to float for JSON compatibility."""
        return float(value) if value is not None else None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_urls(
        cls,
        attendance,
        employee_name: Optional[str] = None,
        employee_number: Optional[str] = None,
        org_unit_name: Optional[str] = None,
        check_in_url: Optional[str] = None,
        check_out_url: Optional[str] = None,
    ):
        """Create response from ORM model with employee/org unit info and generated URLs"""
        response = cls.model_validate(attendance)
        response.employee_name = employee_name
        response.employee_number = employee_number
        response.org_unit_name = org_unit_name
        response.check_in_selfie_url = check_in_url
        response.check_out_selfie_url = check_out_url
        return response


class AttendanceRecordInReport(BaseModel):
    """Schema untuk single attendance record dalam report."""

    attendance_date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    work_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None

    @field_serializer("work_hours", "overtime_hours")
    def serialize_hours(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    class Config:
        from_attributes = True


class EmployeeAttendanceReport(BaseModel):
    """Response schema untuk attendance report per employee."""

    employee_id: int
    employee_name: str
    employee_number: Optional[str] = None
    employee_position: Optional[str] = None
    employee_type: Optional[str] = None
    org_unit_id: Optional[int] = None
    org_unit_name: Optional[str] = None
    attendances: list[AttendanceRecordInReport] = []
    total_present_days: int = 0
    total_work_hours: Optional[Decimal] = None
    total_overtime_hours: Optional[Decimal] = None

    @field_serializer("total_work_hours", "total_overtime_hours")
    def serialize_total_hours(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    class Config:
        from_attributes = True


class EmployeeAttendanceOverview(BaseModel):
    """Response schema untuk attendance overview per employee (untuk table dengan paginasi)."""

    employee_id: int
    employee_name: str
    employee_number: Optional[str] = None
    employee_position: Optional[str] = None
    org_unit_id: Optional[int] = None
    org_unit_name: Optional[str] = None
    total_present: int = 0
    total_absent: int = 0
    total_leave: int = 0
    total_hybrid: int = 0
    total_work_hours: Optional[Decimal] = None
    total_overtime_hours: Optional[Decimal] = None

    @field_serializer("total_work_hours", "total_overtime_hours")
    def serialize_total_hours(self, value: Optional[Decimal]) -> Optional[float]:
        """Serialize Decimal to float for JSON compatibility."""
        return float(value) if value is not None else None

    class Config:
        from_attributes = True


class BulkMarkPresentSummary(BaseModel):
    """Response schema untuk bulk mark present summary."""

    total_employees: int
    created: int
    updated: int
    skipped: int
    attendance_date: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class LeaveDetailsResponse(BaseModel):
    """Response schema untuk detail cuti."""

    leave_type: str
    start_date: str
    end_date: str
    total_days: int
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceStatusCheckResponse(BaseModel):
    """Response schema untuk check attendance status."""

    can_attend: bool
    reason: Optional[str] = None
    is_on_leave: bool
    is_working_day: bool
    employee_type: Optional[str] = None
    leave_details: Optional[LeaveDetailsResponse] = None

    class Config:
        from_attributes = True
