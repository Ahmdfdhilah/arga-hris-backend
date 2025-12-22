from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from app.modules.org_units.schemas.responses import (
    OrgUnitResponse,
    OrgUnitTypesResponse,
    OrgUnitHierarchyResponse,
    BulkInsertResult,
)
from app.modules.org_units.schemas.requests import (
    OrgUnitCreateRequest,
    OrgUnitUpdateRequest,
)
from app.modules.org_units.dependencies import OrgUnitServiceDep
from app.core.dependencies.auth import get_current_user
from app.core.security.rbac import require_permission
from app.core.schemas import (
    CurrentUser,
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)
from app.core.security.rbac import require_role
from app.core.utils import ExcelParser

router = APIRouter(prefix="/org-units", tags=["Organization Units"])


@router.get("/deleted", response_model=PaginatedResponse[OrgUnitResponse])
@require_permission("org_unit.view_deleted")
async def list_deleted_org_units(
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
) -> PaginatedResponse[OrgUnitResponse]:
    """
    List archived/deleted org units employee_number

    Returns paginated list of archived org units.

    Required Permission: org_unit.view_deleted
    """
    items, pagination = await service.list_deleted_org_units(
        page=page,
        limit=limit,
        search=search,
    )
    return create_paginated_response(
        message="Retrieved deleted org units",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/{org_unit_id}", response_model=DataResponse[OrgUnitResponse])
@require_permission("org_unit.read")
async def get_org_unit(
    org_unit_id: int,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """Get organization unit by ID"""
    data = await service.get_org_unit(org_unit_id)
    return create_success_response(message="Org unit berhasil diambil", data=data)


@router.get("/by-code/{code}", response_model=DataResponse[OrgUnitResponse])
@require_permission("org_unit.read")
async def get_org_unit_by_code(
    code: str,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """Get organization unit by code"""
    data = await service.get_org_unit_by_code(code)
    return create_success_response(message="Org unit berhasil diambil", data=data)


@router.get("", response_model=PaginatedResponse[OrgUnitResponse])
@require_permission("org_unit.read")
async def list_org_units(
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    search: Optional[str] = None,
    parent_id: Optional[int] = None,
    type_filter: Optional[str] = None,
) -> PaginatedResponse[OrgUnitResponse]:
    """List organization units with pagination and filters"""
    items, pagination = await service.list_org_units(
        page, limit, search, parent_id, type_filter
    )
    return create_paginated_response(
        message="Daftar org unit berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/{org_unit_id}/children", response_model=PaginatedResponse[OrgUnitResponse]
)
@require_permission("org_unit.read")
async def get_org_unit_children(
    org_unit_id: int,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
) -> PaginatedResponse[OrgUnitResponse]:
    """Get children organization units with pagination"""
    items, pagination = await service.get_org_unit_children(org_unit_id, page, limit)
    return create_paginated_response(
        message="Children org unit berhasil diambil",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/{org_unit_id}/hierarchy", response_model=DataResponse[OrgUnitHierarchyResponse]
)
@require_permission("org_unit.read")
async def get_org_unit_hierarchy(
    org_unit_id: int,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitHierarchyResponse]:
    """Get organization unit hierarchy"""
    data = await service.get_org_unit_hierarchy(org_unit_id)
    return create_success_response(
        message="Hierarchy org unit berhasil diambil", data=data
    )


@router.get("/types/all", response_model=DataResponse[OrgUnitTypesResponse])
@require_permission("org_unit.read")
async def get_org_unit_types(
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitTypesResponse]:
    """
    Get all available org unit types

    Returns list of org unit types yang tersedia di sistem.
    """
    data = await service.get_org_unit_types()
    return create_success_response(message="Org unit types berhasil diambil", data=data)


@router.post("", response_model=DataResponse[OrgUnitResponse])
@require_role(["super_admin", "hr_admin"])
async def create_org_unit(
    request: OrgUnitCreateRequest,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """
    Create new org unit (Super Admin only)

    Hanya super_admin yang dapat membuat data unit organisasi master baru.
    Level dan path akan dihitung otomatis berdasarkan parent_id.
    """
    data = await service.create_org_unit(
        code=request.code,
        name=request.name,
        type=request.type,
        created_by=current_user.id,
        parent_id=request.parent_id,
        head_id=request.head_id,
        description=request.description,
    )
    return create_success_response(message="Org unit berhasil dibuat", data=data)


@router.post("/bulk-insert", response_model=DataResponse[BulkInsertResult])
@require_role(["super_admin", "hr_admin"])
async def bulk_insert_org_units(
    service: OrgUnitServiceDep,
    file: UploadFile = File(..., description="Excel file dengan sheet 'Department'"),
    skip_errors: bool = Form(False, description="Skip item yang error"),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BulkInsertResult]:
    """
    Bulk insert org units dari Excel

    Upload Excel file dengan sheet 'Department' yang berisi kolom:
    - Kode: Kode unit organisasi (wajib)
    - Nama: Nama unit (wajib)
    - Tipe: Tipe unit (wajib)
    - Head Departement: Kode parent department (opsional)
    - Head Email: Email kepala unit (opsional)
    - Deskripsi: Deskripsi unit (opsional)

    Required Permission: super_admin atau hr_admin
    """
    from app.modules.org_units.schemas.requests import OrgUnitBulkItem

    # Validate file type
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        return create_success_response(
            message="Invalid file type. Please upload an Excel file (.xlsx or .xls)",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": "Invalid file type"}],
                warnings=[],
                created_ids=[],
            ),
        )

    # Read file content
    file_content = await file.read()

    # Parse Excel
    try:
        parsed_data = ExcelParser.parse_org_units_sheet(
            file_content, sheet_name="Department"
        )
    except Exception as e:
        return create_success_response(
            message=f"Failed to parse Excel file: {str(e)}",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": f"Parse error: {str(e)}"}],
                warnings=[],
                created_ids=[],
            ),
        )

    # Convert to OrgUnitBulkItem
    bulk_items = []
    for item_data in parsed_data:
        try:
            bulk_item = OrgUnitBulkItem(**item_data)
            bulk_items.append(bulk_item)
        except Exception:
            # Skip invalid items but track them
            pass

    if not bulk_items:
        return create_success_response(
            message="No valid org units found in Excel file",
            data=BulkInsertResult(
                total_items=len(parsed_data),
                success_count=0,
                error_count=len(parsed_data),
                errors=[{"error": "No valid data found"}],
                warnings=[],
                created_ids=[],
            ),
        )

    # Call service to bulk insert
    result = await service.bulk_insert_org_units(
        items=bulk_items,
        created_by=current_user.id,
        skip_errors=skip_errors,
    )

    return create_success_response(
        message=f"Bulk insert completed: {result.success_count} sukses, {result.error_count} error",
        data=result,
    )


@router.put("/{org_unit_id}", response_model=DataResponse[OrgUnitResponse])
@require_role(["super_admin", "hr_admin"])
async def update_org_unit(
    org_unit_id: int,
    request: OrgUnitUpdateRequest,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """
    Update org unit (Super Admin only)

    Hanya super_admin yang dapat mengupdate data unit organisasi master.
    """
    update_data = request.model_dump(exclude_unset=True)
    data = await service.update_org_unit(
        org_unit_id=org_unit_id,
        updated_by=current_user.id,
        update_data=update_data,
    )
    return create_success_response(message="Org unit berhasil diupdate", data=data)


@router.delete(
    "/{org_unit_id}", response_model=DataResponse[OrgUnitResponse]
)
@require_permission("org_unit.soft_delete")
async def soft_delete_org_unit(
    org_unit_id: int,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """
    Soft delete (archive) org unit

    This operation:
    - Archives org unit in workforce service
    - Validates no active employees exist
    - Validates no child org units exist

    Required Permission: org_unit.soft_delete
    """
    data = await service.soft_delete_org_unit(
        org_unit_id=org_unit_id, deleted_by_user_id=current_user.id
    )
    return create_success_response(message="Org unit archived successfully", data=data)


@router.post("/{org_unit_id}/restore", response_model=DataResponse[OrgUnitResponse])
@require_permission("org_unit.restore")
async def restore_org_unit(
    org_unit_id: int,
    service: OrgUnitServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[OrgUnitResponse]:
    """
    Restore archived org unit

    This operation:
    - Restores org unit in workforce service
    - Validates parent is not deleted

    Required Permission: org_unit.restore
    """
    data = await service.restore_org_unit(org_unit_id=org_unit_id)
    return create_success_response(message="Org unit restored successfully", data=data)
