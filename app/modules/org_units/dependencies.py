"""
OrgUnit Module Dependencies - Refactored for Local Repository

Uses local SQLAlchemy repositories instead of gRPC clients for master data.
Includes event publishing to RabbitMQ.
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.org_units.repositories.org_unit_repository import OrgUnitRepository
from app.modules.employees.repositories.employee_repository import EmployeeRepository
from app.modules.org_units.services.org_unit_service import OrgUnitService
from app.core.messaging.event_publisher import EventPublisher, event_publisher


# ===========================================
# Repositories
# ===========================================

def get_org_unit_repository(db: PostgresDB) -> OrgUnitRepository:
    """Get OrgUnit repository instance"""
    return OrgUnitRepository(db)


OrgUnitRepositoryDep = Annotated[OrgUnitRepository, Depends(get_org_unit_repository)]


def get_employee_repository(db: PostgresDB) -> EmployeeRepository:
    """Get Employee repository instance"""
    return EmployeeRepository(db)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]


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

def get_org_unit_service(
    org_unit_repo: OrgUnitRepositoryDep,
    employee_repo: EmployeeRepositoryDep,
    publisher: EventPublisherDep,
) -> OrgUnitService:
    """Get OrgUnit service instance with local repositories and event publisher"""
    return OrgUnitService(org_unit_repo, employee_repo, publisher)


OrgUnitServiceDep = Annotated[OrgUnitService, Depends(get_org_unit_service)]
