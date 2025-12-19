from typing import Tuple
from datetime import datetime


def calculate_work_hours_and_overtime(
    check_in_time: datetime, check_out_time: datetime
) -> Tuple[float, float]:
    """
    Calculate work hours and overtime based on check-in and check-out times.
    Standard cutoff time is 18:00.
    """
    cutoff_time = check_out_time.replace(hour=18, minute=0, second=0, microsecond=0)

    if check_out_time <= cutoff_time:
        time_diff = check_out_time - check_in_time
        work_hours = time_diff.total_seconds() / 3600
        overtime_hours = 0.0
    else:
        work_time_diff = cutoff_time - check_in_time
        overtime_time_diff = check_out_time - cutoff_time

        work_hours = work_time_diff.total_seconds() / 3600
        overtime_hours = overtime_time_diff.total_seconds() / 3600

    return round(work_hours, 2), round(overtime_hours, 2)
