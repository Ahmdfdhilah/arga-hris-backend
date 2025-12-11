"""
Job untuk mark attendance status menjadi 'invalid' jika tidak checkout.

Business Logic:
- Berjalan setiap hari jam 23:59 WIB (sebelum hari berganti)
- Cek semua attendance yang memiliki check_in_time tapi tidak ada check_out_time
- Update status menjadi "invalid" untuk attendance tersebut
- Hanya memproses attendance untuk hari ini
"""

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from sqlalchemy import select, and_
from app.modules.attendance.models.attendance import Attendance

logger = logging.getLogger(__name__)


class MarkInvalidNoCheckoutJob(BaseScheduledJob):
    """
    Job untuk mark attendance status menjadi 'invalid' jika check-in tapi tidak checkout.

    Attendance dengan check_in_time tapi tidak ada check_out_time akan diubah statusnya
    menjadi 'invalid' pada akhir hari kerja.
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
                # Query attendance yang:
                # 1. Tanggal = hari ini
                # 2. Ada check_in_time
                # 3. Tidak ada check_out_time
                # 4. Status bukan 'invalid', atau 'leave'
                query = select(Attendance).where(
                    and_(
                        Attendance.attendance_date == today,
                        Attendance.check_in_time.isnot(None),
                        Attendance.check_out_time.is_(None),
                        Attendance.status.notin_(["invalid", "leave"])
                    )
                )

                result = await db.execute(query)
                attendances = result.scalars().all()

                total_found = len(attendances)
                logger.info(
                    f"Ditemukan {total_found} attendance dengan check-in tapi tanpa check-out"
                )

                for attendance in attendances:
                    try:
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
                    f"Errors: {error_count}"
                )

                logger.info(message)

                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "date": today.isoformat(),
                        "total_found": total_found,
                        "updated": updated_count,
                        "errors": error_count,
                    },
                }

        except Exception as e:
            error_message = f"Error saat execute mark invalid no checkout: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)
