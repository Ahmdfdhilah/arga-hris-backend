from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.attendance.repositories.attendance_repository import (
    AttendanceRepository,
)
from app.modules.attendance.services.attendance_service import AttendanceService
from app.modules.leave_requests.repositories.leave_request_repository import (
    LeaveRequestRepository,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient


def get_attendance_repository(db: PostgresDB) -> AttendanceRepository:
    return AttendanceRepository(db)


AttendanceRepositoryDep = Annotated[
    AttendanceRepository, Depends(get_attendance_repository)
]


def get_leave_request_repository(db: PostgresDB) -> LeaveRequestRepository:
    return LeaveRequestRepository(db)


LeaveRequestRepositoryDep = Annotated[
    LeaveRequestRepository, Depends(get_leave_request_repository)
]


def get_employee_grpc_client() -> EmployeeGRPCClient:
    return EmployeeGRPCClient()


EmployeeGRPCClientDep = Annotated[EmployeeGRPCClient, Depends(get_employee_grpc_client)]


def get_attendance_service(
    attendance_repo: AttendanceRepositoryDep,
    employee_client: EmployeeGRPCClientDep,
    leave_request_repo: LeaveRequestRepositoryDep,
) -> AttendanceService:
    return AttendanceService(attendance_repo, employee_client, leave_request_repo)


AttendanceServiceDep = Annotated[AttendanceService, Depends(get_attendance_service)]
