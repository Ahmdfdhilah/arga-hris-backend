from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.modules.leave_requests.schemas.shared import LeaveType


class ReplacementInfo(BaseModel):
    """Info pengganti sementara untuk leave request."""

    employee_id: int
    employee_name: Optional[str] = None
    employee_number: Optional[str] = None
    assignment_id: Optional[int] = None
    assignment_status: Optional[str] = None

    class Config:
        from_attributes = True


class LeaveRequestResponse(BaseModel):
    """Response schema untuk leave request."""

    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: str
    replacement: Optional[ReplacementInfo] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestListResponse(BaseModel):
    """Response schema untuk leave request list dengan employee info."""

    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_number: Optional[str] = None
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: str
    replacement_employee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
