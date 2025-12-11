from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.modules.employees.services.employee_service import EmployeeService
from app.modules.employees.services.employee_account_service import EmployeeAccountService
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.guests.repositories.guest_repository import GuestRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.core.dependencies.database import PostgresDB


def get_employee_grpc_client() -> EmployeeGRPCClient:
    return EmployeeGRPCClient()


EmployeeGRPCClientDep = Annotated[
    EmployeeGRPCClient, Depends(get_employee_grpc_client)
]


def get_org_unit_grpc_client() -> OrgUnitGRPCClient:
    return OrgUnitGRPCClient()


OrgUnitGRPCClientDep = Annotated[
    OrgUnitGRPCClient, Depends(get_org_unit_grpc_client)
]


def get_user_repository(db: PostgresDB) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_guest_repository(db: PostgresDB) -> GuestRepository:
    return GuestRepository(db)


GuestRepositoryDep = Annotated[GuestRepository, Depends(get_guest_repository)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


def get_employee_service(
    client: EmployeeGRPCClientDep,
    user_repo: UserRepositoryDep
) -> EmployeeService:
    return EmployeeService(client, user_repo)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]


def get_employee_account_service(
    employee_client: EmployeeGRPCClientDep,
    user_repo: UserRepositoryDep,
    guest_repo: GuestRepositoryDep,
    role_repo: RoleRepositoryDep,
    org_unit_client: OrgUnitGRPCClientDep,
) -> EmployeeAccountService:
    return EmployeeAccountService(
        employee_client, user_repo, guest_repo, role_repo, org_unit_client
    )


EmployeeAccountServiceDep = Annotated[
    EmployeeAccountService,
    Depends(get_employee_account_service)
]
