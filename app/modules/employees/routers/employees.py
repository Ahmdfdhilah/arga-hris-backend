from fastapi import APIRouter, Query, Depends, status, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
from app.modules.employees.dependencies import (
    EmployeeServiceDep,
    EmployeeAccountServiceDep,
)
from app.modules.employees.schemas import (
    EmployeeCreateRequest,
    EmployeeUpdateRequest,
    CreateEmployeeWithAccountRequest,
    UpdateEmployeeWithAccountRequest,
    EmployeeResponse,
    EmployeeAccountData,
    EmployeeAccountUpdateData,
    EmployeeAccountListItem,
    BulkInsertResult,
)
from app.core.utils import ExcelParser
from app.core.schemas import (
    CurrentUser,
    DataResponse,
    PaginatedResponse,
    create_success_response,
    create_paginated_response,
)
from app.core.security.rbac import require_permission, require_role
from app.core.dependencies.auth import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/deleted", response_model=PaginatedResponse[EmployeeAccountListItem])
@require_permission("employee.view_deleted")
async def list_deleted_employees(
    service: EmployeeAccountServiceDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[EmployeeAccountListItem]:
    """
    List archived/deleted employees employee_number

    Returns paginated list of archived employees with their account details.

    Required Permission: employee.view_deleted
    """
    items, pagination = await service.list_deleted_employees(
        page=page,
        limit=limit,
        search=search,
    )
    return create_paginated_response(
        message="Retrieved deleted employees",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/with-account", response_model=PaginatedResponse[EmployeeAccountListItem])
@require_permission("employee.read")
async def list_employees_with_account(
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    search: Optional[str] = None,
    org_unit_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    account_type: Optional[str] = Query(
        None, description="Filter: 'regular' or 'guest'"
    ),
) -> PaginatedResponse[EmployeeAccountListItem]:
    """List employees with account (paginated)"""
    items, pagination = await service.list_employees_with_account(
        page=page,
        limit=limit,
        search=search,
        org_unit_id=org_unit_id,
        is_active=is_active,
        account_type=account_type,
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/{user_id}/with-account", response_model=DataResponse[EmployeeAccountListItem]
)
@require_permission("employee.read")
async def get_employee_with_account(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountListItem]:
    """Get employee with account by user_id"""
    data = await service.get_employee_with_account(user_id=user_id)
    return create_success_response(message="Success", data=data)


@router.post(
    "/with-account",
    response_model=DataResponse[EmployeeAccountData],
    status_code=status.HTTP_201_CREATED,
)
@require_role(["super_admin", "hr_admin"])
async def create_employee_with_account(
    request: CreateEmployeeWithAccountRequest,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountData]:
    """Create employee with account"""
    valid_from = (
        datetime.fromisoformat(request.valid_from.replace("Z", "+00:00"))
        if request.valid_from
        else None
    )
    valid_until = (
        datetime.fromisoformat(request.valid_until.replace("Z", "+00:00"))
        if request.valid_until
        else None
    )

    data = await service.create_employee_with_account(
        number=request.number,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        org_unit_id=request.org_unit_id,
        created_by=current_user.id,
        account_type=request.account_type,
        phone=request.phone,
        position=request.position,
        employee_type=request.employee_type,
        employee_gender=request.employee_gender,
        supervisor_id=request.supervisor_id,
        guest_type=request.guest_type,
        valid_from=valid_from,
        valid_until=valid_until,
        sponsor_id=request.sponsor_id,
        notes=request.notes,
    )
    return create_success_response(message="Created", data=data)


@router.post("/bulk-insert", response_model=DataResponse[BulkInsertResult])
@require_role(["super_admin", "hr_admin"])
async def bulk_insert_employees(
    service: EmployeeAccountServiceDep,
    file: UploadFile = File(..., description="Excel file dengan sheet 'Karyawan'"),
    skip_errors: bool = Form(False, description="Skip item yang error"),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BulkInsertResult]:
    """
    Bulk insert employees dari Excel

    Upload Excel file dengan sheet 'Karyawan' yang berisi kolom:
    - Nomor: Nomor karyawan (wajib)
    - Nama Depan: Nama depan (wajib)
    - Nama Belakang: Nama belakang (wajib)
    - Email: Email karyawan (wajib)
    - Department: Kode unit organisasi (wajib)
    - Nomor HP: Nomor telepon (opsional)
    - Jabatan: Jabatan/Posisi (opsional)
    - Tipe Karyawan: on_site atau hybrid (opsional)
    - Jenis Karyawan: user, guest, atau none (opsional, default: user)
    - Gender: male atau female (opsional)
    - Awal Kontrak: Tanggal mulai (ISO format, opsional)
    - Selesai Kontrak: Tanggal akhir (ISO format, opsional)
    - Catatan: Catatan (opsional)

    Required Permission: super_admin atau hr_admin
    """
    from app.modules.employees.schemas.requests import EmployeeBulkItem

    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        return create_success_response(
            message="Invalid file type. Please upload an Excel file (.xlsx or .xls)",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": "Invalid file type"}],
                warnings=[],
                created_ids=[]
            )
        )

    # Read file content
    file_content = await file.read()

    # Parse Excel
    try:
        parsed_data = ExcelParser.parse_employees_sheet(file_content, sheet_name="Karyawan")
    except Exception as e:
        return create_success_response(
            message=f"Failed to parse Excel file: {str(e)}",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": f"Parse error: {str(e)}"}],
                warnings=[],
                created_ids=[]
            )
        )

    # Convert to EmployeeBulkItem
    bulk_items = []
    validation_errors = []
    for item_data in parsed_data:
        try:
            bulk_item = EmployeeBulkItem(**item_data)
            bulk_items.append(bulk_item)
        except Exception as e:
            # Collect validation errors
            validation_errors.append({
                "row_number": item_data.get("row_number", "unknown"),
                "number": item_data.get("number", "unknown"),
                "error": str(e)
            })


    if not bulk_items:
        return create_success_response(
            message="No valid employees found in Excel file",
            data=BulkInsertResult(
                total_items=len(parsed_data),
                success_count=0,
                error_count=len(parsed_data),
                errors=validation_errors if validation_errors else [{"error": "No valid data found"}],
                warnings=[],
                created_ids=[]
            )
        )

    # Call service to bulk insert
    result = await service.bulk_insert_employees(
        items=bulk_items,
        created_by=current_user.id,
        skip_errors=skip_errors,
    )

    return create_success_response(
        message=f"Bulk insert completed: {result.success_count} sukses, {result.error_count} error",
        data=result
    )


@router.put(
    "/{user_id}/with-account", response_model=DataResponse[EmployeeAccountUpdateData]
)
@require_role(["super_admin", "hr_admin"])
async def update_employee_with_account(
    user_id: int,
    request: UpdateEmployeeWithAccountRequest,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountUpdateData]:
    """Update employee with account"""
    valid_from = (
        datetime.fromisoformat(request.valid_from.replace("Z", "+00:00"))
        if request.valid_from
        else None
    )
    valid_until = (
        datetime.fromisoformat(request.valid_until.replace("Z", "+00:00"))
        if request.valid_until
        else None
    )

    data = await service.update_employee_with_account(
        user_id=user_id,
        updated_by=current_user.id,
        first_name=request.first_name,
        last_name=request.last_name,
        org_unit_id=request.org_unit_id,
        number=request.number,
        phone=request.phone,
        position=request.position,
        employee_type=request.employee_type,
        employee_gender=request.employee_gender,
        supervisor_id=request.supervisor_id,
        valid_from=valid_from,
        valid_until=valid_until,
        guest_type=request.guest_type,
        notes=request.notes,
        sponsor_id=request.sponsor_id,
    )
    return create_success_response(message="Updated", data=data)


@router.get("/{employee_id}", response_model=DataResponse[EmployeeResponse])
@require_permission("employee.read")
async def get_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """Get employee by ID"""
    data = await service.get_employee(employee_id)
    return create_success_response(message="Success", data=data)


@router.get(
    "/by-email/{email}", response_model=DataResponse[Optional[EmployeeResponse]]
)
@require_permission("employee.read")
async def get_employee_by_email(
    email: str,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Optional[EmployeeResponse]]:
    """Get employee by email"""
    data = await service.get_employee_by_email(email)
    return create_success_response(
        message="Success" if data else "Not found", data=data
    )


@router.get(
    "/by-number/{employee_number}",
    response_model=DataResponse[Optional[EmployeeResponse]],
)
@require_permission("employee.read")
async def get_employee_by_number(
    employee_number: str,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Optional[EmployeeResponse]]:
    """Get employee by employee number"""
    data = await service.get_employee_by_number(employee_number)
    return create_success_response(
        message="Success" if data else "Not found", data=data
    )


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
@require_permission("employee.read")
async def list_employees(
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    search: Optional[str] = None,
    org_unit_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    include_details: Optional[bool] = None,
) -> PaginatedResponse[EmployeeResponse]:
    """List employees with pagination and filters"""
    items, pagination = await service.list_employees(
        page, limit, search, org_unit_id, is_active, include_details
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/{employee_id}/subordinates", response_model=PaginatedResponse[EmployeeResponse]
)
@require_permission("employee.read")
async def get_employee_subordinates(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    recursive: bool = Query(False),
) -> PaginatedResponse[EmployeeResponse]:
    """Get employee subordinates with pagination"""
    items, pagination = await service.get_employee_subordinates(
        employee_id, page, limit, recursive
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/org-unit/{org_unit_id}/employees",
    response_model=PaginatedResponse[EmployeeResponse],
)
@require_permission("employee.read")
async def get_employees_by_org_unit(
    org_unit_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    include_children: bool = Query(False),
) -> PaginatedResponse[EmployeeResponse]:
    """Get employees by organization unit with pagination"""
    items, pagination = await service.get_employees_by_org_unit(
        org_unit_id, page, limit, include_children
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.post(
    "",
    response_model=DataResponse[EmployeeResponse],
    status_code=status.HTTP_201_CREATED,
)
@require_role(["super_admin", "hr_admin"])
async def create_employee(
    request: EmployeeCreateRequest,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """Create new employee"""
    full_name = f"{request.first_name} {request.last_name}"

    data = await service.create_employee(
        number=request.number,
        name=full_name,
        email=request.email,
        phone=request.phone or "",
        position=request.position or "",
        employee_type=request.employee_type,
        employee_gender=request.employee_gender,
        org_unit_id=request.org_unit_id,
        created_by=current_user.id,
        supervisor_id=request.supervisor_id,
    )
    return create_success_response(message="Created", data=data)


@router.put("/{employee_id}", response_model=DataResponse[EmployeeResponse])
@require_role(["super_admin", "hr_admin"])
async def update_employee(
    employee_id: int,
    request: EmployeeUpdateRequest,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """Update employee"""
    full_name = None
    if request.first_name and request.last_name:
        full_name = f"{request.first_name} {request.last_name}"
    elif request.first_name:
        employee = await service.get_employee(employee_id)
        existing_name = employee.name
        parts = existing_name.split(" ", 1)
        last_name = parts[1] if len(parts) > 1 else ""
        full_name = f"{request.first_name} {last_name}"
    elif request.last_name:
        employee = await service.get_employee(employee_id)
        existing_name = employee.name
        parts = existing_name.split(" ", 1)
        first_name = parts[0] if len(parts) > 0 else ""
        full_name = f"{first_name} {request.last_name}"

    data = await service.update_employee(
        employee_id=employee_id,
        updated_by=current_user.id,
        name=full_name,
        email=None,
        phone=request.phone,
        position=request.position,
        employee_type=request.employee_type,
        employee_gender=request.employee_gender,
        org_unit_id=request.org_unit_id,
        supervisor_id=request.supervisor_id,
        is_active=request.is_active,
    )
    return create_success_response(message="Updated", data=data)


@router.delete(
    "/{employee_id}",
    response_model=DataResponse[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
@require_role(["super_admin", "hr_admin"])
async def deactivate_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """
    Deactivate employee (Super Admin / HR Admin) - Soft Delete

    Hanya super_admin atau hr_admin yang dapat menonaktifkan karyawan.
    Ini adalah soft delete, data tidak dihapus dari database.
    """
    data = await service.update_employee(
        employee_id=employee_id,
        updated_by=current_user.id,
        name=None,
        email=None,
        phone=None,
        position=None,
        employee_type=None,
        employee_gender=None,
        org_unit_id=None,
        supervisor_id=None,
        is_active=False,
    )
    return create_success_response(message="Deactivated", data=data)


@router.post("/{user_id}/activate", response_model=DataResponse[List[str]])
@require_role(["super_admin", "hr_admin"])
async def activate_employee_account(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[str]]:
    """Activate employee account"""
    warnings = await service.activate_employee_account(
        user_id=user_id, updated_by=current_user.id
    )
    return create_success_response(message="Activated", data=warnings)


@router.post("/{user_id}/deactivate", response_model=DataResponse[List[str]])
@require_role(["super_admin", "hr_admin"])
async def deactivate_employee_account(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[str]]:
    """Deactivate employee account"""
    warnings = await service.deactivate_employee_account(
        user_id=user_id, updated_by=current_user.id
    )
    return create_success_response(message="Deactivated", data=warnings)


@router.post("/{user_id}/sync-to-sso", response_model=DataResponse[List[str]])
@require_role(["super_admin", "hr_admin"])
async def sync_user_to_sso(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[str]]:
    """Manual sync user to SSO"""
    warnings = await service.sync_user_to_sso(user_id=user_id)
    return create_success_response(message="Synced to SSO", data=warnings)


@router.delete(
    "/{user_id}/soft-delete", response_model=DataResponse[EmployeeAccountData]
)
@require_permission("employee.soft_delete")
async def soft_delete_employee_account(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountData]:
    """
    Soft delete (archive) employee account

    This operation:
    - Archives employee in workforce service (auto-reassigns subordinates)
    - Deactivates user in HRIS
    - Deactivates SSO account (fire-and-forget)

    Note: Employee cannot be archived if they are org unit head.
    Reassign org unit head first before archiving.

    Required Permission: employee.soft_delete
    """
    data = await service.soft_delete_employee_account(
        user_id=user_id, deleted_by_user_id=current_user.id
    )
    return create_success_response(message="Employee archived successfully", data=data)


@router.post("/{user_id}/restore", response_model=DataResponse[EmployeeAccountData])
@require_permission("employee.restore")
async def restore_employee_account(
    user_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountData]:
    """
    Restore archived employee account

    This operation:
    - Restores employee in workforce service
    - Activates user in HRIS
    - Activates SSO account (fire-and-forget)

    Required Permission: employee.restore
    """
    data = await service.restore_employee_account(user_id=user_id)
    return create_success_response(message="Employee restored successfully", data=data)
