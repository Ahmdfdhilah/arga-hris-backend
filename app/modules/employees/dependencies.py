"""
Employee Module Dependencies - Refactored for Local Repository

Uses local SQLAlchemy repositories instead of gRPC clients for master data.
Includes event publishing to RabbitMQ.
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.employees.repositories.employee_repository import EmployeeRepository
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.services.employee_service import EmployeeService
from app.modules.employees.services.employee_account_service import EmployeeAccountService
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.core.messaging.event_publisher import EventPublisher, event_publisher


# ===========================================
# Repositories
# ===========================================

def get_employee_repository(db: PostgresDB) -> EmployeeRepository:
    """Get Employee repository instance"""
    return EmployeeRepository(db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]


def get_org_unit_repository(db: PostgresDB) -> OrgUnitRepository:
    """Get OrgUnit repository instance"""
    return OrgUnitRepository(db)


OrgUnitRepositoryDep = Annotated[OrgUnitRepository, Depends(get_org_unit_repository)]


def get_user_repository(db: PostgresDB) -> UserRepository:
    """Get User repository instance"""
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    """Get Role repository instance"""
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


# ===========================================
# Event Publisher
# ===========================================

def get_event_publisher() -> EventPublisher:
    """Get Event publisher instance"""
    return event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]


# ===========================================
# Services
# ===========================================

def get_employee_service(
    employee_repo: EmployeeRepositoryDep,
    org_unit_repo: OrgUnitRepositoryDep,
    user_repo: UserRepositoryDep,
    publisher: EventPublisherDep,
) -> EmployeeService:
    """Get Employee service instance with local repositories and event publisher"""
    return EmployeeService(employee_repo, org_unit_repo, user_repo, publisher)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]


def get_employee_account_service(
    employee_repo: EmployeeRepositoryDep,
    org_unit_repo: OrgUnitRepositoryDep,
    user_repo: UserRepositoryDep,
    role_repo: RoleRepositoryDep,
    publisher: EventPublisherDep,
) -> EmployeeAccountService:
    """Get Employee Account service instance with event publisher"""
    return EmployeeAccountService(
        employee_repo, org_unit_repo, user_repo, role_repo, publisher
    )


EmployeeAccountServiceDep = Annotated[
    EmployeeAccountService,
    Depends(get_employee_account_service)
]
