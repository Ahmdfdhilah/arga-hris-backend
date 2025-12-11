"""
Job untuk auto-create attendance records setiap hari untuk semua karyawan aktif.

Business Logic:
- Berjalan setiap hari jam 00:30 WIB (setelah tengah malam)
- Membuat row attendance dengan status berdasarkan employee type:
  * Hybrid employee: status "hybrid" (akan berubah ke "present" jika check in/out complete)
  * Non-hybrid employee: status "absent" (akan berubah ke "present" jika check in)
  * On_site employee: kerja 7 hari seminggu (termasuk Minggu), status default "absent"
- Untuk hari Minggu: hanya on_site employee yang akan dibuatkan attendance record
- Untuk hari Senin-Sabtu: semua employee type akan dibuatkan attendance record
- Jika karyawan clock in, status akan diupdate menjadi "present"
- Hybrid employee yang tidak check in/out tetap dengan status "hybrid"
- Non-hybrid employee yang tidak check in tetap dengan status "absent"
"""

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from app.modules.attendance.models.attendance import Attendance
from app.modules.attendance.repositories.attendance_repository import (
    AttendanceRepository,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient

logger = logging.getLogger(__name__)


class AutoCreateDailyAttendanceJob(BaseScheduledJob):
    """
    Job untuk membuat attendance records otomatis setiap hari.

    Attendance dibuat dengan status "absent", akan berubah menjadi "present"
    ketika karyawan melakukan clock in.
    """

    job_id = "auto_create_daily_attendance"
    description = (
        "Auto-create attendance records untuk semua karyawan aktif setiap hari"
    )
    cron = "0 23 * * *"  # Setiap hari jam 23:00 WIB
    enabled = True
    max_retries = 3

    async def execute(self) -> Dict[str, Any]:
        """
        Execute job: create attendance untuk semua karyawan aktif.

        Untuk hari Minggu: hanya create attendance untuk employee type 'on_site'
        Untuk hari Senin-Sabtu: create attendance untuk semua employee type

        Returns:
            Dict dengan hasil eksekusi
        """
        today = date.today()
        is_sunday = today.weekday() == 6

        created_count = 0
        skipped_count = 0
        error_count = 0

        if is_sunday:
            logger.info(f"Memulai auto-create attendance untuk tanggal: {today} (hari Minggu - hanya on_site)")
        else:
            logger.info(f"Memulai auto-create attendance untuk tanggal: {today}")

        try:
            # Get database session
            async with get_db_context() as db:
                attendance_repo = AttendanceRepository(db)

                # Get semua karyawan aktif dari Workforce Service via gRPC
                employee_client = EmployeeGRPCClient()

                try:
                    # List all active employees dengan pagination (loop semua pages)
                    all_employees = []
                    page = 1
                    limit = 200  # Max items per page

                    while True:
                        employees_response = await employee_client.list_employees(
                            page=page, limit=limit, is_active=True
                        )

                        all_employees.extend(employees_response.get("employees", []))

                        # Check if there are more pages
                        pagination = employees_response.get("pagination", {})
                        total_pages = pagination.get("total_pages", 1)

                        logger.info(
                            f"Fetched page {page}/{total_pages}, "
                            f"total employees so far: {len(all_employees)}"
                        )

                        if page >= total_pages:
                            break

                        page += 1

                    employees = all_employees
                    total_employees = len(employees)

                    logger.info(f"Ditemukan total {total_employees} karyawan aktif")

                    # Iterate employees dan create attendance
                    for employee in employees:
                        employee_id = employee.get("id")
                        org_unit_id = employee.get("org_unit_id")
                        employee_type = employee.get("employee_type")

                        if not employee_id:
                            error_count += 1
                            continue

                        try:
                            # Jika hari Minggu, skip employee yang bukan on_site
                            if is_sunday and employee_type != "on_site":
                                logger.debug(
                                    f"Skip employee_id={employee_id} (type={employee_type}) "
                                    f"karena hari Minggu dan bukan on_site"
                                )
                                skipped_count += 1
                                continue

                            elif org_unit_id == 20:
                                logger.debug(
                                    f"Skip employee_id={employee_id} (type={employee_type}) "
                                    f"karena direktorat"
                                )
                                skipped_count += 1
                                continue

                            # Cek apakah attendance sudah ada untuk employee & date ini
                            existing = await attendance_repo.get_by_employee_and_date(
                                employee_id=employee_id, attendance_date=today
                            )

                            if existing:
                                logger.debug(
                                    f"Attendance untuk employee_id={employee_id} "
                                    f"tanggal {today} sudah ada, skip"
                                )
                                skipped_count += 1
                                continue

                            # Tentukan status berdasarkan employee_type
                            # Hybrid employee: status "hybrid"
                            # On_site dan employee lainnya: status "absent"
                            if employee_type and employee_type.lower() == "hybrid":
                                attendance_status = "hybrid"
                            else:
                                attendance_status = "absent"

                            # Create attendance baru dengan status sesuai employee type
                            attendance_data = {
                                "employee_id": employee_id,
                                "org_unit_id": org_unit_id,
                                "attendance_date": today,
                                "status": attendance_status,
                            }

                            await attendance_repo.create(attendance_data)
                            created_count += 1

                            logger.debug(
                                f"Attendance created untuk employee_id={employee_id}, "
                                f"org_unit_id={org_unit_id}, status={attendance_status}"
                            )

                        except Exception as e:
                            logger.error(
                                f"Error create attendance untuk employee_id={employee_id}: {e}"
                            )
                            error_count += 1

                    # Summary
                    message = (
                        f"Auto-create attendance selesai. "
                        f"Total: {total_employees} karyawan, "
                        f"Created: {created_count}, "
                        f"Skipped: {skipped_count}, "
                        f"Errors: {error_count}"
                    )

                    logger.info(message)

                    return {
                        "success": True,
                        "message": message,
                        "data": {
                            "date": today.isoformat(),
                            "total_employees": total_employees,
                            "created": created_count,
                            "skipped": skipped_count,
                            "errors": error_count,
                        },
                    }

                finally:
                    await employee_client.close()

        except Exception as e:
            error_message = f"Error saat execute auto-create attendance: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)
