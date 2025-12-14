from typing import Optional, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi import UploadFile, Request
from app.modules.attendance.repositories import AttendanceQueries, AttendanceCommands
from app.modules.attendance.schemas import (
    CheckInRequest,
    CheckOutRequest,
    BulkMarkPresentRequest,
    AttendanceResponse,
)
from app.modules.attendance.schemas.shared import AttendanceStatus
from app.modules.attendance.schemas.responses import (
    AttendanceRecordInReport,
    EmployeeAttendanceReport,
    EmployeeAttendanceOverview,
    AttendanceListResponse,
    BulkMarkPresentSummary,
    AttendanceStatusCheckResponse,
    LeaveDetailsResponse,
)
from app.modules.leave_requests.repositories import LeaveRequestQueries

from app.modules.employees.repositories import EmployeeQueries
from app.external_clients.rest.nominatim_client import nominatim_client
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    BadRequestException,
)
from app.core.utils.file_upload import upload_file_to_gcp, generate_signed_url_for_path
from app.config.constants import FileUploadConstants
from app.config.settings import settings
from app.config.constants import AttendanceConstants


class AttendanceService:
    """Service untuk operasi attendance management."""

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

    async def _get_employee_dict(self, employee_id: int) -> Optional[dict]:
        """Helper to get employee as dict for backward compat"""
        emp = await self.employee_queries.get_by_id(employee_id)
        if not emp:
            return None
        return {
            "id": emp.id,
            "name": emp.user.name if emp.user else None,
            "employee_number": emp.employee_number,
            "employee_type": emp.employee_type,
            "org_unit_id": emp.org_unit_id,
            "is_active": emp.is_active,
        }

    async def _list_employees_dict(self, org_unit_id: int = None, page: int = 1, limit: int = 100) -> dict:
        """Helper to list employees as dict"""
        from app.modules.employees.repositories import EmployeeFilters, PaginationParams
        params = PaginationParams(page=page, limit=limit)
        filters = EmployeeFilters(org_unit_id=org_unit_id, is_active=True)
        employees, pagination = await self.employee_queries.list(params, filters)
        return {
            "employees": [{"id": e.id, "name": e.user.name if e.user else None, "employee_number": e.employee_number, "employee_type": e.employee_type} for e in employees],
            "pagination": pagination.to_dict()
        }

    async def _get_employees_by_org_unit_dict(self, org_unit_id: int, page: int = 1, limit: int = 100, include_children: bool = False) -> dict:
        """Helper to get employees by org unit as dict"""
        employees = await self.employee_queries.get_by_org_unit_id(org_unit_id, include_children=include_children)
        return {
            "employees": [{"id": e.id, "name": e.user.name if e.user else None, "employee_number": e.employee_number, "employee_type": e.employee_type, "org_unit_id": e.org_unit_id} for e in employees],
            "pagination": {"total_items": len(employees)}
        }

    async def _get_subordinates_dict(self, employee_id: int, page: int = 1, limit: int = 100, recursive: bool = False) -> dict:
        """Helper to get subordinates as dict"""
        subordinates = await self.employee_queries.get_subordinates(employee_id, recursive=recursive)
        return {
            "employees": [{"id": e.id, "name": e.user.name if e.user else None, "employee_number": e.employee_number} for e in subordinates],
            "pagination": {"total_items": len(subordinates), "total_pages": 1}
        }


    def _validate_working_day_and_employee_type(
        self, check_date: date, employee_type: Optional[str]
    ) -> None:
        """
        Validate bahwa tanggal adalah hari kerja dengan mempertimbangkan employee type.

        Rules:
        - Senin-Sabtu: Semua employee type bisa absen
        - Minggu: Hanya employee type 'on_site' yang bisa absen

        Args:
            check_date: Tanggal yang akan dicek
            employee_type: Tipe employee ('on_site', 'hybrid', 'ho')

        Raises:
            ValidationException: Jika tidak memenuhi aturan hari kerja
        """

        if check_date.weekday() == 6:  # Sunday
            # Hari Minggu: hanya on_site yang boleh absen
            if employee_type != "on_site":
                raise ValidationException(
                    "Tidak bisa absen pada hari Minggu. "
                    "Hanya karyawan dengan tipe On Site yang dapat absen di hari Minggu. "
                )

    async def _validate_not_on_leave(self, employee_id: int, check_date: date) -> None:
        """
        Validate bahwa employee tidak sedang cuti pada tanggal tertentu.

        Args:
            employee_id: ID employee
            check_date: Tanggal yang akan dicek

        Raises:
            ValidationException: Jika employee sedang cuti
        """
        leave_request = await self.leave_queries.is_on_leave(
            employee_id, check_date
        )

        if leave_request:
            raise ValidationException(
                f"Tidak bisa absen karena Anda sedang cuti ({leave_request.leave_type}) "
                f"dari {leave_request.start_date.strftime('%d-%m-%Y')} "
                f"sampai {leave_request.end_date.strftime('%d-%m-%Y')}."
            )

    def _get_date_range_from_type(self, type: str) -> Tuple[date, date]:
        """
        Convert type string ke range tanggal.

        Args:
            type: Tipe periode (today/weekly/monthly)

        Returns:
            Tuple (start_date, end_date)

        Raises:
            BadRequestException: Jika type tidak valid
        """
        today = date.today()

        if type == "today":
            return (today, today)
        elif type == "weekly":
            # Senin minggu ini
            start_of_week = today - timedelta(days=today.weekday())
            return (start_of_week, today)
        elif type == "monthly":
            # Tanggal 1 bulan ini
            start_of_month = today.replace(day=1)
            return (start_of_month, today)
        else:
            raise BadRequestException(
                f"Tipe tidak valid. Harus salah satu dari: {', '.join(AttendanceConstants.VALID_TYPES)}"
            )

    async def check_in(
        self,
        employee_id: int,
        request: CheckInRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> AttendanceResponse:
        """
        Check-in attendance untuk employee.

        Args:
            employee_id: ID employee yang check-in
            request: Data check-in request
            request_obj: FastAPI request object untuk mendapatkan IP
            selfie: File selfie check-in (MANDATORY)

        Returns:
            AttendanceResponse dengan data attendance

        Raises:
            ValidationException: Jika sudah check-in hari ini atau selfie tidak ada
        """
        # Validate selfie is mandatory
        if not selfie:
            raise ValidationException("Foto selfie check-in wajib diisi")

        today = date.today()

        # Get employee info untuk ambil org_unit_id dan employee_type
        employee_data = await self._get_employee_dict(employee_id)
        org_unit_id = employee_data.get("org_unit_id")
        employee_type = employee_data.get("employee_type")

        # Validate hari kerja berdasarkan employee type
        self._validate_working_day_and_employee_type(today, employee_type)

        # Validate tidak sedang cuti
        await self._validate_not_on_leave(employee_id, today)

        # Cek apakah sudah ada attendance hari ini
        existing = await self.queries.get_by_employee_and_date(
            employee_id, today
        )

        if existing:
            if existing.check_in_time:
                raise ValidationException(
                    f"Anda sudah check-in hari ini pada {existing.check_in_time.strftime('%H:%M:%S')}"
                )

        from datetime import timezone

        now = datetime.now(timezone.utc)
        client_ip = request_obj.client.host if request_obj.client else None

        # Handle selfie upload to GCP (save path only)
        _, selfie_path = await upload_file_to_gcp(
            file=selfie,
            entity_type="attendances",
            entity_id=employee_id,
            subfolder=f"check_in/{today.strftime('%Y-%m-%d')}",
            allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES,
            max_size=settings.MAX_IMAGE_SIZE,
        )

        # Handle location data and reverse geocoding
        location_name = None
        if request.latitude is not None and request.longitude is not None:
            # Get address from coordinates using Nominatim
            location_name = await nominatim_client.reverse_geocode(
                latitude=request.latitude, longitude=request.longitude
            )

        if existing:
            # Update existing attendance
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
            # Create new attendance
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

        # Generate signed URL for response
        check_in_url = (
            generate_signed_url_for_path(attendance.check_in_selfie_path)
            if attendance.check_in_selfie_path
            else None
        )
        response = AttendanceResponse.from_orm_with_urls(
            attendance, check_in_url=check_in_url, check_out_url=None
        )
        return response

    def _calculate_work_hours_and_overtime(
        self, check_in_time: datetime, check_out_time: datetime
    ) -> tuple[float, float]:
        """
        Calculate work hours (until 18:00) and overtime hours (after 18:00).

        Logic:
        - work_hours: Dihitung dari check_in sampai maksimal jam 18:00
        - overtime_hours: Dihitung setelah jam 18:00

        Args:
            check_in_time: Check-in datetime (timezone-aware)
            check_out_time: Check-out datetime (timezone-aware)

        Returns:
            Tuple (work_hours, overtime_hours) as decimals
        """
        from datetime import time as dt_time

        # Buat cutoff time (18:00) pada tanggal yang sama dengan check_out_time
        # Gunakan timezone dari check_out_time
        cutoff_time = check_out_time.replace(hour=18, minute=0, second=0, microsecond=0)

        if check_out_time <= cutoff_time:
            # Check-out sebelum atau tepat jam 18:00
            # Semua dihitung sebagai work_hours, overtime = 0
            time_diff = check_out_time - check_in_time
            work_hours = time_diff.total_seconds() / 3600
            overtime_hours = 0.0
        else:
            # Check-out setelah jam 18:00
            # work_hours: dari check_in sampai jam 18:00
            # overtime_hours: dari jam 18:00 sampai check_out
            work_time_diff = cutoff_time - check_in_time
            overtime_time_diff = check_out_time - cutoff_time

            work_hours = work_time_diff.total_seconds() / 3600
            overtime_hours = overtime_time_diff.total_seconds() / 3600

        return round(work_hours, 2), round(overtime_hours, 2)

    async def check_out(
        self,
        employee_id: int,
        request: CheckOutRequest,
        request_obj: Request,
        selfie: UploadFile,
    ) -> Tuple[AttendanceResponse, str]:
        """
        Check-out attendance untuk employee.

        Args:
            employee_id: ID employee yang check-out
            request: Data check-out request
            request_obj: FastAPI request object untuk mendapatkan IP
            selfie: File selfie check-out (MANDATORY)

        Returns:
            Tuple of (AttendanceResponse, message) untuk router

        Raises:
            NotFoundException: Jika belum check-in hari ini
            ValidationException: Jika sudah check-out hari ini atau selfie tidak ada
        """
        # Validate selfie is mandatory
        if not selfie:
            raise ValidationException("Foto selfie check-out wajib diisi")

        today = date.today()

        # Get employee info untuk validasi employee type
        employee_data = await self._get_employee_dict(employee_id)
        employee_type = employee_data.get("employee_type")

        # Validate hari kerja berdasarkan employee type
        self._validate_working_day_and_employee_type(today, employee_type)

        # Validate tidak sedang cuti
        await self._validate_not_on_leave(employee_id, today)

        # Cek apakah sudah ada attendance hari ini
        existing = await self.queries.get_by_employee_and_date(
            employee_id, today
        )

        if not existing or not existing.check_in_time:
            raise NotFoundException("Anda belum check-in hari ini")

        if existing.check_out_time:
            raise ValidationException(
                f"Anda sudah check-out hari ini pada {existing.check_out_time.strftime('%H:%M:%S')}"
            )

        from datetime import timezone

        now = datetime.now(timezone.utc)
        client_ip = request_obj.client.host if request_obj.client else None

        # Handle selfie upload to GCP (save path only)
        _, selfie_path = await upload_file_to_gcp(
            file=selfie,
            entity_type="attendances",
            entity_id=employee_id,
            subfolder=f"check_out/{today.strftime('%Y-%m-%d')}",
            allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES,
            max_size=settings.MAX_IMAGE_SIZE,
        )

        # Handle location data and reverse geocoding
        location_name = None
        if request.latitude is not None and request.longitude is not None:
            # Get address from coordinates using Nominatim
            location_name = await nominatim_client.reverse_geocode(
                latitude=request.latitude, longitude=request.longitude
            )

        # Calculate work hours (until 18:00) and overtime hours (after 18:00)
        work_hours, overtime_hours = self._calculate_work_hours_and_overtime(
            existing.check_in_time, now
        )

        # Update attendance with check-out info
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

        # Generate signed URLs for response
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

        # Build message with overtime info if applicable
        message = f"Check-out berhasil. Total jam kerja: {work_hours} jam"
        if overtime_hours > 0:
            message += f", overtime: {overtime_hours} jam"

        return response, message

    async def get_my_attendance(
        self,
        employee_id: int,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[list[AttendanceListResponse], dict]:
        """
        Ambil attendance history employee sendiri.

        Args:
            employee_id: ID employee
            type: Tipe periode (today/weekly/monthly). Jika diisi, start_date dan end_date diabaikan
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            Tuple of (list[AttendanceListResponse], pagination_dict)
        """
        # Jika type ada, convert ke start_date & end_date
        if type:
            start_date, end_date = self._get_date_range_from_type(type)

        skip = (page - 1) * limit

        attendances = await self.queries.list_by_employee(
            employee_id, start_date, end_date, skip, limit
        )

        total_items = await self.queries.count_by_employee(
            employee_id, start_date, end_date
        )

        # Get employee info for enrichment
        employee_name = None
        employee_number = None
        org_unit_name = None
        try:
            employee_data = await self._get_employee_dict(employee_id)
            employee_name = employee_data.get("name")
            employee_number = employee_data.get("employee_number")

            # Get org unit info from employee data
            org_unit_data = employee_data.get("org_unit")
            if org_unit_data:
                org_unit_name = org_unit_data.get("name")
        except:
            # If employee/org_unit not found, skip enrichment
            pass

        attendances_data: list[AttendanceListResponse] = []
        for att in attendances:
            check_in_url = generate_signed_url_for_path(att.check_in_selfie_path)
            check_out_url = generate_signed_url_for_path(att.check_out_selfie_path)
            response = AttendanceListResponse.from_orm_with_urls(
                attendance=att,
                employee_name=employee_name,
                employee_number=employee_number,
                org_unit_name=org_unit_name,
                check_in_url=check_in_url,
                check_out_url=check_out_url,
            )
            attendances_data.append(response)

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total_items,
        }
        return attendances_data, pagination

    async def get_team_attendance(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[list[AttendanceListResponse], dict]:
        """
        Ambil attendance team/subordinates untuk org unit head.

        Args:
            employee_id: ID employee yang meminta (head)
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            status: Filter status attendance
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            Tuple of (list[AttendanceListResponse], pagination_dict)
        """
        # Ambil semua subordinates dari employee (recursive) dengan pagination
        # Max 250 per page sesuai limit dari employee core service
        all_subordinates = []
        subordinate_page = 1
        subordinate_page_size = 250

        while True:
            subordinates_data = await self._get_subordinates_dict(
                employee_id=employee_id,
                page=subordinate_page,
                limit=subordinate_page_size,
                recursive=True,
            )

            all_subordinates.extend(subordinates_data.get("employees", []))

            # Check if there are more pages
            pagination = subordinates_data.get("pagination", {})
            total_pages = pagination.get("total_pages", 1)

            if subordinate_page >= total_pages:
                break

            subordinate_page += 1

        subordinate_ids = [emp["id"] for emp in all_subordinates]

        if not subordinate_ids:
            pagination = {
                "page": page,
                "limit": limit,
                "total_items": 0,
            }
            return [], pagination

        skip = (page - 1) * limit

        attendances = await self.queries.list_by_employees(
            subordinate_ids, start_date, end_date, status, skip, limit
        )

        total_items = await self.queries.count_by_employees(
            subordinate_ids, start_date, end_date, status
        )

        # Build response dengan employee dan org unit info
        attendances_data: list[AttendanceListResponse] = []
        for att in attendances:
            # Get employee info
            employee_name = None
            employee_number = None
            org_unit_name = None
            try:
                employee_data = await self._get_employee_dict(att.employee_id)
                employee_name = employee_data.get("name")
                employee_number = employee_data.get("employee_number")

                # Get org unit info from employee data
                org_unit_data = employee_data.get("org_unit")
                if org_unit_data:
                    org_unit_name = org_unit_data.get("name")
            except:
                # If employee/org_unit not found, skip enrichment
                pass

            # Generate signed URLs for selfies
            check_in_url = generate_signed_url_for_path(att.check_in_selfie_path)
            check_out_url = generate_signed_url_for_path(att.check_out_selfie_path)

            response = AttendanceListResponse.from_orm_with_urls(
                attendance=att,
                employee_name=employee_name,
                employee_number=employee_number,
                org_unit_name=org_unit_name,
                check_in_url=check_in_url,
                check_out_url=check_out_url,
            )
            attendances_data.append(response)

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total_items,
        }
        return attendances_data, pagination

    async def get_all_attendances(
        self,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        org_unit_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[list[AttendanceListResponse], dict]:
        """
        Ambil semua attendance dengan berbagai filter (admin/super admin only).

        Args:
            type: Tipe periode (today/weekly/monthly). Jika diisi, start_date dan end_date diabaikan
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            org_unit_id: Filter berdasarkan org unit
            employee_id: Filter berdasarkan employee ID tertentu
            status: Filter status attendance (present/absent/leave)
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            Tuple of (list[AttendanceListResponse], pagination_dict)

        Raises:
            BadRequestException: Jika status tidak valid
        """
        # Jika type ada, convert ke start_date & end_date (priority lebih tinggi)
        if type:
            start_date, end_date = self._get_date_range_from_type(type)

        # Validate status jika ada
        if status and status not in AttendanceConstants.VALID_STATUSES:
            raise BadRequestException(
                f"Status tidak valid. Harus salah satu dari: {', '.join(AttendanceConstants.VALID_STATUSES)}"
            )

        # Build employee_ids list untuk filter
        employee_ids = None

        # Filter berdasarkan employee_id tertentu (override org_unit filter jika ada)
        if employee_id:
            employee_ids = [employee_id]

        skip = (page - 1) * limit

        # Ambil attendance list
        attendances = await self.queries.list_all(
            employee_ids=employee_ids,
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=skip,
            limit=limit,
        )

        # Count total
        total_items = await self.queries.count_all(
            employee_ids=employee_ids,
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
        )

        # Build response dengan employee dan org unit info
        attendances_data: list[AttendanceListResponse] = []
        for att in attendances:
            # Get employee info
            employee_name = None
            employee_number = None
            org_unit_name = None
            try:
                employee_data = await self._get_employee_dict(att.employee_id)
                employee_name = employee_data.get("name")
                employee_number = employee_data.get("employee_number")

                # Get org unit info from employee data
                org_unit_data = employee_data.get("org_unit")
                if org_unit_data:
                    org_unit_name = org_unit_data.get("name")
            except:
                # If employee/org_unit not found, skip enrichment
                pass

            # Generate signed URLs for selfies
            check_in_url = generate_signed_url_for_path(att.check_in_selfie_path)
            check_out_url = generate_signed_url_for_path(att.check_out_selfie_path)

            response = AttendanceListResponse.from_orm_with_urls(
                attendance=att,
                employee_name=employee_name,
                employee_number=employee_number,
                org_unit_name=org_unit_name,
                check_in_url=check_in_url,
                check_out_url=check_out_url,
            )
            attendances_data.append(response)

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total_items,
        }
        return attendances_data, pagination

    async def bulk_mark_present(
        self,
        request: BulkMarkPresentRequest,
        created_by: int,
    ) -> BulkMarkPresentSummary:
        """
        Bulk mark present untuk semua employees pada tanggal tertentu.

        Args:
            request: Data bulk mark present request
            created_by: ID employee yang membuat

        Returns:
            BulkMarkPresentSummary dengan summary hasil operasi

        Logic:
            - Mengambil semua employees yang aktif dari workforce service
            - Untuk setiap employee:
              - Cek apakah sudah ada attendance pada tanggal tersebut
              - Jika sudah ada: update status menjadi 'present' dan notes
              - Jika belum ada: create attendance baru dengan status 'present'
        """
        # Get all active employees from workforce service
        all_employees = []
        page = 1
        limit = 200  # Max items per page

        while True:
            employees_data = await self._list_employees_dict(
                page=page,
                limit=limit,
                is_active=True,
            )

            all_employees.extend(employees_data["employees"])

            # Check if there are more pages
            total_pages = employees_data["pagination"]["total_pages"]
            if page >= total_pages:
                break

            page += 1

        # Filter employees yang memiliki employee_id (skip yang None)
        valid_employees = [emp for emp in all_employees if emp.get("id")]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for employee in valid_employees:
            employee_id = employee["id"]
            org_unit_id = employee.get("org_unit_id")

            try:
                # Cek apakah sudah ada attendance pada tanggal ini
                existing = await self.queries.get_by_employee_and_date(
                    employee_id, request.attendance_date
                )

                if existing:
                    # Update existing attendance
                    update_data = {
                        "status": "present",
                        "check_in_notes": request.notes,
                    }
                    await self.commands.update(existing.id, update_data)
                    updated_count += 1
                else:
                    # Create new attendance
                    attendance_data = {
                        "employee_id": employee_id,
                        "org_unit_id": org_unit_id,
                        "attendance_date": request.attendance_date,
                        "status": "present",
                        "check_in_notes": request.notes,
                        "created_by": created_by,
                    }
                    await self.commands.create(attendance_data)
                    created_count += 1
            except Exception as e:
                # Skip jika ada error untuk employee tertentu
                print(f"Error processing employee {employee_id}: {str(e)}")
                skipped_count += 1
                continue

        return BulkMarkPresentSummary(
            total_employees=len(valid_employees),
            created=created_count,
            updated=updated_count,
            skipped=skipped_count,
            attendance_date=request.attendance_date.strftime("%Y-%m-%d"),
            notes=request.notes,
        )

    async def check_attendance_status(
        self, employee_id: int
    ) -> AttendanceStatusCheckResponse:
        """
        Check apakah employee bisa absen hari ini (check status cuti dan hari kerja).

        Args:
            employee_id: ID employee

        Returns:
            AttendanceStatusCheckResponse dengan status informasi
        """
        today = date.today()

        # Get employee info untuk cek employee type
        employee_data = await self._get_employee_dict(employee_id)
        employee_type = employee_data.get("employee_type")

        # Check working day dengan mempertimbangkan employee type
        is_sunday = today.weekday() == 6  # 6 = Sunday

        # Determine if working day based on employee type
        if is_sunday:
            # Hari Minggu: hanya on_site yang bisa absen
            is_working_day = employee_type == "on_site"
        else:
            # Senin-Sabtu: semua tipe bisa absen
            is_working_day = True

        # Check leave status
        leave_request = await self.leave_queries.is_on_leave(
            employee_id, today
        )
        is_on_leave = leave_request is not None

        # Determine if can attend
        can_attend = is_working_day and not is_on_leave

        # Build reason if cannot attend
        reason = None
        if not is_working_day:
            if is_sunday and employee_type != "on_site":
                reason = (
                    "Tidak bisa absen pada hari Minggu. "
                    "Hanya karyawan dengan tipe 'on_site' yang dapat absen di hari Minggu. "
                    "Hari kerja untuk tipe lainnya adalah Senin-Sabtu."
                )
            else:
                reason = "Hari ini adalah hari Minggu. Hari kerja adalah Senin-Sabtu."
        elif is_on_leave:
            reason = f"Anda sedang cuti ({leave_request.leave_type}) dari {leave_request.start_date.strftime('%d-%m-%Y')} sampai {leave_request.end_date.strftime('%d-%m-%Y')}."

        # Build leave details if on leave
        leave_details = None
        if is_on_leave:
            leave_details = LeaveDetailsResponse(
                leave_type=leave_request.leave_type,
                start_date=leave_request.start_date.strftime("%Y-%m-%d"),
                end_date=leave_request.end_date.strftime("%Y-%m-%d"),
                total_days=leave_request.total_days,
                reason=leave_request.reason,
            )

        return AttendanceStatusCheckResponse(
            can_attend=can_attend,
            reason=reason,
            is_on_leave=is_on_leave,
            is_working_day=is_working_day,
            employee_type=employee_type,
            leave_details=leave_details,
        )

    async def get_attendance_by_id(self, attendance_id: int) -> AttendanceResponse:
        """
        Ambil attendance berdasarkan ID.

        Args:
            attendance_id: ID attendance

        Returns:
            AttendanceResponse dengan data attendance

        Raises:
            NotFoundException: Jika attendance tidak ditemukan
        """
        attendance = await self.attendance_repo.get(attendance_id)

        if not attendance:
            raise NotFoundException(
                f"Attendance dengan ID {attendance_id} tidak ditemukan"
            )

        # Generate signed URLs for response
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

    async def mark_present_by_id(
        self,
        attendance_id: int,
        current_user_employee_id: int,
        admin_name: str,
        notes: Optional[str] = None,
    ) -> AttendanceResponse:
        """
        Mark attendance sebagai present berdasarkan ID (untuk admin/super admin).

        Args:
            attendance_id: ID attendance yang akan diupdate
            current_user_employee_id: Employee ID dari user yang melakukan update
            admin_name: Nama lengkap admin yang melakukan update
            notes: Catatan opsional tambahan

        Returns:
            AttendanceResponse dengan data attendance yang sudah diupdate

        Raises:
            NotFoundException: Jika attendance tidak ditemukan
            ValidationException: Jika user mencoba update attendance sendiri
        """
        from datetime import timezone

        # Get existing attendance
        attendance = await self.attendance_repo.get(attendance_id)

        if not attendance:
            raise NotFoundException(
                f"Attendance dengan ID {attendance_id} tidak ditemukan"
            )

        # Prevent user from updating their own attendance
        if attendance.employee_id == current_user_employee_id:
            raise ValidationException(
                "Anda tidak dapat mengubah status attendance Anda sendiri"
            )

        # Get attendance date for generating time
        attendance_date = attendance.attendance_date
        now = datetime.now(timezone.utc)

        # Create datetime with microsecond precision for consistency with actual check-in/check-out
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

        # Calculate work hours (8 hours standard)
        work_hours = 8.0
        overtime_hours = 0.0

        # Build update notes
        auto_note = (
            f"Diubah oleh {admin_name} pada {now.strftime('%d-%m-%Y %H:%M:%S')} WIB"
        )
        final_notes = f"{notes}. {auto_note}" if notes else auto_note

        # Update attendance
        update_data = {
            "status": "present",
            "check_in_time": check_in_datetime,
            "check_out_time": check_out_datetime,
            "work_hours": work_hours,
            "overtime_hours": overtime_hours,
            "check_in_notes": final_notes,
            "check_out_notes": final_notes,
        }

        updated_attendance = await self.commands.update(
            attendance_id, update_data
        )

        if not updated_attendance:
            raise ValidationException("Gagal update attendance")

        # Generate signed URLs for response
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
        response = AttendanceResponse.from_orm_with_urls(
            updated_attendance, check_in_url=check_in_url, check_out_url=check_out_url
        )
        return response

    def _generate_working_days_for_employee(
        self, start_date: date, end_date: date, employee_type: Optional[str]
    ) -> list[date]:
        """
        Generate list working days dalam date range berdasarkan employee type.

        Business Rules:
        - Employee type 'on_site': Kerja 7 hari (Senin-Minggu)
        - Employee type lainnya (hybrid, ho, dll): Kerja 6 hari (Senin-Sabtu)

        Args:
            start_date: Tanggal mulai
            end_date: Tanggal akhir
            employee_type: Tipe employee ('on_site', 'hybrid', 'ho', dll)

        Returns:
            List of dates (working days based on employee type)
        """
        working_days = []
        current_date = start_date

        while current_date <= end_date:
            # weekday(): 0=Monday, 6=Sunday
            is_sunday = current_date.weekday() == 6

            # On_site employee kerja 7 hari seminggu (termasuk Minggu)
            # Employee lain kerja 6 hari (Senin-Sabtu)
            if employee_type == "on_site":
                # On_site: include all days (including Sunday)
                working_days.append(current_date)
            elif not is_sunday:
                # Non on_site: exclude Sunday
                working_days.append(current_date)

            current_date += timedelta(days=1)

        return working_days

    async def get_attendance_report(
        self,
        org_unit_id: int,
        start_date: date,
        end_date: date,
    ) -> list[EmployeeAttendanceReport]:
        """
        Ambil attendance report untuk org unit tertentu dalam date range.
        Return list employees dengan attendance mereka untuk keperluan export Excel.

        IMPORTANT: Setiap employee memiliki jumlah attendance record berdasarkan
        working days mereka sesuai employee type:
        - On_site: 7 hari seminggu (Senin-Minggu)
        - Lainnya: 6 hari seminggu (Senin-Sabtu)
        Missing dates akan diisi dengan default values (status="absent").

        Args:
            org_unit_id: ID org unit (WAJIB)
            start_date: Tanggal mulai (WAJIB)
            end_date: Tanggal akhir (WAJIB)

        Returns:
            list[EmployeeAttendanceReport] untuk export Excel

        Raises:
            BadRequestException: Jika validasi input gagal
        """
        # Validasi date range
        if start_date > end_date:
            raise BadRequestException(
                "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            )

        # Get all employees dari org unit (loop all pages untuk mendapat semua data)
        all_employees = []
        page = 1
        limit = 200  # Max items per page

        while True:
            employees_data = await self._get_employees_by_org_unit_dict(
                org_unit_id=org_unit_id,
                page=page,
                limit=limit,
                include_children=False,
            )

            all_employees.extend(employees_data["employees"])

            total_pages = employees_data["pagination"]["total_pages"]
            if page >= total_pages:
                break

            page += 1

        if not all_employees:
            return []

        # Get all attendance untuk org_unit dan date range
        attendances = await self.queries.get_report_by_org_unit(
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Group attendance by employee_id dan tanggal untuk O(1) lookup
        attendance_by_employee_date = {}
        for att in attendances:
            if att.employee_id not in attendance_by_employee_date:
                attendance_by_employee_date[att.employee_id] = {}

            attendance_by_employee_date[att.employee_id][att.attendance_date] = att

        # Build final report
        report_data = []
        for employee in all_employees:
            employee_id = employee["id"]
            employee_type = employee.get("employee_type")

            # Generate working days berdasarkan employee type
            # On_site: 7 hari (termasuk Minggu), Lainnya: 6 hari (exclude Minggu)
            employee_working_days = self._generate_working_days_for_employee(
                start_date, end_date, employee_type
            )

            # Get attendance dict untuk employee ini
            employee_att_dict = attendance_by_employee_date.get(employee_id, {})

            # Build attendance records untuk working days employee ini
            employee_attendances = []
            total_present_days = 0
            total_work_hours = 0.0
            total_overtime_hours = 0.0

            for working_day in employee_working_days:
                if working_day in employee_att_dict:
                    # Ada data attendance, gunakan data asli
                    att = employee_att_dict[working_day]
                    record = AttendanceRecordInReport(
                        attendance_date=att.attendance_date,
                        status=att.status,
                        check_in_time=att.check_in_time,
                        check_out_time=att.check_out_time,
                        work_hours=att.work_hours,
                        overtime_hours=att.overtime_hours,
                    )

                    # Hitung total_present_days (present dan hybrid)
                    if att.status in ["present", "hybrid"]:
                        total_present_days += 1

                    # Hitung total_work_hours
                    if att.work_hours:
                        total_work_hours += float(att.work_hours)

                    # Hitung total_overtime_hours
                    if att.overtime_hours:
                        total_overtime_hours += float(att.overtime_hours)
                else:
                    # Tidak ada data, gunakan default values (absent)
                    record = AttendanceRecordInReport(
                        attendance_date=working_day,
                        status=AttendanceStatus.ABSENT,
                        check_in_time=None,
                        check_out_time=None,
                        work_hours=None,
                        overtime_hours=None,
                    )

                employee_attendances.append(record)

            # Get org unit info
            org_unit_name = None
            if employee.get("org_unit"):
                org_unit_name = employee["org_unit"].get("name")

            # Build employee report
            employee_report = EmployeeAttendanceReport(
                employee_id=employee_id,
                employee_name=employee["name"],
                employee_number=employee.get("employee_number"),
                employee_position=employee.get("position"),
                employee_type=employee.get("employee_type"),
                org_unit_id=employee.get("org_unit_id"),
                org_unit_name=org_unit_name,
                attendances=employee_attendances,
                total_present_days=total_present_days,
                total_work_hours=(
                    Decimal(str(total_work_hours)) if total_work_hours else None
                ),
                total_overtime_hours=(
                    Decimal(str(total_overtime_hours)) if total_overtime_hours else None
                ),
            )
            report_data.append(employee_report)

        return report_data

    async def get_attendance_overview(
        self,
        org_unit_id: Optional[int],
        start_date: date,
        end_date: date,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[list[EmployeeAttendanceOverview], dict]:
        """
        Ambil attendance overview per employee dengan paginasi.
        Menampilkan summary kehadiran (total present, absent, leave) per employee.

        Args:
            org_unit_id: ID org unit (OPTIONAL). Jika None, ambil semua employees
            start_date: Tanggal mulai (WAJIB)
            end_date: Tanggal akhir (WAJIB)
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            Tuple of (list[EmployeeAttendanceOverview], pagination_dict)

        Raises:
            BadRequestException: Jika validasi input gagal
        """
        # Validasi date range
        if start_date > end_date:
            raise BadRequestException(
                "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            )

        # Get employees dengan paginasi
        if org_unit_id:
            # Get employees dari org unit tertentu
            employees_data = await self._get_employees_by_org_unit_dict(
                org_unit_id=org_unit_id,
                page=page,
                limit=limit,
                include_children=False,
            )
        else:
            # Get ALL active employees (tanpa filter org_unit_id)
            employees_data = await self._list_employees_dict(
                page=page,
                limit=limit,
                is_active=True,
            )

        employees = employees_data["employees"]
        pagination = employees_data["pagination"]

        if not employees:
            pagination_dict = {
                "page": page,
                "limit": limit,
                "total_items": 0,
            }
            return [], pagination_dict

        # Get employee IDs untuk query attendance
        employee_ids = [emp["id"] for emp in employees]

        # Get semua attendance untuk employee IDs ini dalam date range
        attendances = await self.queries.get_by_employee_ids(
            employee_ids=employee_ids,
            start_date=start_date,
            end_date=end_date,
        )

        # Group attendance by employee_id dan calculate summary
        attendance_summary = {}
        for att in attendances:
            if att.employee_id not in attendance_summary:
                attendance_summary[att.employee_id] = {
                    "total_present": 0,
                    "total_absent": 0,
                    "total_leave": 0,
                    "total_hybrid": 0,
                    "total_work_hours": 0,
                    "total_overtime_hours": 0,
                }

            summary = attendance_summary[att.employee_id]

            # Count by status
            if att.status == "present":
                summary["total_present"] += 1
            elif att.status == "absent":
                summary["total_absent"] += 1
            elif att.status == "leave":
                summary["total_leave"] += 1
            elif att.status == "hybrid":
                summary["total_hybrid"] += 1

            # Sum work hours
            if att.work_hours:
                summary["total_work_hours"] += float(att.work_hours)

            # Sum overtime hours
            if att.overtime_hours:
                summary["total_overtime_hours"] += float(att.overtime_hours)

        # Build overview response
        overview_data = []
        for employee in employees:
            employee_id = employee["id"]

            # Get summary untuk employee ini (default 0 jika tidak ada)
            summary = attendance_summary.get(
                employee_id,
                {
                    "total_present": 0,
                    "total_absent": 0,
                    "total_leave": 0,
                    "total_hybrid": 0,
                    "total_work_hours": 0,
                    "total_overtime_hours": 0,
                },
            )

            # Get org unit info
            org_unit_name = None
            if employee.get("org_unit"):
                org_unit_name = employee["org_unit"].get("name")

            # Build employee overview
            employee_overview = EmployeeAttendanceOverview(
                employee_id=employee_id,
                employee_name=employee["name"],
                employee_number=employee.get("employee_number"),
                employee_position=employee.get("position"),
                org_unit_id=employee.get("org_unit_id"),
                org_unit_name=org_unit_name,
                total_present=summary["total_present"],
                total_absent=summary["total_absent"],
                total_leave=summary["total_leave"],
                total_hybrid=summary["total_hybrid"],
                total_work_hours=summary["total_work_hours"],
                total_overtime_hours=summary["total_overtime_hours"],
            )
            overview_data.append(employee_overview)

        pagination_dict = {
            "page": pagination["page"],
            "limit": pagination["limit"],
            "total_items": pagination["total_items"],
        }
        return overview_data, pagination_dict
