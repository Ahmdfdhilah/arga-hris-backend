"""
Job untuk auto-create attendance records setiap hari untuk semua karyawan aktif.

Business Logic:
- Berjalan setiap hari jam 00:30 WIB (setelah tengah malam)
- Skip jika tanggal adalah hari libur nasional (dari holiday_calendar)
- Membuat row attendance dengan status berdasarkan employee type:
  * Hybrid employee: status "hybrid" (akan berubah ke "present" jika check in/out complete)
  * Non-hybrid employee: status "absent" (akan berubah ke "present" jika check in)
  * On_site employee: kerja 7 hari seminggu (termasuk Minggu), status default "absent"
- Untuk hari Minggu: hanya on_site employee yang akan dibuatkan attendance record
- Untuk hari Senin-Sabtu: semua employee type akan dibuatkan attendance record
- Employee dengan org_unit.type = "Direktorat" akan di-skip (tidak dibuatkan attendance)
- Jika karyawan clock in, status akan diupdate menjadi "present"
- Hybrid employee yang tidak check in/out tetap dengan status "hybrid"
- Non-hybrid employee yang tidak check in tetap dengan status "absent"
"""

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.holiday_calendar.repositories import HolidayQueries
from app.core.enums.org_unit import OrgUnitType

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

        - Skip jika tanggal adalah hari libur nasional
        - Untuk hari Minggu: hanya create attendance untuk employee type 'on_site'
        - Untuk hari Senin-Sabtu: create attendance untuk semua employee type
        - Skip employee dengan org_unit.type = "Direktorat"

        Returns:
            Dict dengan hasil eksekusi
        """
        today = date.today()
        is_sunday = today.weekday() == 6

        created_count = 0
        skipped_count = 0
        error_count = 0

        logger.info(f"Memulai auto-create attendance untuk tanggal: {today}")

        try:
            # Get database session
            async with get_db_context() as db:
                holiday_queries = HolidayQueries(db)
                is_holiday = await holiday_queries.is_holiday(today)
                
                if is_holiday:
                    holiday = await holiday_queries.get_by_date(today)
                    holiday_name = holiday.name if holiday else "Hari Libur"
                    message = f"Skip auto-create attendance: {today} adalah {holiday_name}"
                    logger.info(message)
                    return {
                        "success": True,
                        "message": message,
                        "data": {
                            "date": today.isoformat(),
                            "is_holiday": True,
                            "holiday_name": holiday_name,
                            "total_employees": 0,
                            "created": 0,
                            "skipped": 0,
                            "errors": 0,
                        },
                    }

                attendance_queries = AttendanceQueries(db)
                attendance_commands = AttendanceCommands(db)
                employee_queries = EmployeeQueries(db)
                
                # Import and initialize leave request queries for checking leave
                from app.modules.leave_requests.repositories import LeaveRequestQueries
                leave_request_queries = LeaveRequestQueries(db)

                # Get semua karyawan aktif dari local repository
                all_employees = []
                page = 1
                limit = 200  # Max items per page

                while True:
                    skip = (page - 1) * limit
                    employees_list, total = await employee_queries.list(
                        is_active=True,
                        skip=skip,
                        limit=limit,
                    )
                    
                    if not employees_list:
                        break

                    for emp in employees_list:
                        # Ambil org_unit.type untuk pengecekan direktorat
                        org_unit_type = emp.org_unit.type if emp.org_unit else None
                        all_employees.append(
                            {
                                "id": emp.id,
                                "org_unit_id": emp.org_unit_id,
                                "employee_type": emp.type,
                                "org_unit_type": org_unit_type,
                            }
                        )

                    logger.info(
                        f"Fetched page {page}, "
                        f"total employees so far: {len(all_employees)}"
                    )

                    if len(employees_list) < limit:
                        break

                    page += 1

                employees = all_employees
                total_employees = total

                if is_sunday:
                    logger.info(
                        f"Ditemukan total {total_employees} karyawan aktif (hari Minggu - hanya on_site)"
                    )
                else:
                    logger.info(f"Ditemukan total {total_employees} karyawan aktif")

                # Iterate employees dan create attendance
                for employee in employees:
                    employee_id = employee.get("id")
                    org_unit_id = employee.get("org_unit_id")
                    employee_type = employee.get("employee_type")
                    org_unit_type = employee.get("org_unit_type")

                    if not employee_id:
                        error_count += 1
                        continue

                    try:
                        if org_unit_type == OrgUnitType.DIREKTORAT.value:
                            logger.debug(
                                f"Skip employee_id={employee_id} "
                                f"karena org_unit.type=Direktorat"
                            )
                            skipped_count += 1
                            continue

                        # Jika hari Minggu, skip employee yang bukan on_site
                        if is_sunday and employee_type != "on_site":
                            logger.debug(
                                f"Skip employee_id={employee_id} (type={employee_type}) "
                                f"karena hari Minggu dan bukan on_site"
                            )
                            skipped_count += 1
                            continue

                        # Cek apakah attendance sudah ada untuk employee & date ini
                        existing = await attendance_queries.get_by_employee_and_date(
                            employee_id=employee_id, attendance_date=today
                        )

                        if existing:
                            logger.debug(
                                f"Attendance untuk employee_id={employee_id} "
                                f"tanggal {today} sudah ada, skip"
                            )
                            skipped_count += 1
                            continue

                        # Tentukan status berdasarkan employee_type atau leave
                        # Cek apakah employee memiliki cuti pada hari ini
                        leave_request = await leave_request_queries.is_on_leave(
                            employee_id=employee_id,
                            check_date=today,
                        )
                        
                        if leave_request:
                            attendance_status = "leave"
                            logger.debug(
                                f"Employee_id={employee_id} has leave request, "
                                f"setting status='leave'"
                            )
                        elif employee_type and employee_type.lower() == "hybrid":
                            attendance_status = "hybrid"
                        else:
                            attendance_status = "absent"

                        # Create attendance baru dengan status sesuai
                        from app.modules.attendances.models.attendances import Attendance
                        
                        attendance = Attendance(
                            employee_id=employee_id,
                            org_unit_id=org_unit_id,
                            attendance_date=today,
                            status=attendance_status,
                        )

                        await attendance_commands.create(attendance)
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
                        "is_holiday": False,
                        "total_employees": total_employees,
                        "created": created_count,
                        "skipped": skipped_count,
                        "errors": error_count,
                    },
                }

        except Exception as e:
            error_message = f"Error saat execute auto-create attendance: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)

