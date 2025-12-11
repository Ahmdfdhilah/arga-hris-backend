from typing import Optional, List, Tuple
from app.external_clients.grpc.org_unit_client import OrgUnitGRPCClient
from app.modules.org_units.schemas import (
    OrgUnitResponse,
    OrgUnitListResponse,
    OrgUnitHierarchyResponse,
    OrgUnitHierarchyItem,
    OrgUnitTypesResponse,
    BulkInsertResult,
    OrgUnitBulkItem,
)
from app.external_clients.grpc.employee_client import EmployeeGRPCClient

class OrgUnitService:
    def __init__(self, grpc_client: OrgUnitGRPCClient, employee_grpc_client: Optional[EmployeeGRPCClient] = None):
        self.grpc_client = grpc_client
        self.employee_grpc_client = employee_grpc_client

    async def get_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        """
        Get organization unit by ID.

        Args:
            org_unit_id: ID organization unit

        Returns:
            OrgUnitResponse
        """
        data = await self.grpc_client.get_org_unit(org_unit_id)
        return OrgUnitResponse.model_validate(data)

    async def get_org_unit_by_code(self, code: str) -> Optional[OrgUnitResponse]:
        """
        Get organization unit by code.

        Args:
            code: Kode organization unit

        Returns:
            OrgUnitResponse or None if not found
        """
        data = await self.grpc_client.get_org_unit_by_code(code)
        if data is None:
            return None
        return OrgUnitResponse.model_validate(data)

    async def list_org_units(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        parent_id: Optional[int] = None,
        type_filter: Optional[str] = None,
    ) -> Tuple[List[OrgUnitResponse], dict]:
        """
        List organization units with filters and pagination.

        Args:
            page: Nomor halaman
            limit: Jumlah item per halaman
            search: Search query
            parent_id: Filter berdasarkan parent unit
            type_filter: Filter berdasarkan tipe unit

        Returns:
            Tuple of (list of OrgUnitResponse, pagination dict)
        """
        data = await self.grpc_client.list_org_units(
            page, limit, search, parent_id, type_filter
        )
        result = OrgUnitListResponse.model_validate(data)
        pagination = {
            "page": result.pagination.page,
            "limit": result.pagination.limit,
            "total_items": result.pagination.total_items,
        }
        return result.org_units, pagination

    async def get_org_unit_children(
        self, org_unit_id: int, page: int = 1, limit: int = 10
    ) -> Tuple[List[OrgUnitResponse], dict]:
        """
        Get children organization units.

        Args:
            org_unit_id: ID parent organization unit
            page: Nomor halaman
            limit: Jumlah item per halaman

        Returns:
            Tuple of (list of OrgUnitResponse, pagination dict)
        """
        data = await self.grpc_client.get_org_unit_children(
            org_unit_id, page, limit
        )
        result = OrgUnitListResponse.model_validate(data)
        pagination = {
            "page": result.pagination.page,
            "limit": result.pagination.limit,
            "total_items": result.pagination.total_items,
        }
        return result.org_units, pagination

    async def get_org_unit_hierarchy(self, org_unit_id: int) -> OrgUnitHierarchyResponse:
        """
        Get organization unit hierarchy.

        Args:
            org_unit_id: ID organization unit

        Returns:
            OrgUnitHierarchyResponse
        """
        hierarchy_data = await self.grpc_client.get_org_unit_hierarchy(org_unit_id)
        return OrgUnitHierarchyResponse.model_validate(hierarchy_data)

    async def create_org_unit(
        self,
        code: str,
        name: str,
        type: str,
        created_by: int,
        parent_id: Optional[int] = None,
        head_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> OrgUnitResponse:
        """
        Create new org unit via gRPC

        Args (simplified field names):
            code: Kode unit organisasi (unik)
            name: Nama unit organisasi
            type: Tipe unit organisasi
            created_by: ID user yang membuat
            parent_id: ID parent unit (opsional)
            head_id: ID kepala unit (opsional)
            description: Deskripsi unit (opsional)

        Returns:
            OrgUnitResponse

        Note: level dan path akan dihitung otomatis oleh backend
        """
        # Calculate level and path based on parent
        level = 0
        path = "0"

        if parent_id:
            parent = await self.grpc_client.get_org_unit(parent_id)
            level = parent.get("level", 0) + 1
            path = f"{parent.get('path', '0')}.{parent_id}"

        data = await self.grpc_client.create_org_unit(
            org_unit_code=code,
            org_unit_name=name,
            org_unit_type=type,
            org_unit_level=level,
            org_unit_path=path,
            created_by=created_by,
            org_unit_parent_id=parent_id,
            org_unit_head_id=head_id,
            org_unit_description=description,
        )
        return OrgUnitResponse.model_validate(data)

    async def update_org_unit(
        self,
        org_unit_id: int,
        updated_by: int,
        name: Optional[str] = None,
        type: Optional[str] = None,
        parent_id: Optional[int] = None,
        head_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> OrgUnitResponse:
        """
        Update org unit via gRPC

        Args (simplified field names):
            org_unit_id: ID unit organisasi
            updated_by: ID user yang melakukan update
            name: Nama unit (opsional)
            type: Tipe unit (opsional)
            parent_id: ID parent (opsional)
            head_id: ID kepala unit (opsional)
            description: Deskripsi (opsional)
            is_active: Status aktif (opsional)

        Returns:
            OrgUnitResponse
        """
        data = await self.grpc_client.update_org_unit(
            org_unit_id=org_unit_id,
            updated_by=updated_by,
            org_unit_name=name,
            org_unit_type=type,
            org_unit_parent_id=parent_id,
            org_unit_head_id=head_id,
            org_unit_description=description,
            is_active=is_active,
        )
        return OrgUnitResponse.model_validate(data)

    async def get_org_unit_types(self) -> OrgUnitTypesResponse:
        """
        Get all available org unit types from the backend

        Returns:
            OrgUnitTypesResponse
        """
        types = await self.grpc_client.get_org_unit_types()
        return OrgUnitTypesResponse(types=types)

    async def soft_delete_org_unit(
        self,
        org_unit_id: int,
        deleted_by_user_id: int,
    ) -> OrgUnitResponse:
        """
        Soft delete org unit via gRPC

        Args:
            org_unit_id: ID unit organisasi yang akan di-soft delete
            deleted_by_user_id: ID user yang melakukan soft delete

        Returns:
            OrgUnitResponse

        Raises:
            ValidationException: Jika org unit has active employees atau child units
        """
        data = await self.grpc_client.soft_delete_org_unit(
            org_unit_id=org_unit_id,
            deleted_by_user_id=deleted_by_user_id
        )
        return OrgUnitResponse.model_validate(data)

    async def restore_org_unit(self, org_unit_id: int) -> OrgUnitResponse:
        """
        Restore soft-deleted org unit via gRPC

        Args:
            org_unit_id: ID unit organisasi yang akan di-restore

        Returns:
            OrgUnitResponse

        Raises:
            ValidationException: Jika parent is deleted
        """
        data = await self.grpc_client.restore_org_unit(org_unit_id=org_unit_id)
        return OrgUnitResponse.model_validate(data)

    async def list_deleted_org_units(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[OrgUnitResponse], dict]:
        """
        List deleted org units

        Args:
            page: Page number
            limit: Items per page
            search: Search query

        Returns:
            Tuple of (list of OrgUnitResponse, pagination dict)
        """
        data = await self.grpc_client.list_deleted_org_units(
            page=page,
            limit=limit,
            search=search,
        )
        result = OrgUnitListResponse.model_validate(data)
        pagination = {
            "page": result.pagination.page,
            "limit": result.pagination.limit,
            "total_items": result.pagination.total_items,
        }
        return result.org_units, pagination

    async def bulk_insert_org_units(
        self,
        items: List[OrgUnitBulkItem],
        created_by: int,
        skip_errors: bool = False,
    ) -> BulkInsertResult:
        """
        Bulk insert org units from Excel data

        Proses dilakukan dalam 2 fase:
        1. Insert org units tanpa parent (root units)
        2. Insert org units dengan parent (child units)

        Args:
            items: List of OrgUnitBulkItem dari Excel
            created_by: ID user yang membuat
            skip_errors: Skip item yang error dan lanjutkan processing

        Returns:
            BulkInsertResult dengan detail success/error
        """
        result = BulkInsertResult(
            total_items=len(items),
            success_count=0,
            error_count=0,
            errors=[],
            warnings=[],
            created_ids=[]
        )

        # Cache untuk mapping code -> ID
        code_to_id_map = {}

        # Cache untuk mapping email -> employee ID
        email_to_employee_map = {}

        # Resolve head emails to employee IDs
        if self.employee_grpc_client:
            for item in items:
                if item.head_email and item.head_email not in email_to_employee_map:
                    try:
                        employee = await self.employee_grpc_client.get_employee_by_email(item.head_email)
                        if employee:
                            email_to_employee_map[item.head_email] = employee.get("id")
                    except Exception:
                        # Jika tidak ketemu, skip dan kasih warning nanti
                        pass

        # Fase 1: Insert root units (tanpa parent)
        root_items = [item for item in items if not item.parent_code]
        for item in root_items:
            try:
                # Check if code already exists
                existing = await self.get_org_unit_by_code(item.code)
                if existing:
                    result.error_count += 1
                    result.errors.append({
                        "row_number": item.row_number,
                        "code": item.code,
                        "error": f"Kode '{item.code}' sudah ada"
                    })
                    if not skip_errors:
                        continue
                    continue

                # Resolve head_id from email
                head_id = None
                if item.head_email:
                    head_id = email_to_employee_map.get(item.head_email)
                    if not head_id:
                        result.warnings.append(f"Email kepala unit '{item.head_email}' tidak ditemukan untuk {item.code}")

                # Create org unit
                created = await self.create_org_unit(
                    code=item.code,
                    name=item.name,
                    type=item.type,
                    created_by=created_by,
                    parent_id=None,
                    head_id=head_id,
                    description=item.description,
                )

                result.success_count += 1
                result.created_ids.append(created.id)
                code_to_id_map[item.code] = created.id

            except Exception as e:
                result.error_count += 1
                result.errors.append({
                    "row_number": item.row_number,
                    "code": item.code,
                    "error": str(e)
                })
                if not skip_errors:
                    break

        # Fase 2: Insert child units (dengan parent)
        # Sort berdasarkan level (parent harus sudah ada)
        child_items = [item for item in items if item.parent_code]

        # Retry mechanism untuk child items yang parent-nya belum dibuat
        max_retries = 3
        for retry in range(max_retries):
            remaining_items = []

            for item in child_items:
                try:
                    # Check if code already exists
                    existing = await self.get_org_unit_by_code(item.code)
                    if existing:
                        result.error_count += 1
                        result.errors.append({
                            "row_number": item.row_number,
                            "code": item.code,
                            "error": f"Kode '{item.code}' sudah ada"
                        })
                        if not skip_errors:
                            continue
                        continue

                    # Resolve parent_id from parent_code
                    parent_id = code_to_id_map.get(item.parent_code)
                    if not parent_id and item.parent_code:
                        # Try to find parent from database
                        parent = await self.get_org_unit_by_code(item.parent_code)
                        if parent:
                            parent_id = parent.id
                            code_to_id_map[item.parent_code] = parent_id
                        else:
                            # Parent belum ada, retry nanti
                            if retry < max_retries - 1:
                                remaining_items.append(item)
                                continue
                            else:
                                result.error_count += 1
                                result.errors.append({
                                    "row_number": item.row_number,
                                    "code": item.code,
                                    "error": f"Parent code '{item.parent_code}' tidak ditemukan"
                                })
                                if not skip_errors:
                                    continue
                                continue

                    # Resolve head_id from email
                    head_id = None
                    if item.head_email:
                        head_id = email_to_employee_map.get(item.head_email)
                        if not head_id:
                            result.warnings.append(f"Email kepala unit '{item.head_email}' tidak ditemukan untuk {item.code}")

                    # Create org unit
                    created = await self.create_org_unit(
                        code=item.code,
                        name=item.name,
                        type=item.type,
                        created_by=created_by,
                        parent_id=parent_id,
                        head_id=head_id,
                        description=item.description,
                    )

                    result.success_count += 1
                    result.created_ids.append(created.id)
                    code_to_id_map[item.code] = created.id

                except Exception as e:
                    result.error_count += 1
                    result.errors.append({
                        "row_number": item.row_number,
                        "code": item.code,
                        "error": str(e)
                    })
                    if not skip_errors:
                        break

            # Update child_items untuk retry berikutnya
            child_items = remaining_items
            if not child_items:
                break

        return result
