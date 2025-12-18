from typing import Tuple
from datetime import date, timedelta
from app.core.exceptions.client_error import BadRequestException
from app.config.constants import AttendanceConstants


def get_date_range_from_type(type: str) -> Tuple[date, date]:
    """
    Get start and end date based on type (today/weekly/monthly).
    """
    today = date.today()
    if type == "today":
        return (today, today)
    elif type == "weekly":
        start_of_week = today - timedelta(days=today.weekday())
        return (start_of_week, today)
    elif type == "monthly":
        start_of_month = today.replace(day=1)
        return (start_of_month, today)
    else:
        raise BadRequestException(
            f"Tipe tidak valid. Harus salah satu dari: {', '.join(AttendanceConstants.VALID_TYPES)}"
        )
