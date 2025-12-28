"""
Employee Assignments Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.employee_assignments.services.assignment_service import (
    AssignmentService,
)


def get_assignment_queries(db: PostgresDB) -> AssignmentQueries:
    return AssignmentQueries(db)


AssignmentQueriesDep = Annotated[AssignmentQueries, Depends(get_assignment_queries)]


def get_assignment_commands(db: PostgresDB) -> AssignmentCommands:
    return AssignmentCommands(db)


AssignmentCommandsDep = Annotated[AssignmentCommands, Depends(get_assignment_commands)]


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_org_unit_queries(db: PostgresDB) -> OrgUnitQueries:
    return OrgUnitQueries(db)


OrgUnitQueriesDep = Annotated[OrgUnitQueries, Depends(get_org_unit_queries)]


def get_leave_request_queries(db: PostgresDB) -> LeaveRequestQueries:
    return LeaveRequestQueries(db)


LeaveRequestQueriesDep = Annotated[
    LeaveRequestQueries, Depends(get_leave_request_queries)
]


def get_assignment_service(
    queries: AssignmentQueriesDep,
    commands: AssignmentCommandsDep,
    employee_queries: EmployeeQueriesDep,
    org_unit_queries: OrgUnitQueriesDep,
    leave_request_queries: LeaveRequestQueriesDep,
) -> AssignmentService:
    return AssignmentService(
        queries, commands, employee_queries, org_unit_queries, leave_request_queries
    )


AssignmentServiceDep = Annotated[AssignmentService, Depends(get_assignment_service)]
