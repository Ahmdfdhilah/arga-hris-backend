"""
OrgUnit Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.services.org_unit_service import OrgUnitService
from app.core.messaging.event_publisher import EventPublisher, event_publisher


def get_org_unit_queries(db: PostgresDB) -> OrgUnitQueries:
    return OrgUnitQueries(db)


OrgUnitQueriesDep = Annotated[OrgUnitQueries, Depends(get_org_unit_queries)]


def get_org_unit_commands(db: PostgresDB) -> OrgUnitCommands:
    return OrgUnitCommands(db)


OrgUnitCommandsDep = Annotated[OrgUnitCommands, Depends(get_org_unit_commands)]


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_employee_commands(db: PostgresDB) -> EmployeeCommands:
    return EmployeeCommands(db)


EmployeeCommandsDep = Annotated[EmployeeCommands, Depends(get_employee_commands)]


def get_event_publisher() -> EventPublisher:
    return event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]


def get_org_unit_service(
    queries: OrgUnitQueriesDep,
    commands: OrgUnitCommandsDep,
    employee_queries: EmployeeQueriesDep,
    employee_commands: EmployeeCommandsDep,
    publisher: EventPublisherDep,
) -> OrgUnitService:
    return OrgUnitService(
        queries, commands, employee_queries, employee_commands, publisher
    )


OrgUnitServiceDep = Annotated[OrgUnitService, Depends(get_org_unit_service)]
