from typing import Optional, List
from datetime import date
from app.modules.leave_requests.repositories.leave_request_repository import (
    LeaveRequestRepository,
)
from app.modules.leave_requests.schemas.requests import (
    LeaveRequestCreateRequest,
    LeaveRequestUpdateRequest,
)
from app.modules.leave_requests.schemas.responses import (
    LeaveRequestResponse,
    LeaveRequestListResponse,
)
from app.modules.leave_requests.schemas.shared import LeaveType
from app.external_clients.grpc.employee_client import EmployeeGRPCClient
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
)
from app.modules.leave_requests.utils.total_days import (
    calculate_working_days,
    validate_no_overlapping_leave,
    validate_leave_dates,
)
from app.core.schemas import (
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)


class LeaveRequestService:
    """Service untuk operasi leave request management."""

    def __init__(
        self,
        leave_request_repo: LeaveRequestRepository,
        employee_client: EmployeeGRPCClient,
    ):
        self.leave_request_repo = leave_request_repo
        self.employee_client = employee_client

    async def create_leave_request(
        self, request: LeaveRequestCreateRequest, created_by_user_id: int
    ) -> DataResponse[LeaveRequestResponse]:
        """
        Membuat leave request baru (HR Admin/Super Admin).

        Args:
            request: Data leave request baru
            created_by_user_id: ID user yang membuat leave request

        Returns:
            DataResponse dengan LeaveRequestResponse

        Raises:
            NotFoundException: Jika employee tidak ditemukan
            BadRequestException: Jika validasi tanggal gagal (HTTP 400)
            ConflictException: Jika ada cuti yang overlap (HTTP 409)
        """
        employee_data = await self.employee_client.get_employee(request.employee_id)
        if not employee_data:
            raise NotFoundException(
                f"Employee dengan ID {request.employee_id} tidak ditemukan"
            )

        employee_type = employee_data.get("employee_type")

        validate_leave_dates(request.start_date, request.end_date)

        await validate_no_overlapping_leave(
            leave_request_repo=self.leave_request_repo,
            employee_id=request.employee_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        total_days = calculate_working_days(
            request.start_date, request.end_date, employee_type
        )

        leave_request_data = {
            "employee_id": request.employee_id,
            "leave_type": request.leave_type.value,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "total_days": total_days,
            "reason": request.reason,
            "created_by": created_by_user_id,
        }

        leave_request = await self.leave_request_repo.create(leave_request_data)

        leave_request_response = LeaveRequestResponse.model_validate(leave_request)
        return create_success_response(
            message="Leave request berhasil dibuat",
            data=leave_request_response,
        )

    async def get_leave_request_by_id(
        self, leave_request_id: int
    ) -> DataResponse[LeaveRequestResponse]:
        """
        Ambil detail leave request berdasarkan ID.

        Args:
            leave_request_id: ID leave request

        Returns:
            DataResponse dengan LeaveRequestResponse

        Raises:
            NotFoundException: Jika leave request tidak ditemukan
        """
        leave_request = await self.leave_request_repo.get(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        leave_request_response = LeaveRequestResponse.model_validate(leave_request)
        return create_success_response(
            message="Leave request berhasil diambil",
            data=leave_request_response,
        )

    async def update_leave_request(
        self,
        leave_request_id: int,
        request: LeaveRequestUpdateRequest,
    ) -> DataResponse[LeaveRequestResponse]:
        """
        Update leave request (HR Admin/Super Admin).

        Args:
            leave_request_id: ID leave request yang akan diupdate
            request: Data update

        Returns:
            DataResponse dengan LeaveRequestResponse

        Raises:
            NotFoundException: Jika leave request tidak ditemukan
            BadRequestException: Jika tidak ada data yang akan diupdate atau validasi tanggal gagal (HTTP 400)
            ConflictException: Jika ada cuti yang overlap (HTTP 409)
        """
        leave_request = await self.leave_request_repo.get(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        update_data = request.model_dump(exclude_none=True)

        if not update_data:
            raise BadRequestException("Tidak ada data yang akan diupdate")

        new_start_date = update_data.get("start_date", leave_request.start_date)
        new_end_date = update_data.get("end_date", leave_request.end_date)

        validate_leave_dates(new_start_date, new_end_date)

        if "start_date" in update_data or "end_date" in update_data:
            await validate_no_overlapping_leave(
                leave_request_repo=self.leave_request_repo,
                employee_id=leave_request.employee_id,
                start_date=new_start_date,
                end_date=new_end_date,
                exclude_leave_request_id=leave_request_id,
            )

            # Get employee type untuk perhitungan total days
            employee_data = await self.employee_client.get_employee(
                leave_request.employee_id
            )
            employee_type = employee_data.get("employee_type")

            update_data["total_days"] = calculate_working_days(
                new_start_date, new_end_date, employee_type
            )

        if "leave_type" in update_data:
            update_data["leave_type"] = update_data["leave_type"].value

        updated_leave_request = await self.leave_request_repo.update(
            leave_request_id, update_data
        )

        leave_request_response = LeaveRequestResponse.model_validate(
            updated_leave_request
        )
        return create_success_response(
            message="Leave request berhasil diperbarui",
            data=leave_request_response,
        )

    async def delete_leave_request(self, leave_request_id: int) -> DataResponse[None]:
        """
        Hapus leave request (HR Admin/Super Admin).

        Args:
            leave_request_id: ID leave request yang akan dihapus

        Returns:
            DataResponse dengan None

        Raises:
            NotFoundException: Jika leave request tidak ditemukan
        """
        leave_request = await self.leave_request_repo.get(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        await self.leave_request_repo.delete(leave_request_id)

        return create_success_response(
            message="Leave request berhasil dihapus",
            data=None,
        )

    async def get_my_leave_requests(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedResponse[LeaveRequestResponse]:
        """
        Ambil daftar leave requests employee sendiri.

        Args:
            employee_id: ID employee
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            leave_type: Filter jenis cuti
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            PaginatedResponse dengan list LeaveRequestResponse
        """
        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests = await self.leave_request_repo.list_by_employee(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        total_items = await self.leave_request_repo.count_by_employee(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
        )

        leave_requests_data: List[LeaveRequestResponse] = [
            LeaveRequestResponse.model_validate(lr) for lr in leave_requests
        ]

        return create_paginated_response(
            message="Daftar leave request berhasil diambil",
            data=leave_requests_data,
            page=page,
            limit=limit,
            total_items=total_items,
        )

    async def list_all_leave_requests(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedResponse[LeaveRequestListResponse]:
        """
        Ambil daftar semua leave requests (HR Admin/Super Admin).

        Args:
            employee_id: Filter berdasarkan employee ID
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            leave_type: Filter jenis cuti
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            PaginatedResponse dengan list LeaveRequestListResponse
        """
        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests = await self.leave_request_repo.list_all_leave_requests(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        total_items = await self.leave_request_repo.count_all_leave_requests(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
        )

        leave_requests_data: List[LeaveRequestListResponse] = []
        for lr in leave_requests:
            employee_data = await self.employee_client.get_employee(lr.employee_id)

            leave_request_response = LeaveRequestListResponse(
                id=lr.id,
                employee_id=lr.employee_id,
                employee_name=employee_data.get("name"),
                employee_number=employee_data.get("employee_number"),
                leave_type=LeaveType(lr.leave_type),
                start_date=lr.start_date,
                end_date=lr.end_date,
                total_days=lr.total_days,
                reason=lr.reason,
                created_at=lr.created_at,
                updated_at=lr.updated_at,
            )

            leave_requests_data.append(leave_request_response)

        return create_paginated_response(
            message="Daftar leave request berhasil diambil",
            data=leave_requests_data,
            page=page,
            limit=limit,
            total_items=total_items,
        )

    async def get_team_leave_requests(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        leave_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedResponse[LeaveRequestListResponse]:
        """
        Ambil leave requests team/subordinates untuk org unit head.

        Args:
            employee_id: ID employee yang meminta (head)
            start_date: Filter tanggal mulai
            end_date: Filter tanggal akhir
            leave_type: Filter jenis cuti
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            PaginatedResponse dengan list LeaveRequestListResponse
        """
        # Ambil semua subordinates dari employee (recursive) dengan pagination
        # Max 250 per page sesuai limit dari employee core service
        all_subordinates: List[dict] = []
        subordinate_page = 1
        subordinate_page_size = 250

        while True:
            subordinates_data = await self.employee_client.get_employee_subordinates(
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
            return create_paginated_response(
                message="Tidak ada subordinate ditemukan",
                data=[],
                page=page,
                limit=limit,
                total_items=0,
            )

        if page < 1:
            raise BadRequestException("Halaman harus lebih besar dari 0")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit harus antara 1 dan 100")

        skip = (page - 1) * limit

        leave_requests = await self.leave_request_repo.list_by_employees(
            employee_ids=subordinate_ids,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            skip=skip,
            limit=limit,
        )

        total_items = await self.leave_request_repo.count_by_employees(
            employee_ids=subordinate_ids,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
        )

        leave_requests_data: List[LeaveRequestListResponse] = []
        for lr in leave_requests:
            employee_data = await self.employee_client.get_employee(lr.employee_id)

            leave_request_response = LeaveRequestListResponse(
                id=lr.id,
                employee_id=lr.employee_id,
                employee_name=employee_data.get("name"),
                employee_number=employee_data.get("employee_number"),
                leave_type=LeaveType(lr.leave_type),
                start_date=lr.start_date,
                end_date=lr.end_date,
                total_days=lr.total_days,
                reason=lr.reason,
                created_at=lr.created_at,
                updated_at=lr.updated_at,
            )

            leave_requests_data.append(leave_request_response)

        return create_paginated_response(
            message="Daftar leave request team berhasil diambil",
            data=leave_requests_data,
            page=page,
            limit=limit,
            total_items=total_items,
        )
