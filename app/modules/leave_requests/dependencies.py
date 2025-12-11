from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.leave_requests.repositories.leave_request_repository import (
    LeaveRequestRepository,
)
from app.modules.leave_requests.services.leave_request_service import (
    LeaveRequestService,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient


def get_leave_request_repository(db: PostgresDB) -> LeaveRequestRepository:
    return LeaveRequestRepository(db)


LeaveRequestRepositoryDep = Annotated[
    LeaveRequestRepository, Depends(get_leave_request_repository)
]


def get_employee_grpc_client() -> EmployeeGRPCClient:
    return EmployeeGRPCClient()


EmployeeGRPCClientDep = Annotated[EmployeeGRPCClient, Depends(get_employee_grpc_client)]


def get_leave_request_service(
    leave_request_repo: LeaveRequestRepositoryDep,
    employee_client: EmployeeGRPCClientDep,
) -> LeaveRequestService:
    return LeaveRequestService(leave_request_repo, employee_client)


LeaveRequestServiceDep = Annotated[
    LeaveRequestService, Depends(get_leave_request_service)
]
