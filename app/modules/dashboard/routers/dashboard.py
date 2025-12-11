"""
Dashboard router
"""
from typing import Annotated, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query

from app.core.dependencies.auth import get_current_user
from app.core.schemas.current_user import CurrentUser
from app.core.schemas import DataResponse
from app.core.schemas.helpers import create_success_response
from app.modules.dashboard.dependencies import DashboardServiceDep
from app.modules.dashboard.schemas.responses import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DataResponse[DashboardSummary],
    summary="Get Dashboard Summary",
    description="""
    Get personalized dashboard summary based on authenticated user's roles.

    **Multi-Role Support:**
    - Users with multiple roles will see widgets for ALL their roles
    - Example: HR Admin who is also an Employee sees both admin metrics and personal attendance

    **Role-Based Widgets:**
    - **Employee**: Personal attendance, leave requests, monthly summary
    - **Org Unit Head**: Team metrics, subordinate attendance, pending approvals
    - **HR Admin**: Company-wide stats, all pending approvals, headcount
    - **Guest**: Limited attendance tracking

    **Data Sources:**
    - Employee & OrgUnit data: Fetched via gRPC from workforce-service
    - Attendance & Leave data: Queried from local HRIS database

    **Permissions:**
    - No specific permission required - authenticated users only
    - Widget data automatically filtered by user's roles and permissions
    """,
)
async def get_dashboard_summary(
    service: DashboardServiceDep,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    target_date: Annotated[
        Optional[date],
        Query(description="Target date for dashboard data (default: today)")
    ] = None,
) -> DataResponse[DashboardSummary]:
    """
    Get multi-role dashboard summary.

    Returns personalized widgets based on user's assigned roles.
    """
    summary = await service.get_dashboard_summary(current_user, target_date)

    return create_success_response(
        message="Dashboard summary retrieved successfully",
        data=summary,
    )


@router.get(
    "/summary/roles",
    summary="Get Available Dashboard Roles",
    description="Get list of dashboard-enabled roles for current user",
)
async def get_dashboard_roles(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> DataResponse[dict]:
    """
    Get dashboard roles available to current user.

    Useful for frontend to know which widgets to expect.
    """
    dashboard_roles = []

    if "employee" in current_user.roles and current_user.employee_id:
        dashboard_roles.append("employee")

    if "org_unit_head" in current_user.roles and current_user.employee_id:
        dashboard_roles.append("org_unit_head")

    if "hr_admin" in current_user.roles or "super_admin" in current_user.roles:
        dashboard_roles.append("hr_admin")

    if "guest" in current_user.roles and not current_user.employee_id:
        dashboard_roles.append("guest")

    return create_success_response(
        message="Dashboard roles retrieved successfully",
        data={
            "user_id": current_user.id,
            "all_roles": current_user.roles,
            "dashboard_roles": dashboard_roles,
            "has_employee_record": current_user.employee_id is not None,
        },
    )
