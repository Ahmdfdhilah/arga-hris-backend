"""
Utility functions untuk leave request operations.
"""
from typing import  Optional
from datetime import date, timedelta
from app.modules.leave_requests.repositories import LeaveRequestRepository

def calculate_working_days(
    start_date: date, end_date: date, employee_type: Optional[str] = None
) -> int:
    """
    Calculate working days based on employee type.

    Business Rules:
    - Employee type 'on_site': Kerja 7 hari (Senin-Minggu), Sunday included
    - Employee type lainnya (hybrid, ho, dll): Kerja 6 hari (Senin-Sabtu), Sunday excluded

    Args:
        start_date: Start date
        end_date: End date
        employee_type: Tipe employee ('on_site', 'hybrid', 'ho', dll)

    Returns:
        Number of working days based on employee type
    """
    if start_date > end_date:
        return 0

    delta = end_date - start_date
    working_days = 0

    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        is_sunday = day.weekday() == 6  # Sunday = 6

        # On_site employee: include all days (including Sunday)
        # Other employee types: exclude Sunday
        if employee_type == "on_site":
            working_days += 1
        elif not is_sunday:  # Non on_site: exclude Sunday
            working_days += 1

    return working_days



async def validate_no_overlapping_leave(
    leave_request_repo: LeaveRequestRepository,
    employee_id: int,
    start_date: date,
    end_date: date,
    exclude_leave_request_id: Optional[int] = None,
) -> None:
    """
    Validasi bahwa tidak ada leave request yang overlap untuk employee.

    Args:
        leave_request_repo: Repository untuk leave request
        employee_id: ID employee yang akan dicek
        start_date: Tanggal mulai cuti yang akan dicek
        end_date: Tanggal akhir cuti yang akan dicek
        exclude_leave_request_id: ID leave request yang akan di-exclude dari pengecekan (untuk update)

    Raises:
        ConflictException: Jika ada leave request yang overlap (HTTP 409)
    """
    from app.core.exceptions import ConflictException

    overlapping = await leave_request_repo.check_overlapping_leave(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        exclude_id=exclude_leave_request_id,
    )

    if overlapping:
        raise ConflictException(
            f"Employee sudah memiliki cuti yang terdaftar pada periode "
            f"{overlapping.start_date.strftime('%d-%m-%Y')} sampai "
            f"{overlapping.end_date.strftime('%d-%m-%Y')}. "
            f"Tidak dapat membuat atau mengubah cuti yang overlap dengan periode tersebut."
        )


def validate_leave_dates(start_date: date, end_date: date) -> None:
    """
    Validasi bahwa tanggal cuti valid.

    Args:
        start_date: Tanggal mulai cuti
        end_date: Tanggal akhir cuti

    Raises:
        BadRequestException: Jika validasi tanggal gagal (HTTP 400)
    """
    from app.core.exceptions import BadRequestException

    if start_date > end_date:
        raise BadRequestException(
            "Tanggal mulai cuti tidak boleh lebih besar dari tanggal akhir cuti"
        )
