"""
Employee Routers - API endpoints for Employee operations

Profile data (name, email, phone, gender) comes from User (synced from SSO).
Employee endpoints focus on employment data.
"""

from fastapi import APIRouter, Query, Depends, status, UploadFile, File, Form
from typing import Optional, List, Dict, Any
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


# =========================================
# Employee Account Endpoints (with SSO)
# =========================================

@router.get("/with-account", response_model=PaginatedResponse[EmployeeAccountListItem])
@require_permission("employee.read")
async def list_employee_accounts(
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    search: Optional[str] = None,
    org_unit_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> PaginatedResponse[EmployeeAccountListItem]:
    """
    List employees with user profile data.
    
    Profile data (name, email) comes from linked User.
    """
    result = await service.list_employee_accounts(
        page=page,
        limit=limit,
        search=search,
        org_unit_id=org_unit_id,
        is_active=is_active,
    )
    return create_paginated_response(
        message="Success",
        data=result["items"],
        page=result["pagination"]["page"],
        limit=result["pagination"]["limit"],
        total_items=result["pagination"]["total_items"],
    )


@router.get("/{employee_id}/with-account", response_model=DataResponse[Dict[str, Any]])
@require_permission("employee.read")
async def get_employee_account(
    employee_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Dict[str, Any]]:
    """Get employee with user profile and SSO data."""
    data = await service.get_employee_account(employee_id=employee_id)
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
    """
    Create employee with SSO user account.
    
    Flow:
    1. Create SSO user (Master for profile)
    2. Create local User (sync from SSO response)
    3. Create Employee linked to User
    """
    data = await service.create_employee_with_account(
        number=request.number,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        org_unit_id=request.org_unit_id,
        created_by=current_user.id,
        phone=request.phone,
        position=request.position,
        employee_type=request.type,  # Schema uses 'type'
        gender=request.gender,
        supervisor_id=request.supervisor_id,
    )
    return create_success_response(message="Created", data=data)


@router.put(
    "/{employee_id}/with-account", 
    response_model=DataResponse[EmployeeAccountUpdateData]
)
@require_role(["super_admin", "hr_admin"])
async def update_employee_with_account(
    employee_id: int,
    request: UpdateEmployeeWithAccountRequest,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeAccountUpdateData]:
    """
    Update employee with sync to SSO.
    
    Profile updates (name, phone, gender) sync to SSO Master.
    Employment updates (position, type, org_unit) update Employee.
    """
    data = await service.update_employee_with_account(
        employee_id=employee_id,
        updated_by=current_user.id,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        gender=request.gender,
        position=request.position,
        employee_type=request.type,  # Schema uses 'type'
        org_unit_id=request.org_unit_id,
        supervisor_id=request.supervisor_id,
    )
    return create_success_response(message="Updated", data=data)


@router.delete(
    "/{employee_id}/with-account", 
    response_model=DataResponse[Dict[str, Any]]
)
@require_permission("employee.soft_delete")
async def delete_employee_account(
    employee_id: int,
    service: EmployeeAccountServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Dict[str, Any]]:
    """
    Soft delete employee and deactivate SSO user.
    
    This operation:
    - Deactivates SSO account
    - Reassigns subordinates
    - Soft deletes employee
    - Deactivates local user
    
    Note: Employee cannot be deleted if they are org unit head.
    """
    data = await service.delete_employee_account(
        employee_id=employee_id, 
        deleted_by=current_user.id
    )
    return create_success_response(message="Employee archived successfully", data=data)


# =========================================
# Basic Employee Endpoints
# =========================================

@router.get("/{employee_id}", response_model=DataResponse[EmployeeResponse])
@require_permission("employee.read")
async def get_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """Get employee by ID with user profile."""
    data = await service.get_employee(employee_id)
    return create_success_response(message="Success", data=data)


@router.get(
    "/by-email/{email}", 
    response_model=DataResponse[Optional[EmployeeResponse]]
)
@require_permission("employee.read")
async def get_employee_by_email(
    email: str,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Optional[EmployeeResponse]]:
    """Get employee by email (via User)."""
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
    """Get employee by employee number."""
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
    include_details: Optional[bool] = True,
) -> PaginatedResponse[EmployeeResponse]:
    """
    List employees with pagination and filters.
    
    Search searches by User.name, User.email, and Employee.number.
    """
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
    "/{employee_id}/subordinates", 
    response_model=PaginatedResponse[EmployeeResponse]
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
    """Get employee subordinates with pagination."""
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
    """Get employees by organization unit with pagination."""
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
    """
    Create new employee (requires existing user_id).
    
    For creating employee with SSO account, use POST /employees/with-account.
    """
    data = await service.create_employee(
        user_id=request.user_id,
        number=request.number,
        position=request.position,
        org_unit_id=request.org_unit_id,
        created_by=current_user.id,
        supervisor_id=request.supervisor_id,
        employee_type=request.type,
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
    """
    Update employee employment data.
    
    Profile updates (name, email, phone, gender) should use PATCH /employees/{id}/with-account.
    """
    data = await service.update_employee(
        employee_id=employee_id,
        updated_by=current_user.id,
        position=request.position,
        employee_type=request.type,
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
async def soft_delete_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """
    Soft delete employee.
    
    Subordinates are automatically reassigned to the employee's supervisor.
    Cannot delete if employee is org unit head.
    """
    data = await service.soft_delete_employee(
        employee_id=employee_id,
        deleted_by_user_id=current_user.id,
    )
    return create_success_response(message="Deleted", data=data)


@router.post("/{employee_id}/restore", response_model=DataResponse[EmployeeResponse])
@require_permission("employee.restore")
async def restore_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    """Restore soft-deleted employee."""
    data = await service.restore_employee(employee_id)
    return create_success_response(message="Restored", data=data)


@router.get("/deleted", response_model=PaginatedResponse[EmployeeResponse])
@require_permission("employee.view_deleted")
async def list_deleted_employees(
    service: EmployeeServiceDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[EmployeeResponse]:
    """List soft-deleted employees."""
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


# =========================================
# Bulk Operations
# =========================================

@router.post("/bulk-insert", response_model=DataResponse[BulkInsertResult])
@require_role(["super_admin", "hr_admin"])
async def bulk_insert_employees(
    service: EmployeeAccountServiceDep,
    file: UploadFile = File(..., description="Excel file dengan sheet 'Karyawan'"),
    skip_errors: bool = Form(False, description="Skip item yang error"),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BulkInsertResult]:
    """
    Bulk insert employees dari Excel.
    
    Upload Excel file dengan sheet 'Karyawan' yang berisi kolom:
    - Nomor: Nomor karyawan (wajib)
    - Nama Depan: Nama depan (wajib)
    - Nama Belakang: Nama belakang (wajib)
    - Email: Email karyawan (wajib)
    - Department: Kode unit organisasi (wajib)
    - Nomor HP: Nomor telepon (opsional)
    - Jabatan: Jabatan/Posisi (opsional)
    - Tipe: on_site, hybrid, atau ho (opsional)
    - Gender: male atau female (opsional)
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
    # Note: bulk_insert_employees method needs to be implemented in EmployeeAccountService
    result = BulkInsertResult(
        total_items=len(bulk_items),
        success_count=0,
        error_count=len(bulk_items),
        errors=[{"error": "Bulk insert not yet implemented for new schema"}],
        warnings=["Bulk insert requires migration to new schema first"],
        created_ids=[]
    )

    return create_success_response(
        message=f"Bulk insert completed: {result.success_count} sukses, {result.error_count} error",
        data=result
    )
