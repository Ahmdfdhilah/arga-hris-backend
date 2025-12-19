"""
Centralized router configuration.
"""

from typing import Sequence
from fastapi import FastAPI, APIRouter
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
    # System routes (/, /health) tanpa prefix
    app.include_router(system_router, tags=["System"])

    # API routes dengan prefix /api/v1
    routers: Sequence[tuple[APIRouter, str, Sequence[str]]] = [
        (auth.router, "", ("Authentication",)),
        (roles.router, "", ("Roles & RBAC",)),
        (employees.router, "", ("Employees",)),
        (org_units.router, "", ("Organization Units",)),
        (attendances.router, "", ("Attendances",)),
        (leave_requests.router, "", ("Leave Requests",)),
        (scheduled_jobs.router, "", ("Scheduled Jobs",)),
        (dashboard.router, "", ("Dashboard",)),
        (assignments.router, "", ("Employee Assignments",)),
    ]

    for router, prefix, tags in routers:
        app.include_router(
            router, prefix=f"{settings.API_PREFIX}{prefix}", tags=list(tags)
        )
