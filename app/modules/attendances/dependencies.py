"""
Attendance Module Dependencies
"""

from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.employees.repositories import EmployeeQueries
from app.modules.holiday_calendar.repositories import HolidayQueries
from app.modules.attendances.services.attendances_service import AttendanceService


def get_attendance_queries(db: PostgresDB) -> AttendanceQueries:
    return AttendanceQueries(db)


AttendanceQueriesDep = Annotated[AttendanceQueries, Depends(get_attendance_queries)]


def get_attendance_commands(db: PostgresDB) -> AttendanceCommands:
    return AttendanceCommands(db)


AttendanceCommandsDep = Annotated[AttendanceCommands, Depends(get_attendance_commands)]


def get_leave_request_queries(db: PostgresDB) -> LeaveRequestQueries:
    return LeaveRequestQueries(db)


LeaveRequestQueriesDep = Annotated[LeaveRequestQueries, Depends(get_leave_request_queries)]


def get_employee_queries(db: PostgresDB) -> EmployeeQueries:
    return EmployeeQueries(db)


EmployeeQueriesDep = Annotated[EmployeeQueries, Depends(get_employee_queries)]


def get_holiday_queries(db: PostgresDB) -> HolidayQueries:
    return HolidayQueries(db)


HolidayQueriesDep = Annotated[HolidayQueries, Depends(get_holiday_queries)]


def get_attendance_service(
    queries: AttendanceQueriesDep,
    commands: AttendanceCommandsDep,
    employee_queries: EmployeeQueriesDep,
    leave_queries: LeaveRequestQueriesDep,
    holiday_queries: HolidayQueriesDep,
) -> AttendanceService:
    return AttendanceService(queries, commands, employee_queries, leave_queries, holiday_queries)


AttendanceServiceDep = Annotated[AttendanceService, Depends(get_attendance_service)]

