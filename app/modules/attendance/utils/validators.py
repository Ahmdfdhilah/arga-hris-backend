from typing import Optional
from datetime import date
from app.core.exceptions.client_error import ValidationException
from app.modules.leave_requests.repositories import LeaveRequestQueries


def is_working_day(check_date: date, employee_type: Optional[str]) -> bool:
    """Check if the given date is a working day for the employee type."""
    if check_date.weekday() == 6:  # Sunday
        return employee_type == "on_site"
    return True


def get_working_day_violation_reason(
    check_date: date, employee_type: Optional[str]
) -> str:
    """Get the reason why it's not a working day."""
    if check_date.weekday() == 6:
        if employee_type != "on_site":
            return (
                "Tidak bisa absen pada hari Minggu. "
                "Hanya karyawan dengan tipe 'on_site' yang dapat absen di hari Minggu. "
                "Hari kerja untuk tipe lainnya adalah Senin-Sabtu."
            )
    return "Hari ini adalah hari libur."


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
