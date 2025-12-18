from datetime import date
from fastapi import UploadFile, Request
from app.modules.attendance.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.modules.attendance.schemas import CheckInRequest, AttendanceResponse
from app.core.exceptions.client_error import ValidationException
from app.core.utils.file_upload import upload_file_to_gcp, generate_signed_url_for_path
from app.core.utils.datetime import get_utc_now
from app.config.settings import settings
from app.config.constants import FileUploadConstants
from app.external_clients.rest.nominatim_client import nominatim_client
from app.modules.attendance.utils.validators import (
    validate_working_day_and_employee_type,
    validate_not_on_leave,
)


class CheckInUseCase:
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
        request: CheckInRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> AttendanceResponse:
        if not selfie:
            raise ValidationException("Foto selfie check-in wajib diisi")

        today = date.today()

        employee = await self.employee_queries.get_by_id(employee_id)
        if not employee:
            raise ValidationException("Employee not found")

        employee_type = employee.employee_type
        org_unit_id = employee.org_unit_id

        validate_working_day_and_employee_type(today, employee_type)
        await validate_not_on_leave(self.leave_queries, employee_id, today)

        existing = await self.queries.get_by_employee_and_date(employee_id, today)
        if existing and existing.check_in_time:
            raise ValidationException(
                f"Anda sudah check-in hari ini pada {existing.check_in_time.strftime('%H:%M:%S')}"
            )

        now = get_utc_now()
        client_ip = request_obj.client.host if request_obj.client else None

        _, selfie_path = await upload_file_to_gcp(
            file=selfie,
            entity_type="attendances",
            entity_id=employee_id,
            subfolder=f"check_in/{today.strftime('%Y-%m-%d')}",
            allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES,
            max_size=settings.MAX_IMAGE_SIZE,
        )

        location_name = None
        if request.latitude is not None and request.longitude is not None:
            location_name = await nominatim_client.reverse_geocode(
                latitude=request.latitude, longitude=request.longitude
            )

        if existing:
            update_data = {
                "check_in_time": now,
                "check_in_submitted_at": now,
                "check_in_submitted_ip": client_ip,
                "check_in_notes": request.notes,
                "check_in_selfie_path": selfie_path,
                "check_in_latitude": request.latitude,
                "check_in_longitude": request.longitude,
                "check_in_location_name": location_name,
                "status": "present",
                "org_unit_id": org_unit_id,
            }
            attendance = await self.commands.update(existing.id, update_data)
        else:
            attendance_data = {
                "employee_id": employee_id,
                "org_unit_id": org_unit_id,
                "attendance_date": today,
                "status": "present",
                "check_in_time": now,
                "check_in_submitted_at": now,
                "check_in_submitted_ip": client_ip,
                "check_in_notes": request.notes,
                "check_in_selfie_path": selfie_path,
                "check_in_latitude": request.latitude,
                "check_in_longitude": request.longitude,
                "check_in_location_name": location_name,
                "created_by": employee_id,
            }
            attendance = await self.commands.create(attendance_data)

        if not attendance:
            raise ValidationException("Gagal membuat atau update data attendance")

        check_in_url = (
            generate_signed_url_for_path(attendance.check_in_selfie_path)
            if attendance.check_in_selfie_path
            else None
        )
        return AttendanceResponse.from_orm_with_urls(
            attendance, check_in_url=check_in_url, check_out_url=None
        )
