# Type-Safe Schemas Architecture

## Overview

Semua response schemas menggunakan **Generic Types** untuk type safety penuh.

## Core Schemas

### 1. DataResponse[T]
Untuk single data response:
```python
from app.core.schemas import DataResponse, create_success_response

# Service
async def get_employee(id: int) -> EmployeeResponse:
    employee = await db.get(id)
    return EmployeeResponse.model_validate(employee)

# Router
@router.get("/{id}", response_model=DataResponse[EmployeeResponse])
async def get_employee(id: int) -> DataResponse[EmployeeResponse]:
    data = await service.get_employee(id)
    return create_success_response(message="Success", data=data)
```

Response:
```json
{
  "error": false,
  "message": "Success",
  "timestamp": "2025-11-23T10:00:00Z",
  "data": {
    "id": 1,
    "name": "John Doe"
  }
}
```

### 2. PaginatedResponse[T]
Untuk paginated list:
```python
from app.core.schemas import PaginatedResponse, create_paginated_response

# Service
async def list_employees(...) -> tuple[List[EmployeeResponse], dict]:
    items = [...]
    pagination = {"page": 1, "limit": 10, "total_items": 100}
    return items, pagination

# Router
@router.get("", response_model=PaginatedResponse[EmployeeResponse])
async def list_employees(...) -> PaginatedResponse[EmployeeResponse]:
    items, pagination = await service.list_employees(...)
    return create_paginated_response(
        message="Success",
        data=items,
        page=pagination["page"],
        limit=pagination["limit"],
        total_items=pagination["total_items"],
    )
```

Response:
```json
{
  "error": false,
  "message": "Success",
  "timestamp": "2025-11-23T10:00:00Z",
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total_items": 100,
    "total_pages": 10,
    "has_prev_page": false,
    "has_next_page": true
  }
}
```

## Module Schemas

### Employee Module

**Responses:**
- `EmployeeResponse` - Single employee data
- `EmployeeAccountData` - Employee + User + Guest (for create)
- `EmployeeAccountUpdateData` - Update response dengan updated_fields
- `EmployeeAccountListItem` - Item dalam list (Employee + User + Guest)
- `UserNestedResponse` - Nested user data
- `GuestAccountNestedResponse` - Nested guest data

**Pattern:**
```python
# Service returns typed data
async def create_employee(...) -> EmployeeAccountData:
    return EmployeeAccountData(
        employee=EmployeeResponse(...),
        user=UserNestedResponse.model_validate(user),
        guest_account=GuestAccountNestedResponse(...) if guest else None,
        warnings=[],
    )

# Router wraps dengan DataResponse
@router.post("", response_model=DataResponse[EmployeeAccountData])
async def create(...) -> DataResponse[EmployeeAccountData]:
    data = await service.create_employee(...)
    return create_success_response(message="Created", data=data)
```

---


## Benefits

✅ **Type Safety** - Compiler detects errors before runtime
✅ **IDE Autocomplete** - Full autocomplete untuk semua fields
✅ **Better OpenAPI** - Schema documentation otomatis lebih detail
✅ **Maintainable** - Refactor lebih mudah dengan type checking
✅ **Consistent** - Semua endpoints pakai format yang sama

## Migration dari Dict

**Before (Dict-based):**
```python
# Service
from app.core.schemas.helpers import success_data_response

async def get_employee(id: int) -> Dict[str, Any]:
    employee = await db.get(id)
    return success_data_response(
        message="Success",
        data={"id": employee.id, "name": employee.name}
    )

# Router
@router.get("/{id}", response_model=dict)  # ❌ No type safety
async def get_employee(id: int):
    return await service.get_employee(id)
```

**After (Typed):**
```python
# Service
async def get_employee(id: int) -> EmployeeResponse:
    employee = await db.get(id)
    return EmployeeResponse.model_validate(employee)

# Router
@router.get("/{id}", response_model=DataResponse[EmployeeResponse])
async def get_employee(id: int) -> DataResponse[EmployeeResponse]:
    data = await service.get_employee(id)
    return create_success_response(message="Success", data=data)
```

## Rules

1. **Service** returns typed data (Pydantic models), bukan dict
2. **Router** wraps service data dengan `create_success_response()` atau `create_paginated_response()`
3. **Schemas** harus define untuk semua response types
4. **No Dict[str, Any]** - semua harus typed
5. **No deprecated helpers** - pakai `create_*_response()`, bukan `success_data_response()`
