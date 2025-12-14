"""
WorkSubmission Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.work_submissions.repositories import WorkSubmissionQueries, WorkSubmissionCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.work_submissions.services.work_submission_service import WorkSubmissionService


def get_work_submission_queries(db: PostgresDB) -> WorkSubmissionQueries:
    return WorkSubmissionQueries(db)


WorkSubmissionQueriesDep = Annotated[WorkSubmissionQueries, Depends(get_work_submission_queries)]


def get_work_submission_commands(db: PostgresDB) -> WorkSubmissionCommands:
    return WorkSubmissionCommands(db)


WorkSubmissionCommandsDep = Annotated[WorkSubmissionCommands, Depends(get_work_submission_commands)]


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_work_submission_service(
    queries: WorkSubmissionQueriesDep,
    commands: WorkSubmissionCommandsDep,
    employee_queries: EmployeeQueriesDep,
) -> WorkSubmissionService:
    return WorkSubmissionService(queries, commands, employee_queries)


WorkSubmissionServiceDep = Annotated[WorkSubmissionService, Depends(get_work_submission_service)]
