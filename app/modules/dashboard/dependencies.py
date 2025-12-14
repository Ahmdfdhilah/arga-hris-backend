"""
Dashboard module dependencies
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.database import get_db
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.services.dashboard_service import DashboardService
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries


def get_dashboard_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> DashboardRepository:
    return DashboardRepository(db)


DashboardRepositoryDep = Annotated[DashboardRepository, Depends(get_dashboard_repository)]


def get_employee_queries(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_org_unit_queries(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> OrgUnitQueries:
    return OrgUnitQueries(db)


OrgUnitQueriesDep = Annotated[OrgUnitQueries, Depends(get_org_unit_queries)]


def get_dashboard_service(
    dashboard_repo: DashboardRepositoryDep,
    employee_queries: EmployeeQueriesDep,
    org_unit_queries: OrgUnitQueriesDep,
) -> DashboardService:
    return DashboardService(dashboard_repo, employee_queries, org_unit_queries)


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
