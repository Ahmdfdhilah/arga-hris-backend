from typing import Optional
from datetime import datetime
from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands
from app.modules.attendances.schemas import AttendanceResponse
from app.core.exceptions import NotFoundException, ValidationException
from app.core.utils.file_upload import generate_signed_url_for_path


class MarkPresentByIdUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        commands: AttendanceCommands,
    ):
        self.queries = queries
        self.commands = commands

    async def execute(
        self,
        attendance_id: int,
        current_user_employee_id: Optional[int],
        updated_by: str,
        admin_name: str,
        notes: Optional[str] = None,
    ) -> AttendanceResponse:
        from datetime import timezone

        attendance = await self.queries.get(attendance_id)

        if not attendance:
            raise NotFoundException(
                f"Attendance dengan ID {attendance_id} tidak ditemukan"
            )

        if attendance.employee_id == current_user_employee_id:
            raise ValidationException(
                "Anda tidak dapat mengubah status attendance Anda sendiri"
            )

        attendance_date = attendance.attendance_date
        now = datetime.now(timezone.utc)

        check_in_datetime = datetime.combine(
            attendance_date,
            datetime.min.time().replace(
                hour=9, minute=0, second=0, microsecond=now.microsecond
            ),
            tzinfo=timezone.utc,
        )
        check_out_datetime = datetime.combine(
            attendance_date,
            datetime.min.time().replace(
                hour=17, minute=0, second=0, microsecond=now.microsecond
            ),
            tzinfo=timezone.utc,
        )

        work_hours = 8.0
        overtime_hours = 0.0

        auto_note = (
            f"Diubah oleh {admin_name} pada {now.strftime('%d-%m-%Y %H:%M:%S')} WIB"
        )
        final_notes = f"{notes}. {auto_note}" if notes else auto_note

        attendance.status = "present"
        attendance.check_in_time = check_in_datetime
        attendance.check_out_time = check_out_datetime
        attendance.work_hours = work_hours
        attendance.overtime_hours = overtime_hours
        attendance.check_in_notes = final_notes
        attendance.check_out_notes = final_notes
        attendance.updated_by = updated_by

        updated_attendance = await self.commands.update(attendance)

        if not updated_attendance:
            raise ValidationException("Gagal update attendance")

        check_in_url = (
            generate_signed_url_for_path(updated_attendance.check_in_selfie_path)
            if updated_attendance.check_in_selfie_path
            else None
        )
        check_out_url = (
            generate_signed_url_for_path(updated_attendance.check_out_selfie_path)
            if updated_attendance.check_out_selfie_path
            else None
        )
        return AttendanceResponse.from_orm_with_urls(
            updated_attendance, check_in_url=check_in_url, check_out_url=check_out_url
        )
