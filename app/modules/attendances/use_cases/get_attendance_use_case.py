from app.modules.attendances.repositories import AttendanceQueries
from app.modules.attendances.schemas import AttendanceResponse
from app.core.exceptions.client_error import NotFoundException
from app.core.utils.file_upload import generate_signed_url_for_path


class GetAttendanceUseCase:
    def __init__(self, queries: AttendanceQueries):
        self.queries = queries

    async def execute(self, attendance_id: int) -> AttendanceResponse:
        attendance = await self.queries.get(
            attendance_id
        ) 

        if not attendance:
            raise NotFoundException(
                f"Attendance dengan ID {attendance_id} tidak ditemukan"
            )

        check_in_url = (
            generate_signed_url_for_path(attendance.check_in_selfie_path)
            if attendance.check_in_selfie_path
            else None
        )
        check_out_url = (
            generate_signed_url_for_path(attendance.check_out_selfie_path)
            if attendance.check_out_selfie_path
            else None
        )
        response = AttendanceResponse.from_orm_with_urls(
            attendance, check_in_url=check_in_url, check_out_url=check_out_url
        )
        return response
