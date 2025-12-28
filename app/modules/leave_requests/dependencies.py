"""
LeaveRequest Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.employee_assignments.repositories import (
    AssignmentCommands,
    AssignmentQueries,
)
from app.modules.leave_requests.services.leave_request_service import (
    LeaveRequestService,
)


def get_leave_request_queries(db: PostgresDB) -> LeaveRequestQueries:
    return LeaveRequestQueries(db)


LeaveRequestQueriesDep = Annotated[
    LeaveRequestQueries, Depends(get_leave_request_queries)
]


def get_leave_request_commands(db: PostgresDB) -> LeaveRequestCommands:
    return LeaveRequestCommands(db)


LeaveRequestCommandsDep = Annotated[
    LeaveRequestCommands, Depends(get_leave_request_commands)
]


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_assignment_commands(db: PostgresDB) -> AssignmentCommands:
    return AssignmentCommands(db)


AssignmentCommandsDep = Annotated[AssignmentCommands, Depends(get_assignment_commands)]


def get_assignment_queries(db: PostgresDB) -> AssignmentQueries:
    return AssignmentQueries(db)


AssignmentQueriesDep = Annotated[AssignmentQueries, Depends(get_assignment_queries)]


def get_leave_request_service(
    queries: LeaveRequestQueriesDep,
    commands: LeaveRequestCommandsDep,
    employee_queries: EmployeeQueriesDep,
    assignment_commands: AssignmentCommandsDep,
    assignment_queries: AssignmentQueriesDep,
) -> LeaveRequestService:
    return LeaveRequestService(
        queries, commands, employee_queries, assignment_commands, assignment_queries
    )


LeaveRequestServiceDep = Annotated[
    LeaveRequestService, Depends(get_leave_request_service)
]
