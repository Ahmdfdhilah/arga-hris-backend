from typing import Optional, List
from datetime import date, timedelta


def is_working_day(check_date: date, employee_type: Optional[str]) -> bool:
    """
    Check if the given date is a working day for the employee type.

    Business Rules:
    - Employee type 'on_site': Works 7 days (Mon-Sun)
    - Other employee types: Work 6 days (Mon-Sat), Sunday is off
    """
    if check_date.weekday() == 6:  # Sunday
        return employee_type == "on_site"
    return True


def calculate_working_days(
    start_date: date, end_date: date, employee_type: Optional[str] = None
) -> int:
    """
    Calculate number of working days between two dates based on employee type.
    """
    if start_date > end_date:
        return 0

    delta = end_date - start_date
    working_days = 0

    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        if is_working_day(day, employee_type):
            working_days += 1

    return working_days


def generate_working_days_list(
    start_date: date, end_date: date, employee_type: Optional[str]
) -> List[date]:
    """
    Generate list of working days in a date range based on employee type.
    """
    working_days = []
    current_date = start_date

    while current_date <= end_date:
        if is_working_day(current_date, employee_type):
            working_days.append(current_date)
        current_date += timedelta(days=1)

    return working_days


def get_working_day_violation_reason(
    check_date: date, employee_type: Optional[str]
) -> str:
    """Get the reason why it's not a working day."""
    if check_date.weekday() == 6:
        if employee_type != "on_site":
            return (
                "Tidak bisa absen pada hari Minggu. "
                "Hanya karyawan dengan tipe 'On Site' yang dapat absen di hari Minggu. "
                "Hari kerja untuk tipe lainnya adalah Senin-Sabtu."
            )
    return "Hari ini adalah hari libur."
