from typing import Tuple
from datetime import date
from fastapi import UploadFile, Request
from app.modules.attendance.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.attendance.schemas import CheckOutRequest, AttendanceResponse
from app.core.exceptions.client_error import ValidationException, NotFoundException
from app.core.utils.file_upload import upload_file_to_gcp, generate_signed_url_for_path
from app.core.utils.datetime import get_utc_now
from app.config.settings import settings
from app.config.constants import FileUploadConstants
from app.external_clients.rest.nominatim_client import nominatim_client
from app.modules.attendance.utils.validators import (
    validate_working_day_and_employee_type,
    validate_not_on_leave,
)
from app.modules.attendance.utils.calculators import calculate_work_hours_and_overtime


class CheckOutUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        commands: AttendanceCommands,
        employee_queries: EmployeeQueries,
        leave_queries: LeaveRequestQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries
        self.leave_queries = leave_queries

    async def execute(
        self,
        employee_id: int,
        request: CheckOutRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> Tuple[AttendanceResponse, str]:
        if not selfie:
            raise ValidationException("Foto selfie check-out wajib diisi")

        today = date.today()

        employee = await self.employee_queries.get_by_id(employee_id)
        if not employee:
            raise ValidationException("Employee not found")

        employee_type = employee.employee_type

        validate_working_day_and_employee_type(today, employee_type)
        await validate_not_on_leave(self.leave_queries, employee_id, today)

        existing = await self.queries.get_by_employee_and_date(employee_id, today)
        if not existing or not existing.check_in_time:
            raise NotFoundException("Anda belum check-in hari ini")

        if existing.check_out_time:
            raise ValidationException(
                f"Anda sudah check-out hari ini pada {existing.check_out_time.strftime('%H:%M:%S')}"
            )

        now = get_utc_now()
        client_ip = request_obj.client.host if request_obj.client else None

        _, selfie_path = await upload_file_to_gcp(
            file=selfie,
            entity_type="attendances",
            entity_id=employee_id,
            subfolder=f"check_out/{today.strftime('%Y-%m-%d')}",
            allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES,
            max_size=settings.MAX_IMAGE_SIZE,
        )

        location_name = None
        if request.latitude is not None and request.longitude is not None:
            location_name = await nominatim_client.reverse_geocode(
                latitude=request.latitude, longitude=request.longitude
            )

        work_hours, overtime_hours = calculate_work_hours_and_overtime(
            existing.check_in_time, now
        )

        update_data = {
            "check_out_time": now,
            "check_out_submitted_at": now,
            "check_out_submitted_ip": client_ip,
            "check_out_notes": request.notes,
            "check_out_selfie_path": selfie_path,
            "check_out_latitude": request.latitude,
            "check_out_longitude": request.longitude,
            "check_out_location_name": location_name,
            "work_hours": work_hours,
            "overtime_hours": overtime_hours,
        }
        attendance = await self.commands.update(existing.id, update_data)

        if not attendance:
            raise ValidationException("Gagal update data attendance untuk check-out")

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

        message = f"Check-out berhasil. Total jam kerja: {work_hours} jam"
        if overtime_hours > 0:
            message += f", overtime: {overtime_hours} jam"

        return response, message
