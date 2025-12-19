"""
Centralized router configuration.
"""

from fastapi import FastAPI
from app.config.settings import settings
from app.modules.auth.routers import auth
from app.modules.users.rbac.routers import roles
from app.modules.employees.routers import employees
from app.modules.employee_assignments.routers import assignments
from app.modules.org_units.routers import org_units
from app.modules.attendances.routers import attendances
from app.modules.leave_requests.routers import leave_requests
from app.modules.scheduled_jobs.routers import scheduled_jobs
from app.modules.dashboard.routers import dashboard
from app.core.routers.system import router as system_router


def setup_routers(app: FastAPI) -> None:
    """
    Register all API routers to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.include_router(system_router, tags=["System"])

    routers = [
        auth.router,
        roles.router,
        employees.router,
        org_units.router,
        attendances.router,
        leave_requests.router,
        scheduled_jobs.router,
        dashboard.router,
        assignments.router,
    ]

    for router in routers:
        app.include_router(router, prefix=settings.API_PREFIX)
