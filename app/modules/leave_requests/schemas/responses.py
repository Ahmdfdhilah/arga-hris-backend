from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.modules.leave_requests.schemas.shared import LeaveType


class LeaveRequestResponse(BaseModel):
    """Response schema untuk leave request."""

    id: int
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: str
    created_by: Optional[int] = None
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
