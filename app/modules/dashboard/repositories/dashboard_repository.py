"""
Dashboard repository for local database queries
"""
from typing import List, Optional
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models.attendance import Attendance
from app.modules.leave_requests.models.leave_request import LeaveRequest


class DashboardRepository:
    """Repository for dashboard data aggregation from local HRIS database"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_attendance(
        self, employee_id: int, target_date: date
    ) -> Optional[Attendance]:
        """Get employee's attendance for specific date"""
        query = select(Attendance).where(
            and_(
                Attendance.employee_id == employee_id,
                func.date(Attendance.check_in_time) == target_date,
                Attendance.deleted_at.is_(None),
            )
        ).order_by(Attendance.check_in_time.desc())

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_monthly_attendance(
        self, employee_id: int, month_start: date, month_end: date
    ) -> int:
        """Count employee's attendance records in date range"""
        query = select(func.count(Attendance.id)).where(
            and_(
                Attendance.employee_id == employee_id,
                func.date(Attendance.check_in_time) >= month_start,
                func.date(Attendance.check_in_time) <= month_end,
                Attendance.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_leave_requests_by_status(
        self, employee_id: int, status: str
    ) -> int:
        """Count employee's leave requests by status"""
        query = select(func.count(LeaveRequest.id)).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == status,
                LeaveRequest.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    # ==================== HR Admin Dashboard Queries ====================

    async def count_active_employees(self) -> int:
        """Count total active employees in system"""
        # Note: Employee data is in gRPC service, this is placeholder
        # Real implementation should call EmployeeGRPCClient
        return 0

    async def count_pending_leave_approvals(self) -> int:
        """Count all pending leave requests"""
        query = select(func.count(LeaveRequest.id)).where(
            and_(
                # LeaveRequest.status == "pending",
                LeaveRequest.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_employees_on_leave_today(self, target_date: date) -> int:
        """Count employees on approved leave today"""
        query = select(func.count(LeaveRequest.employee_id.distinct())).where(
            and_(
                LeaveRequest.status == "approved",
                LeaveRequest.start_date <= target_date,
                LeaveRequest.end_date >= target_date,
                LeaveRequest.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_attendances_today(self, target_date: date) -> int:
        """Count employees who checked in today"""
        query = select(func.count(Attendance.employee_id.distinct())).where(
            and_(
                func.date(Attendance.check_in_time) == target_date,
                Attendance.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0


    async def get_team_employee_ids(self, org_unit_id: int) -> List[int]:
        """Get employee IDs in specific org unit

        Note: This requires calling EmployeeGRPCClient to get employees by org_unit_id
        This method is placeholder - actual implementation in service layer
        """
        return []

    async def count_team_attendance_today(
        self, employee_ids: List[int], target_date: date
    ) -> int:
        """Count team members who checked in today"""
        if not employee_ids:
            return 0

        query = select(func.count(Attendance.employee_id.distinct())).where(
            and_(
                Attendance.employee_id.in_(employee_ids),
                func.date(Attendance.check_in_time) == target_date,
                Attendance.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_team_on_leave_today(
        self, employee_ids: List[int], target_date: date
    ) -> int:
        """Count team members on approved leave today"""
        if not employee_ids:
            return 0

        query = select(func.count(LeaveRequest.employee_id.distinct())).where(
            and_(
                LeaveRequest.employee_id.in_(employee_ids),
                LeaveRequest.status == "approved",
                LeaveRequest.start_date <= target_date,
                LeaveRequest.end_date >= target_date,
                LeaveRequest.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_team_pending_leave_requests(
        self, employee_ids: List[int]
    ) -> int:
        """Count pending leave requests from team"""
        if not employee_ids:
            return 0

        query = select(func.count(LeaveRequest.id)).where(
            and_(
                LeaveRequest.employee_id.in_(employee_ids),
                LeaveRequest.status == "pending",
                LeaveRequest.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
