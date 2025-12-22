"""
Employee Router - API endpoints for Employee operations
"""

from fastapi import APIRouter, Query, Depends, status, UploadFile, File, Form
from typing import Optional, Dict, Any

from app.modules.employees.dependencies import EmployeeServiceDep
from app.modules.employees.schemas import (
    EmployeeCreateRequest,
    EmployeeUpdateRequest,
    EmployeeResponse,
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
) -> PaginatedResponse[EmployeeResponse]:
    items, pagination = await service.list(page, limit, search, org_unit_id, is_active)
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get("/deleted", response_model=PaginatedResponse[EmployeeResponse])
@require_permission("employee.view_deleted")
async def list_deleted_employees(
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
) -> PaginatedResponse[EmployeeResponse]:
    items, pagination = await service.list_deleted(page, limit, search)
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/org-unit/{org_unit_id}", response_model=PaginatedResponse[EmployeeResponse]
)
@require_permission("employee.read")
async def list_by_org_unit(
    org_unit_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    include_children: bool = Query(False),
) -> PaginatedResponse[EmployeeResponse]:
    items, pagination = await service.list_by_org_unit(
        org_unit_id, page, limit, include_children
    )
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )


@router.get(
    "/by-email/{email}", response_model=DataResponse[Optional[EmployeeResponse]]
)
@require_permission("employee.read")
async def get_by_email(
    email: str,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Optional[EmployeeResponse]]:
    data = await service.get_by_email(email)
    return create_success_response(
        message="Success" if data else "Not found", data=data
    )


@router.get(
    "/by-code/{code}", response_model=DataResponse[Optional[EmployeeResponse]]
)
@require_permission("employee.read")
async def get_by_code(
    code: str,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Optional[EmployeeResponse]]:
    data = await service.get_by_code(code)
    return create_success_response(
        message="Success" if data else "Not found", data=data
    )


@router.get("/{employee_id}", response_model=DataResponse[EmployeeResponse])
@require_permission("employee.read")
async def get_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    data = await service.get(employee_id)
    return create_success_response(message="Success", data=data)


@router.get(
    "/{employee_id}/subordinates", response_model=PaginatedResponse[EmployeeResponse]
)
@require_permission("employee.read")
async def list_subordinates(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=250),
    recursive: bool = Query(False),
) -> PaginatedResponse[EmployeeResponse]:
    items, pagination = await service.list_subordinates(
        employee_id, page, limit, recursive
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
    data = await service.create(
        code=request.code,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        created_by=current_user.id,
        org_unit_id=request.org_unit_id,
        phone=request.phone,
        position=request.position,
        site=request.site,
        employee_type=request.type,
        gender=request.gender,
        supervisor_id=request.supervisor_id,
    )

    return create_success_response(message="Created", data=data)


@router.patch("/{employee_id}", response_model=DataResponse[EmployeeResponse])
@require_role(["super_admin", "hr_admin"])
async def update_employee(
    employee_id: int,
    request: EmployeeUpdateRequest,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    update_data = request.model_dump(exclude_unset=True)
    data = await service.update(
        employee_id=employee_id,
        updated_by=current_user.id,
        update_data=update_data,
    )

    return create_success_response(message="Updated", data=data)


@router.delete("/{employee_id}", response_model=DataResponse[Dict[str, Any]])
@require_role(["super_admin", "hr_admin"])
async def delete_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[Dict[str, Any]]:
    result = await service.delete(employee_id, current_user.id)
    return create_success_response(message="Deleted", data=result)


@router.post("/{employee_id}/restore", response_model=DataResponse[EmployeeResponse])
@require_permission("employee.restore")
async def restore_employee(
    employee_id: int,
    service: EmployeeServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[EmployeeResponse]:
    data = await service.restore(employee_id)
    return create_success_response(message="Restored", data=data)


@router.post("/bulk-insert", response_model=DataResponse[BulkInsertResult])
@require_role(["super_admin", "hr_admin"])
async def bulk_insert_employees(
    service: EmployeeServiceDep,
    file: UploadFile = File(..., description="Excel file with 'Karyawan' sheet"),
    skip_errors: bool = Form(False),
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BulkInsertResult]:
    from app.modules.employees.schemas.requests import EmployeeBulkItem

    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        return create_success_response(
            message="Invalid file type",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": "Invalid file type"}],
                warnings=[],
                created_ids=[],
            ),
        )

    file_content = await file.read()

    try:
        parsed_data = ExcelParser.parse_employees_sheet(
            file_content, sheet_name="Karyawan"
        )
    except Exception as e:
        return create_success_response(
            message=f"Parse error: {e}",
            data=BulkInsertResult(
                total_items=0,
                success_count=0,
                error_count=1,
                errors=[{"error": str(e)}],
                warnings=[],
                created_ids=[],
            ),
        )

    bulk_items = []
    validation_errors = []

    for item_data in parsed_data:
        try:
            bulk_items.append(EmployeeBulkItem(**item_data))
        except Exception as e:
            validation_errors.append(
                {
                    "row_number": item_data.get("row_number", "?"),
                    "code": item_data.get("code", "?"),
                    "error": str(e),
                }
            )

    if not bulk_items:
        return create_success_response(
            message="No valid data",
            data=BulkInsertResult(
                total_items=len(parsed_data),
                success_count=0,
                error_count=len(parsed_data),
                errors=validation_errors or [{"error": "No valid data"}],
                warnings=[],
                created_ids=[],
            ),
        )

    success_count = 0
    error_count = 0
    created_ids = []
    errors = validation_errors.copy()
    warnings = []

    for item in bulk_items:
        try:
            result = await service.create(
                code=item.code,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                created_by=current_user.id,
                org_unit_id=item.org_unit_id,
                phone=item.phone,
                position=item.position,
                site=item.site,
                employee_type=item.type,
                gender=item.gender,
            )
            success_count += 1
            created_ids.append(result.id)

        except Exception as e:
            error_count += 1
            if skip_errors:
                errors.append({"code": item.code, "error": str(e)})
            else:
                raise

    return create_success_response(
        message=f"Bulk insert: {success_count} success, {error_count} errors",
        data=BulkInsertResult(
            total_items=len(bulk_items),
            success_count=success_count,
            error_count=error_count + len(validation_errors),
            errors=errors,
            warnings=warnings,
            created_ids=created_ids,
        ),
    )
