"""
Dashboard response schemas
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime


class BaseWidget(BaseModel):
    """Base widget schema for dashboard

    Note: widget_type is defined in each subclass with specific Literal type
    to enable proper type discrimination for the union type.
    """
    title: str = Field(..., description="Widget title for display")
    order: int = Field(default=0, description="Display order priority")


class AttendanceStatusToday(BaseModel):
    """Today's attendance status"""
    has_checked_in: bool
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: Optional[str] = None  # present, late, absent, leave
    location: Optional[str] = None


class EmployeeWidget(BaseWidget):
    """Personal metrics for employee role"""
    widget_type: Literal["employee"] = "employee"
    title: str = "Ringkasan Saya"

    # Attendance data
    attendance_today: AttendanceStatusToday
    monthly_attendance_percentage: float = Field(..., ge=0, le=100, description="Persentase kehadiran bulan ini")
    total_present_days: int = Field(..., description="Total hari hadir bulan ini")
    total_work_days: int = Field(..., description="Total hari kerja bulan ini")

    # Leave data
    pending_leave_requests: int = Field(..., description="Jumlah cuti pending approval")
    approved_leave_requests: int = Field(..., description="Jumlah cuti approved")
    remaining_leave_quota: Optional[int] = Field(None, description="Sisa kuota cuti")

    # Personal info
    employee_name: str
    employee_number: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None


class HRAdminWidget(BaseWidget):
    """HR admin metrics and pending items"""
    widget_type: Literal["hr_admin"] = "hr_admin"
    title: str = "HR Administration"

    # Employee stats
    total_active_employees: int
    total_inactive_employees: int
    new_employees_this_month: int

    # Pending approvals
    pending_leave_approvals: int = Field(..., description="Cuti menunggu approval")
    pending_attendance_corrections: int = Field(..., description="Koreksi absensi pending")

    # Today's snapshot
    employees_on_leave_today: int
    employees_present_today: int
    employees_absent_today: int

    # Payroll
    pending_payroll_processing: int = Field(0, description="Payroll yang belum diproses")


class OrgUnitHeadWidget(BaseWidget):
    """Manager/head of unit metrics for subordinates"""
    widget_type: Literal["org_unit_head"] = "org_unit_head"
    title: str = "Tim Saya"

    # Team info
    org_unit_name: str
    team_size: int = Field(..., description="Jumlah anggota tim")

    # Team attendance today
    team_present_today: int
    team_absent_today: int
    team_on_leave_today: int
    team_attendance_percentage: float = Field(..., ge=0, le=100, description="% kehadiran tim hari ini")

    # Pending approvals from team
    team_pending_leave_requests: int
    team_pending_work_submissions: int

    # Monthly team metrics
    monthly_team_attendance_avg: float = Field(..., ge=0, le=100, description="Rata-rata kehadiran tim bulan ini")


class GuestWidget(BaseWidget):
    """Limited widget for guest users"""
    widget_type: Literal["guest"] = "guest"
    title: str = "Absensi Tamu"

    attendance_today: AttendanceStatusToday
    total_attendance_records: int = Field(..., description="Total rekaman absensi")


class DashboardSummary(BaseModel):
    """Complete dashboard summary for authenticated user with multiple roles"""

    user_id: int
    full_name: str
    email: str
    roles: List[str] = Field(..., description="All roles assigned to user")

    # Dynamic widgets based on user's roles
    widgets: List[BaseWidget] = Field(..., description="Role-specific dashboard widgets")

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    timezone: str = Field(default="Asia/Jakarta")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "roles": ["hr_admin", "employee"],
                "widgets": [
                    {
                        "widget_type": "employee",
                        "title": "Ringkasan Saya",
                        "order": 1,
                        "attendance_today": {
                            "has_checked_in": True,
                            "check_in_time": "2025-12-04T08:15:00",
                            "status": "present"
                        },
                        "monthly_attendance_percentage": 95.5,
                        "total_present_days": 20,
                        "total_work_days": 22,
                        "pending_leave_requests": 1,
                        "employee_name": "John Doe"
                    },
                    {
                        "widget_type": "hr_admin",
                        "title": "HR Administration",
                        "order": 2,
                        "total_active_employees": 150,
                        "pending_leave_approvals": 8,
                        "employees_present_today": 142
                    }
                ],
                "generated_at": "2025-12-04T10:30:00",
                "timezone": "Asia/Jakarta"
            }
        }


class DashboardWidgetRequest(BaseModel):
    """Request for specific widget data"""
    widget_type: Literal["employee", "hr_admin", "org_unit_head", "guest"]
    date_filter: Optional[date] = Field(None, description="Filter for specific date (default: today)")
