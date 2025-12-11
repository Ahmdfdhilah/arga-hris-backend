# PANDUAN IMPLEMENTASI BACKEND PYTHON (FASTAPI)

## PRINSIP UTAMA

### 1. BAHASA & DOKUMENTASI
- **SEMUA** error messages, docstrings, dan komentar dalam **Bahasa Indonesia**
- Tidak ada emoji dalam code
- Komentar hanya untuk logika kompleks, hindari komentar yang jelas dari code

### 2. VERIFIKASI DOKUMENTASI
- **WAJIB** cek dokumentasi resmi sebelum implementasi (FastAPI, SQLAlchemy, Pydantic, dll)
- Jangan mengandalkan asumsi, verifikasi syntax dan pattern dari docs
- Pastikan versi library yang digunakan sesuai dengan project

### 3. KONSISTENSI DENGAN EXISTING CODEBASE
- Selalu periksa `plans` atau dokumentasi arsitektur sebelum coding
- Ikuti pattern yang sudah ada di module lain
- Jika context hilang, tanyakan atau rujuk kembali ke dokumentasi project

---

## STRUKTUR MODULE

```
app/modules/{module_name}/
├── models/
│   └── {entity}.py              # SQLAlchemy models
├── schemas/
│   ├── requests.py              # Input schemas
│   ├── responses.py             # Output schemas
│   └── shared.py                # Shared schemas (opsional)
├── repositories/
│   └── {entity}_repository.py   # Database operations only
├── services/
│   └── {entity}_service.py      # Business logic + response building
└── routers/
    └── {entity}s.py             # API endpoints (nama plural)
```

---

## LAYER RESPONSIBILITIES

### MODELS (SQLAlchemy)
**Tanggung Jawab:** Definisi tabel database
```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
```

**Aturan:**
- Gunakan type hints yang tepat
- Definisikan relationships dengan jelas
- Tambahkan indexes untuk query optimization

---

### SCHEMAS (Pydantic)

#### `requests.py` - Input Validation
```python
class EmployeeCreateRequest(BaseModel):
    """Schema untuk membuat employee baru"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    
    class Config:
        from_attributes = True
```

#### `responses.py` - Output Format
```python
class EmployeeResponse(BaseModel):
    """Schema response employee"""
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Aturan:**
- Request schemas: validasi ketat, gunakan `Field()` dengan constraints
- Response schemas: include semua field yang akan dikembalikan
- Gunakan `Optional[]` untuk field yang bisa null
- Nested schemas untuk relasi atau JSON fields

---

### REPOSITORIES - Database Layer
**Tanggung Jawab:** HANYA operasi database, TIDAK ADA business logic

```python
class EmployeeRepository:
    """Repository untuk operasi database Employee"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Ambil employee berdasarkan ID"""
        result = await self.db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, employee: Employee) -> Employee:
        """Simpan employee baru ke database"""
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
```

**Aturan:**
- Method async dengan `AsyncSession`
- Return type yang jelas (model atau `Optional[Model]`)
- Commit & refresh untuk operasi write
- Tidak ada exception handling business logic

---

### SERVICES - Business Logic Layer
**Tanggung Jawab:** Business logic + validation + response building

```python
class EmployeeService:
    """Service untuk business logic Employee"""
    
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    async def create_employee(
        self,
        request: EmployeeCreateRequest
    ) -> Dict[str, Any]:
        """
        Membuat employee baru
        
        Args:
            request: Data employee yang akan dibuat
            
        Returns:
            Response sukses dengan data employee
            
        Raises:
            ConflictException: Jika email sudah terdaftar
        """
        # Validasi business rules
        existing = await self.employee_repo.get_by_email(request.email)
        if existing:
            raise ConflictException(
                f"Employee dengan email {request.email} sudah terdaftar"
            )
        
        # Proses data
        employee = Employee(**request.model_dump())
        created = await self.employee_repo.create(employee)
        
        # Build response
        response = EmployeeResponse.from_orm(created)
        return success_data_response(
            message="Employee berhasil dibuat",
            data=response.model_dump()
        )
```

**Aturan CRITICAL:**
- **Return type HARUS `Dict[str, Any]`** (bukan Pydantic model)
- **Response building di SERVICE, bukan di router**
- Dependency injection via `__init__`
- Semua validasi business logic di sini
- Exception dengan pesan Bahasa Indonesia
- Docstring lengkap dengan Args, Returns, Raises

---

### ROUTERS - API Endpoint Layer
**Tanggung Jawab:** Routing + dependency injection + permission check

```python
from app.core.security.rbac import require_permission

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_employee_service(
    db: AsyncSession = Depends(get_db)
) -> EmployeeService:
    """Dependency injection untuk EmployeeService"""
    repo = EmployeeRepository(db)
    return EmployeeService(repo)

@router.post("", status_code=201)
@require_permission("employee.create")
async def create_employee(
    request: EmployeeCreateRequest,
    service: EmployeeService = Depends(get_employee_service),
    current_user: Dict = Depends(get_current_user)
):
    """
    Membuat employee baru
    
    **Permission required:** employee.create
    """
    return await service.create_employee(request)
```

**Aturan:**
- **Langsung return hasil service** (jangan build response lagi)
- Semua endpoints WAJIB ada RBAC decorator
- Dependency injection untuk service
- Docstring dengan permission required
- Status code sesuai operation (201 untuk create)

---

## RESPONSE BUILDING

### Location: SERVICE LAYER (WAJIB)

```python
from app.core.schemas.helpers import success_data_response, paginated_data_response

# Single data
return success_data_response(
    message="Data berhasil diambil",
    data=response.model_dump()
)

# Paginated
return paginated_data_response(
    message="Daftar data berhasil diambil",
    data=items_data,
    page=page,
    limit=limit,
    total_items=total_items
)
```

**SALAH jika response building di router!**

---

## RBAC (ROLE-BASED ACCESS CONTROL)

### Permission Naming Convention
Format: `{resource}.{action}[_scope]`

```python
# Examples
'employee.read'           # Baca semua employee
'employee.read_own'       # Baca data sendiri
'employee.read_team'      # Baca data team
'attendance.create'       # Buat attendance
'leave_request.approve'   # Approve cuti
```

### Implementation

```python
# Permission-based (PREFERRED)
@require_permission("employee.read")
async def get_employee(...):
    pass

# Role-based (untuk super admin only)
@require_role("super_admin")
async def delete_employee(...):
    pass

# Multiple roles
@require_role(["hr_admin", "super_admin"])
async def system_config(...):
    pass
```

**Aturan:**
- **SEMUA endpoints WAJIB ada RBAC** (kecuali public)
- Prioritas gunakan `@require_permission`
- `@require_role` hanya untuk operasi super admin
- Dokumentasikan permission di docstring

---

## EXCEPTION HANDLING

### Available Exceptions
```python
from app.core.exceptions import (
    BadRequestException,      # 400 - Input tidak valid
    UnauthorizedException,    # 401 - Belum login
    ForbiddenException,       # 403 - Tidak punya akses
    NotFoundException,        # 404 - Data tidak ditemukan
    ConflictException,        # 409 - Duplikasi/konflik
    FileValidationError,      # 400 - File tidak valid
)
```

### Usage
```python
# Validation
if not value:
    raise BadRequestException("Field tidak boleh kosong")

# Not found
if not data:
    raise NotFoundException(f"Data dengan ID {id} tidak ditemukan")

# Conflict
if existing:
    raise ConflictException(f"Email {email} sudah terdaftar")
```

**WAJIB:** Semua pesan dalam Bahasa Indonesia

---

## FILE UPLOAD HANDLING

### Gunakan Utility Functions
```python
from app.core.utils import upload_file_to_gcp, delete_file_from_gcp_url

# Upload
file_url = await upload_file_to_gcp(
    file=uploaded_file,
    entity_type="employees",
    entity_id=employee.id,
    subfolder="profile",
    allowed_types=settings.ALLOWED_IMAGE_TYPES,
    max_size=settings.MAX_IMAGE_SIZE
)

# Delete
if old_file_url:
    delete_file_from_gcp_url(old_file_url)
```

**JANGAN** buat method `_upload_*` atau `_delete_*` custom!

---

## JSON FIELD OPERATIONS

### Increment Logic (BUKAN Replace)
```python
# BENAR - Increment
current_data = entity.metrics or {}
increment_value = request.weekly_inc

current_weekly = current_data.get("weekly_inc", 0.0)
current_data["weekly_inc"] = current_weekly + increment_value

current_total = current_data.get("total", 0.0)
current_data["total"] = current_total + increment_value

entity.metrics = current_data

# SALAH - Replace
entity.metrics = {"weekly_inc": request.weekly_inc}  #  Data lama hilang
```

---

## IMPORTS ORGANIZATION

```python
# 1. Standard library
from typing import Optional, Dict, Any, List
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local - models
from app.modules.employees.models import Employee

# 4. Local - repositories
from app.modules.employees.repositories import EmployeeRepository

# 5. Local - schemas
from app.modules.employees.schemas import (
    EmployeeCreateRequest,
    EmployeeResponse
)

# 6. Local - core
from app.core.schemas.helpers import success_data_response
from app.core.exceptions import NotFoundException
from app.core.security.rbac import require_permission
```

---

## VALIDATION PATTERNS

### Input Validation
```python
# Enum validation
if request.status not in ["active", "inactive"]:
    raise BadRequestException(
        "Status tidak valid. Harus 'active' atau 'inactive'"
    )

# Range validation
if page < 1:
    raise BadRequestException("Halaman harus lebih besar dari 0")

if limit < 1 or limit > 100:
    raise BadRequestException("Limit harus antara 1 dan 100")

# Existence check
existing = await self.repo.get_by_field(value)
if existing:
    raise ConflictException(f"Data dengan {field} sudah ada")
```

---

## CHECKLIST SEBELUM COMMIT

**Struktur:**
- [ ] Folder structure sesuai standard
- [ ] Schemas terpisah: requests.py & responses.py
- [ ] Imports terorganisir dengan benar

**Service Layer:**
- [ ] Dependency injection via `__init__`
- [ ] Return type `Dict[str, Any]`
- [ ] Response building di SERVICE (bukan router)
- [ ] Validasi business logic lengkap
- [ ] Docstring lengkap (Args, Returns, Raises)

**Router Layer:**
- [ ] Langsung return hasil service
- [ ] SEMUA endpoints punya RBAC decorator
- [ ] Permission documented di docstring
- [ ] Dependency injection untuk service

**RBAC:**
- [ ] Permission naming sesuai convention
- [ ] Gunakan `@require_permission` untuk regular ops
- [ ] `@require_role` hanya untuk super admin ops

**Kualitas Code:**
- [ ] Tidak ada emoji
- [ ] Semua pesan dalam Bahasa Indonesia
- [ ] Tidak ada komentar yang tidak perlu
- [ ] File upload gunakan utility functions
- [ ] Exception handling proper

**Testing:**
- [ ] Test create, read, update operations
- [ ] Test validation errors
- [ ] Test RBAC restrictions
- [ ] Test edge cases

---

## ANTI-PATTERNS (JANGAN LAKUKAN!)

 **Response building di router**
```python
# SALAH
@router.get("/")
async def list_items(service: ServiceDep):
    items = await service.list_items()
    return success_data_response("Success", items)  # 
```

 **Response building di service**
```python
# BENAR
async def list_items(self) -> Dict[str, Any]:
    items = await self.repo.list_all()
    return success_data_response("Success", items)  # 
```

---

 **Service return Pydantic model**
```python
# SALAH
async def get_item(self) -> ItemResponse:  # 
    return ItemResponse.from_orm(item)
```

 **Service return Dict[str, Any]**
```python
# BENAR
async def get_item(self) -> Dict[str, Any]:  # 
    response = ItemResponse.from_orm(item)
    return success_data_response("Success", response.model_dump())
```

---

 **Business logic di repository**
```python
# SALAH - Repository
async def create(self, data: dict) -> Employee:
    if data["age"] < 18:  #  Business logic di repo
        raise BadRequestException("Umur minimal 18")
    # ...
```

 **Business logic di service**
```python
# BENAR - Service
async def create_employee(self, request: CreateRequest):
    if request.age < 18:  #  Business logic di service
        raise BadRequestException("Umur minimal 18")
    # ...
```

---

 **Endpoint tanpa RBAC**
```python
# SALAH
@router.get("/")
async def list_items(...):  #  Tidak ada RBAC
    pass
```

 **Semua endpoint dengan RBAC**
```python
# BENAR
@router.get("/")
@require_permission("item.read")  # 
async def list_items(...):
    pass
```

---

## REFERENSI CEPAT

### Common Patterns
- **Pagination:** `page` (start from 1), `limit`, `total_items`
- **Filtering:** Optional parameters di repository & service
- **Sorting:** `order_by`, `order_direction` ("asc"/"desc")
- **Search:** `search` parameter, gunakan `ilike` untuk case-insensitive

### Response Format
```python
# Success
{
    "status": "success",
    "message": "...",
    "data": {...}
}

# Paginated
{
    "status": "success",
    "message": "...",
    "data": [...],
    "meta": {
        "page": 1,
        "limit": 10,
        "total_items": 100,
        "total_pages": 10
    }
}
```

---

**Dokumen ini adalah single source of truth untuk implementasi backend.**  
**Jika ragu, rujuk dokumen ini atau tanyakan sebelum implementasi.**