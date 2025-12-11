from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.work_submissions.repositories.work_submission_repository import (
    WorkSubmissionRepository,
)
from app.modules.work_submissions.services.work_submission_service import (
    WorkSubmissionService,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient


def get_work_submission_repository(db: PostgresDB) -> WorkSubmissionRepository:
    return WorkSubmissionRepository(db)


WorkSubmissionRepositoryDep = Annotated[
    WorkSubmissionRepository, Depends(get_work_submission_repository)
]


def get_employee_grpc_client() -> EmployeeGRPCClient:
    return EmployeeGRPCClient()


EmployeeGRPCClientDep = Annotated[EmployeeGRPCClient, Depends(get_employee_grpc_client)]


def get_work_submission_service(
    work_submission_repo: WorkSubmissionRepositoryDep,
    employee_client: EmployeeGRPCClientDep,
) -> WorkSubmissionService:
    return WorkSubmissionService(work_submission_repo, employee_client)


WorkSubmissionServiceDep = Annotated[
    WorkSubmissionService, Depends(get_work_submission_service)
]
