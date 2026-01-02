"""
Job untuk mark attendance status menjadi 'invalid' jika tidak checkout.

Business Logic:
- Berjalan setiap hari jam 23:59 WIB (sebelum hari berganti)
- Skip jika tanggal adalah hari libur nasional (dari holiday_calendar)
- Cek semua attendance yang memiliki check_in_time tapi tidak ada check_out_time
- Skip employee dengan org_unit.type = "Direktorat"
- Update status menjadi "invalid" untuk attendance tersebut
- Hanya memproses attendance untuk hari ini
"""

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from app.modules.attendances.models.attendances import Attendance
from app.modules.employees.models.employee import Employee
from app.modules.holiday_calendar.repositories import HolidayQueries
from app.core.enums.org_unit import OrgUnitType

logger = logging.getLogger(__name__)


class MarkInvalidNoCheckoutJob(BaseScheduledJob):
    """
    Job untuk mark attendance status menjadi 'invalid' jika check-in tapi tidak checkout.

    Attendance dengan check_in_time tapi tidak ada check_out_time akan diubah statusnya
    menjadi 'invalid' pada akhir hari kerja.
    Employee dengan org_unit.type = "Direktorat" akan di-skip.
    """

    job_id = "mark_invalid_no_checkout"
    description = (
        "Mark attendance status menjadi 'invalid' jika check-in tapi tidak checkout"
    )
    cron = "30 23 * * *"  # Setiap hari jam 23:30 WIB
    enabled = True
    max_retries = 3

    async def execute(self) -> Dict[str, Any]:
        """
        Execute job: mark invalid untuk attendance yang tidak checkout.

        - Skip jika tanggal adalah hari libur nasional
        - Skip employee dengan org_unit.type = "Direktorat"

        Returns:
            Dict dengan hasil eksekusi
        """
        today = date.today()

        updated_count = 0
        skipped_count = 0
        error_count = 0

        logger.info(
            f"Memulai mark invalid no checkout untuk attendance tanggal: {today}"
        )

        try:
            async with get_db_context() as db:
                # Cek apakah hari ini adalah hari libur
                holiday_queries = HolidayQueries(db)
                is_holiday = await holiday_queries.is_holiday(today)
                
                if is_holiday:
                    holiday = await holiday_queries.get_by_date(today)
                    holiday_name = holiday.name if holiday else "Hari Libur"
                    message = f"Skip mark invalid: {today} adalah {holiday_name}"
                    logger.info(message)
                    return {
                        "success": True,
                        "message": message,
                        "data": {
                            "date": today.isoformat(),
                            "is_holiday": True,
                            "holiday_name": holiday_name,
                            "total_found": 0,
                            "updated": 0,
                            "skipped": 0,
                            "errors": 0,
                        },
                    }

                query = (
                    select(Attendance)
                    .options(
                        joinedload(Attendance.employee).joinedload(Employee.org_unit)
                    )
                    .where(
                        and_(
                            Attendance.attendance_date == today,
                            Attendance.check_in_time.isnot(None),
                            Attendance.check_out_time.is_(None),
                            Attendance.status.notin_(["invalid", "leave"])
                        )
                    )
                )

                result = await db.execute(query)
                attendances = result.scalars().unique().all()

                total_found = len(attendances)
                logger.info(
                    f"Ditemukan {total_found} attendance dengan check-in tapi tanpa check-out"
                )

                for attendance in attendances:
                    try:
                        # Skip jika employee org_unit.type = Direktorat
                        if (
                            attendance.employee 
                            and attendance.employee.org_unit 
                            and attendance.employee.org_unit.type == OrgUnitType.DIREKTORAT.value
                        ):
                            logger.debug(
                                f"Skip attendance ID {attendance.id} (employee_id={attendance.employee_id}) "
                                f"karena org_unit.type=Direktorat"
                            )
                            skipped_count += 1
                            continue

                        # Update status menjadi 'invalid'
                        attendance.status = "invalid"

                        await db.flush()
                        updated_count += 1

                        logger.debug(
                            f"Attendance ID {attendance.id} (employee_id={attendance.employee_id}) "
                            f"di-mark invalid karena tidak checkout"
                        )

                    except Exception as e:
                        logger.error(
                            f"Error update attendance ID {attendance.id}: {e}"
                        )
                        error_count += 1

                # Commit semua changes
                await db.commit()

                message = (
                    f"Mark invalid no checkout selesai. "
                    f"Total ditemukan: {total_found}, "
                    f"Updated: {updated_count}, "
                    f"Skipped: {skipped_count}, "
                    f"Errors: {error_count}"
                )

                logger.info(message)

                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "date": today.isoformat(),
                        "is_holiday": False,
                        "total_found": total_found,
                        "updated": updated_count,
                        "skipped": skipped_count,
                        "errors": error_count,
                    },
                }

        except Exception as e:
            error_message = f"Error saat execute mark invalid no checkout: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)

