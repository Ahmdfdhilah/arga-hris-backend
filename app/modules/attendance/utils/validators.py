from typing import Optional
from datetime import date
from app.core.exceptions.client_error import ValidationException
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.core.utils.workforce import (
    is_working_day,
    get_working_day_violation_reason,
)


def validate_working_day_and_employee_type(
    check_date: date, employee_type: Optional[str]
) -> None:
    """
    Validate if the employee can check in/out on this specific day based on their type.
    Raises ValidationException if invalid.
    """
    if not is_working_day(check_date, employee_type):
        reason = get_working_day_violation_reason(check_date, employee_type)
        raise ValidationException(reason)


async def validate_not_on_leave(
    leave_queries: LeaveRequestQueries, employee_id: int, check_date: date
) -> None:
    """
    Validate if the employee is currently on leave.
    """
    leave_request = await leave_queries.is_on_leave(employee_id, check_date)
    if leave_request:
        raise ValidationException(
            f"Tidak bisa absen karena Anda sedang cuti ({leave_request.leave_type}) "
            f"dari {leave_request.start_date.strftime('%d-%m-%Y')} "
            f"sampai {leave_request.end_date.strftime('%d-%m-%Y')}."
        )
