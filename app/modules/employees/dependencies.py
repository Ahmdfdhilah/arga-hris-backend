"""
Employee Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.modules.users.rbac.repositories import RoleQueries
from app.core.messaging.event_publisher import EventPublisher, event_publisher

from app.modules.employees.services.employee_service import EmployeeService


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_employee_commands(db: PostgresDB) -> EmployeeCommands:
    return EmployeeCommands(db)


EmployeeCommandsDep = Annotated[EmployeeCommands, Depends(get_employee_commands)]


def get_org_unit_queries(db: PostgresDB) -> OrgUnitQueries:
    return OrgUnitQueries(db)


OrgUnitQueriesDep = Annotated[OrgUnitQueries, Depends(get_org_unit_queries)]


def get_user_queries(db: PostgresDB) -> UserQueries:
    return UserQueries(db)


UserQueriesDep = Annotated[UserQueries, Depends(get_user_queries)]


def get_user_commands(db: PostgresDB) -> UserCommands:
    return UserCommands(db)


UserCommandsDep = Annotated[UserCommands, Depends(get_user_commands)]


def get_role_queries(db: PostgresDB) -> RoleQueries:
    return RoleQueries(db)


RoleQueriesDep = Annotated[RoleQueries, Depends(get_role_queries)]


def get_event_publisher() -> EventPublisher:
    return event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]


def get_employee_service(
    queries: EmployeeQueriesDep,
    commands: EmployeeCommandsDep,
    org_unit_queries: OrgUnitQueriesDep,
    user_queries: UserQueriesDep,
    user_commands: UserCommandsDep,
    role_queries: RoleQueriesDep,
    publisher: EventPublisherDep,
) -> EmployeeService:
    return EmployeeService(
        queries,
        commands,
        org_unit_queries,
        user_queries,
        user_commands,
        role_queries,
        publisher,
    )


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
