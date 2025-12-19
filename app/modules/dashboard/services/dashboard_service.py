"""
Dashboard service for multi-role dashboard aggregation
"""

from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.schemas.current_user import CurrentUser
from app.modules.dashboard.schemas.responses import (
    DashboardSummary,
    BaseWidget,
    EmployeeWidget,
    HRAdminWidget,
    OrgUnitHeadWidget,
    GuestWidget,
    AttendanceStatusToday,
)
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries


class DashboardService:
    """Service for aggregating dashboard data based on user roles"""

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        employee_queries: EmployeeQueries,
        org_unit_queries: OrgUnitQueries,
    ):
        self.dashboard_repo = dashboard_repo
        self.employee_queries = employee_queries
        self.org_unit_queries = org_unit_queries

    async def _get_employee_dict(self, employee_id: int):
        emp = await self.employee_queries.get_by_id(employee_id)
        if not emp:
            return None
        return {
            "id": emp.id,
            "name": emp.user.name if emp.user else None,
            "employee_number": emp.number,
            "org_unit_id": emp.org_unit_id,
            "position": emp.position,
        }

    async def _list_employees_dict(
        self, page=1, limit=100, org_unit_id=None, is_active=True
    ):
        skip = (page - 1) * limit
        employees, total = await self.employee_queries.list(
            org_unit_id=org_unit_id, is_active=is_active, limit=limit, skip=skip
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return {
            "employees": [
                {"id": e.id, "name": e.user.name if e.user else None} for e in employees
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": total_pages,
            },
        }

    async def _get_org_unit_dict(self, org_unit_id: int):
        ou = await self.org_unit_queries.get_by_id(org_unit_id)
        if not ou:
            return None
        return {"id": ou.id, "name": ou.name}

    async def _list_org_units_dict(self, page=1, limit=100):
        skip = (page - 1) * limit
        org_units, total = await self.org_unit_queries.list(skip=skip, limit=limit)
        return {
            "org_units": [
                {"id": ou.id, "name": ou.name, "head_id": ou.head_id}
                for ou in org_units
            ]
        }

    async def get_dashboard_summary(
        self, current_user: CurrentUser, target_date: Optional[date] = None
    ) -> DashboardSummary:
        """
        Get complete dashboard summary for user based on all their roles.

        For users with multiple roles, includes widgets for EACH role.
        Example: HR admin who is also employee sees both admin panels and personal summary.

        Args:
            current_user: Authenticated user with roles and permissions
            target_date: Target date for data (default: today)

        Returns:
            DashboardSummary with role-specific widgets
        """
        if target_date is None:
            target_date = date.today()

        widgets: List[BaseWidget] = []
        order = 1

        # Build widgets based on user's roles
        # Order: employee (personal) -> org_unit_head (team) -> hr_admin (company-wide)

        if "employee" in current_user.roles and current_user.employee_id:
            widget = await self._get_employee_widget(current_user, target_date)
            widget.order = order
            widgets.append(widget)
            order += 1

        if "org_unit_head" in current_user.roles and current_user.employee_id:
            widget = await self._get_org_unit_head_widget(current_user, target_date)
            if widget:  # Only add if user actually heads a unit
                widget.order = order
                widgets.append(widget)
                order += 1

        if "hr_admin" in current_user.roles or "super_admin" in current_user.roles:
            widget = await self._get_hr_admin_widget(current_user, target_date)
            widget.order = order
            widgets.append(widget)
            order += 1

        if "guest" in current_user.roles and not current_user.employee_id:
            # Guest widget only if user is ONLY a guest (no employee record)
            widget = await self._get_guest_widget(current_user, target_date)
            widget.order = order
            widgets.append(widget)
            order += 1

        return DashboardSummary(
            user_id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            roles=current_user.roles,
            widgets=widgets,
            generated_at=datetime.utcnow(),
            timezone="Asia/Jakarta",
        )

    async def _get_employee_widget(
        self, current_user: CurrentUser, target_date: date
    ) -> EmployeeWidget:
        """Get personal metrics for employee role"""

        # Validate employee_id exists (nullability check)
        if not current_user.employee_id:
            return EmployeeWidget(
                attendance_today=AttendanceStatusToday(has_checked_in=False),
                monthly_attendance_percentage=0.0,
                total_present_days=0,
                total_work_days=0,
                pending_leave_requests=0,
                approved_leave_requests=0,
                remaining_leave_quota=None,
                employee_name=current_user.full_name,
            )

        # Fetch employee data from gRPC (workforce service)
        try:
            employee_data = await self._get_employee_dict(current_user.employee_id)
        except Exception as e:
            # Fallback if gRPC call fails
            return EmployeeWidget(
                attendance_today=AttendanceStatusToday(has_checked_in=False),
                monthly_attendance_percentage=0.0,
                total_present_days=0,
                total_work_days=0,
                pending_leave_requests=0,
                approved_leave_requests=0,
                remaining_leave_quota=None,
                employee_name=current_user.full_name,
            )

        # Get today's attendance from local DB
        attendance_today = await self._get_today_attendance(
            current_user.employee_id, target_date
        )

        # Get monthly attendance stats from local DB
        month_start = target_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            days=1
        )

        total_present_days = await self.dashboard_repo.count_monthly_attendance(
            current_user.employee_id, month_start, month_end
        )

        # Calculate work days in month (simplified: assume 22 work days)
        # TODO: Integrate with holiday/calendar service
        total_work_days = 22
        monthly_percentage = (
            (total_present_days / total_work_days * 100) if total_work_days > 0 else 0.0
        )

        # Get leave request counts from local DB
        pending_leave = await self.dashboard_repo.count_leave_requests_by_status(
            current_user.employee_id, "pending"
        )
        approved_leave = await self.dashboard_repo.count_leave_requests_by_status(
            current_user.employee_id, "approved"
        )

        # Get org_unit name if exists
        department_name = None
        if employee_data.get("org_unit_id"):
            try:
                org_unit_data = await self._get_org_unit_dict(
                    employee_data["org_unit_id"]
                )
                department_name = org_unit_data.get("name")
            except Exception:
                pass  # Org unit fetch failed, continue without it

        return EmployeeWidget(
            attendance_today=attendance_today,
            monthly_attendance_percentage=round(monthly_percentage, 1),
            total_present_days=total_present_days,
            total_work_days=total_work_days,
            pending_leave_requests=pending_leave,
            approved_leave_requests=approved_leave,
            remaining_leave_quota=None,  # TODO: Implement leave quota calculation
            employee_name=employee_data.get("name", current_user.full_name),
            employee_number=employee_data.get("employee_number"),
            position=employee_data.get("position"),
            department=department_name,
        )

    async def _get_hr_admin_widget(
        self, current_user: CurrentUser, target_date: date
    ) -> HRAdminWidget:
        """Get HR admin metrics for company-wide overview"""

        # Fetch employee counts from gRPC (workforce service)
        try:
            # Get total employees with filters
            active_employees_data = await self._list_employees_dict(
                page=1, limit=1, is_active=True
            )
            total_active = active_employees_data.get("pagination", {}).get(
                "total_items", 0
            )

            inactive_employees_data = await self._list_employees_dict(
                page=1, limit=1, is_active=False
            )
            total_inactive = inactive_employees_data.get("pagination", {}).get(
                "total_items", 0
            )

            # TODO: Add created_at filter to gRPC for new employees this month
            new_this_month = 0

        except Exception:
            # Fallback if gRPC fails
            total_active = 0
            total_inactive = 0
            new_this_month = 0

        # Get attendance/leave data from local DB
        pending_leave = await self.dashboard_repo.count_pending_leave_approvals()
        on_leave_today = await self.dashboard_repo.count_employees_on_leave_today(
            target_date
        )
        present_today = await self.dashboard_repo.count_attendances_today(target_date)

        # Absent today = total active - (present + on leave)
        absent_today = max(0, total_active - present_today - on_leave_today)

        return HRAdminWidget(
            total_active_employees=total_active,
            total_inactive_employees=total_inactive,
            new_employees_this_month=new_this_month,
            pending_leave_approvals=pending_leave,
            pending_attendance_corrections=0,  # TODO: Implement attendance correction system
            employees_on_leave_today=on_leave_today,
            employees_present_today=present_today,
            employees_absent_today=absent_today,
            pending_payroll_processing=0,  # TODO: Integrate with payroll module
        )

    async def _get_org_unit_head_widget(
        self, current_user: CurrentUser, target_date: date
    ) -> Optional[OrgUnitHeadWidget]:
        """Get manager/head of unit metrics for subordinates"""

        # Validate employee_id exists (nullability check)
        if not current_user.employee_id:
            return None

        # Check which org_unit this employee heads (via gRPC)
        try:
            # List all org_units and find which one has this employee as head
            # TODO: Add filter by head_employee_id to gRPC client
            org_units_data = await self._list_org_units_dict(page=1, limit=100)

            headed_org_unit = None
            for org_unit in org_units_data.get("org_units", []):
                # Check if current employee is head of this org_unit
                # This requires org_unit proto to include head_employee_id
                # For now, we'll skip this check
                pass

            # Alternative: Fetch employee data which might include org_unit_head info
            employee_data = await self._get_employee_dict(current_user.employee_id)
            org_unit_id = employee_data.get("org_unit_id")

            if not org_unit_id:
                return None  # Employee not assigned to org_unit

            # Get org_unit details
            org_unit_data = await self._get_org_unit_dict(org_unit_id)
            org_unit_name = org_unit_data.get("name", "Unknown")

        except Exception:
            return None  # gRPC call failed or employee not a head

        # Get team members from gRPC
        try:
            team_data = await self._list_employees_dict(
                page=1, limit=1000, org_unit_id=org_unit_id, is_active=True
            )
            team_employees = team_data.get("employees", [])
            team_size = len(team_employees)
            team_employee_ids = [emp["id"] for emp in team_employees]
        except Exception:
            team_size = 0
            team_employee_ids = []

        if not team_employee_ids:
            return OrgUnitHeadWidget(
                org_unit_name=org_unit_name,
                team_size=0,
                team_present_today=0,
                team_absent_today=0,
                team_on_leave_today=0,
                team_attendance_percentage=0.0,
                team_pending_leave_requests=0,
                team_pending_work_submissions=0,
                monthly_team_attendance_avg=0.0,
            )

        # Get team attendance/leave data from local DB
        team_present = await self.dashboard_repo.count_team_attendance_today(
            team_employee_ids, target_date
        )
        team_on_leave = await self.dashboard_repo.count_team_on_leave_today(
            team_employee_ids, target_date
        )
        team_pending_leave = (
            await self.dashboard_repo.count_team_pending_leave_requests(
                team_employee_ids
            )
        )

        team_absent = max(0, team_size - team_present - team_on_leave)
        team_attendance_pct = (team_present / team_size * 100) if team_size > 0 else 0.0

        return OrgUnitHeadWidget(
            org_unit_name=org_unit_name,
            team_size=team_size,
            team_present_today=team_present,
            team_absent_today=team_absent,
            team_on_leave_today=team_on_leave,
            team_attendance_percentage=round(team_attendance_pct, 1),
            team_pending_leave_requests=team_pending_leave,
            team_pending_work_submissions=0,  # TODO: Implement work submission approvals
            monthly_team_attendance_avg=0.0,  # TODO: Calculate monthly average
        )

    async def _get_guest_widget(
        self, current_user: CurrentUser, target_date: date
    ) -> GuestWidget:
        """Get limited widget for guest users"""

        # Guests don't have employee_id, use user_id in attendance (if system supports)
        # This is a simplified implementation
        attendance_today = AttendanceStatusToday(has_checked_in=False)

        # Count total attendance records for this guest
        # Note: This assumes attendance table can link to user_id for guests
        # Adjust based on your actual schema
        total_records = 0

        return GuestWidget(
            attendance_today=attendance_today,
            total_attendance_records=total_records,
        )

    async def _get_today_attendance(
        self, employee_id: int, target_date: date
    ) -> AttendanceStatusToday:
        """Get today's attendance status for an employee"""

        attendance = await self.dashboard_repo.get_today_attendance(
            employee_id, target_date
        )

        if not attendance:
            return AttendanceStatusToday(has_checked_in=False)

        return AttendanceStatusToday(
            has_checked_in=True,
            check_in_time=attendance.check_in_time,
            check_out_time=attendance.check_out_time,
            status=attendance.status if hasattr(attendance, "status") else "present",
            location=None,  # TODO: Format location from lat/long if needed
        )
