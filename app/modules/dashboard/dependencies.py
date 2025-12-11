"""
Dashboard module dependencies
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.database import get_db
from app.modules.dashboard.repositories.dashboard_repository import DashboardRepository
from app.modules.dashboard.services.dashboard_service import DashboardService
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient


# Repository dependency
def get_dashboard_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> DashboardRepository:
    """Dependency for dashboard repository"""
    return DashboardRepository(db)


DashboardRepositoryDep = Annotated[
    DashboardRepository, Depends(get_dashboard_repository)
]


# gRPC Client dependencies
def get_employee_grpc_client() -> EmployeeGRPCClient:
    """Dependency for employee gRPC client"""
    return EmployeeGRPCClient()


EmployeeGRPCClientDep = Annotated[
    EmployeeGRPCClient, Depends(get_employee_grpc_client)
]


def get_org_unit_grpc_client() -> OrgUnitGRPCClient:
    """Dependency for org_unit gRPC client"""
    return OrgUnitGRPCClient()


OrgUnitGRPCClientDep = Annotated[
    OrgUnitGRPCClient, Depends(get_org_unit_grpc_client)
]


# Service dependency (combines all dependencies)
def get_dashboard_service(
    dashboard_repo: DashboardRepositoryDep,
    employee_client: EmployeeGRPCClientDep,
    org_unit_client: OrgUnitGRPCClientDep,
) -> DashboardService:
    """Dependency for dashboard service with all injected dependencies"""
    return DashboardService(dashboard_repo, employee_client, org_unit_client)


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
