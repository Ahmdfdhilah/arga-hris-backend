"""
Employee Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.employees.repositories.employee_repository import EmployeeRepository
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.services.employee_service import EmployeeService
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.core.messaging.event_publisher import EventPublisher, event_publisher


def get_employee_repository(db: PostgresDB) -> EmployeeRepository:
    return EmployeeRepository(db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]


def get_org_unit_repository(db: PostgresDB) -> OrgUnitRepository:
    return OrgUnitRepository(db)


OrgUnitRepositoryDep = Annotated[OrgUnitRepository, Depends(get_org_unit_repository)]


def get_user_repository(db: PostgresDB) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


def get_event_publisher() -> EventPublisher:
    return event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]


def get_employee_service(
    employee_repo: EmployeeRepositoryDep,
    org_unit_repo: OrgUnitRepositoryDep,
    user_repo: UserRepositoryDep,
    role_repo: RoleRepositoryDep,
    publisher: EventPublisherDep,
) -> EmployeeService:
    return EmployeeService(
        employee_repo, org_unit_repo, user_repo, role_repo, publisher
    )


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
