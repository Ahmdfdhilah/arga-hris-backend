# PANDUAN IMPLEMENTASI BACKEND (MERGED) - SINGLE SOURCE OF TRUTH

## PRINSIP UTAMA
1.  **BAHASA**: Komentar & Error Message WAJIB Bahasa Indonesia.
2.  **KONSISTENSI**: Ikuti pattern yang ada. Jangan "kreatif" sendiri.
3.  **VERIFIKASI**: Cek dokumentasi resmi library sebelum asumsi.
4.  **CHECKLIST**: Wajib self-check sebelum coding.

---

## 1. PROJECT STRUCTURE

```bash
arga-hris-backend/
├── app/
│   ├── main.py                         # Entry point (CLEAN - lihat section 1.1)
│   ├── config/settings.py              # Env vars
│   ├── core/                           # Shared Logic
│   │   ├── exceptions/                 # Custom Exceptions semua error raise ambil dari sini
│   │   ├── schemas/                    # BaseResponses semua response ambil dari sini
│   │   ├── security/                   # RBAC & Auth
│   │   ├── routers/                    # Router configuration
│   │   │   ├── system.py              # Health check & root endpoints
│   │   │   ├── routers.py             # Router registration setup
│   │   │   └── __init__.py            # Export setup_routers
│   │   ├── utils/                      # Global Helpers per use case agar atomic
│   │   │   ├── lifespan.py            # Application lifespan management
│   │   │   └── ...                    # Other utilities
│   │   └── enums/                      # Global Enums per use case agar atomic
│   │
│   ├── middleware/                     # Middleware & Exception Handlers
│   │   ├── setup.py                   # Centralized middleware setup
│   │   ├── cors.py                    # CORS configuration
│   │   ├── logging.py                 # Request logging middleware
│   │   ├── error_handler.py           # Exception handlers
│   │   └── __init__.py                # Export setup_middleware
│   │
│   └── modules/{module_name}/          # Domain Modules
│       ├── models/                     # SQLAlchemy Models
│       ├── schemas/                    # Pydantic DTOs
│       │   ├── commands/               # Write Ops
│       │   └── queries/                # Read Ops
│       ├── use_cases/                  # Pure Business Logic (Atomic per usecase)
│       ├── services/                   # Facade / Wrappers
│       ├── utils/                      # Module-specific helpers
│       ├── dependencies.py             # DI Definitions
│       └── routers/                    # API Endpoints
└── docs/RULES.MD                       # THIS FILE
```

### 1.1 CLEAN MAIN.PY PATTERN (WAJIB)

**PRINSIP**: `main.py` harus BERSIH dan RINGKAS (<50 baris), hanya orchestration.

**Struktur Wajib**:

```python
"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from app.config.settings import settings
from app.core.utils.logging import setup_logging
from app.core.utils.lifespan import lifespan
from app.middleware import setup_middleware
from app.core.routers import setup_routers

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ARGA HRIS Service",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Setup middleware and exception handlers
setup_middleware(app)

# Setup routers
setup_routers(app)
```

**Rules**:
1. **TIDAK BOLEH** ada logic bisnis atau konfigurasi detail di `main.py`
2. **WAJIB** pisahkan lifespan ke `app/core/utils/lifespan.py`
3. **WAJIB** pisahkan middleware setup ke `app/middleware/setup.py`
4. **WAJIB** pisahkan router registration ke `app/core/routers/routers.py`
5. Health check & root endpoint HARUS di `app/core/routers/system.py`

**File Organization**:
- `app/core/utils/lifespan.py`: Startup/shutdown events (scheduler, gRPC, RabbitMQ)
- `app/middleware/setup.py`: CORS, logging, exception handlers registration
- `app/core/routers/routers.py`: All router includes with prefixes and tags
- `app/core/routers/system.py`: Root (/) dan health check (/health) endpoints

---

## 2. LAYER RESPONSIBILITIES (STRICT)

### A. MODELS (`models/*.py`)
*   **Role**: Definisi Tabel Database (SQLAlchemy).
*   **Rule**: Type hints wajb. Relationships harus jelas.

### B. REPOSITORIES (`repositories/*`)
*   **Role**: Akses Database SAJA (No Business Logic).
*   **Structure**:
    *   `queries/`: Read operations (`get`, `list`, `count`). Return `Optional[Model]` atau `List[Model]`.
    *   `commands/`: Write operations (`create`, `update`, `delete`). Commit & Refresh di sini.
*   **Naming**: `UserQueries`, `UserCommands`.

### C. USE CASES (`use_cases/*.py`)
*   **Role**: **PURE BUSINESS LOGIC**. Enkapsulasi SATU proses bisnis.
*   **Rules**:
    *   **NO HTTP**: Tidak boleh import `fastapi`.
    *   **NO DB**: Akses DB hanya via Repository.
    *   **Atomic**: 1 File = 1 Use Case = 1 Public Method (`execute`).
    *   **Input/Output**: DTO (Pydantic Schema) atau Entity.
    *   **CLEAN**: Use Case hanya berisi orchestration. Helper logic pindah ke `utils/`.
    *   **NO PRIVATE METHODS**: Jangan buat `_helper_method()` di Use Case. Pindahkan ke Utils.
*   **Example**: `app/modules/employees/use_cases/create_employee.py`

```python
class CreateEmployeeUseCase:
    def __init__(self, repo: EmployeeCommands):
        self.repo = repo

    async def execute(self, data: CreateEmployeeDTO) -> Employee:
        if data.age < 17:
             raise BadRequestException("Belum cukup umur")
        return await self.repo.create(data)
```

### C.1 UTILS (`utils/*.py`) - DRY PATTERN (WAJIB)

**PRINSIP**: Ekstrak helper methods dari Use Cases ke Utils agar reusable.

**Struktur Utils Per Module**:
```
app/modules/{module_name}/utils/
├── __init__.py          # Export semua util classes
├── events.py            # EventUtil: publish domain events
├── validators.py        # ValidationUtil: business validations
└── {domain}_helper.py   # Specific helpers (e.g., path_calculator.py)
```

**Pattern**:
```python
# utils/events.py
class OrgUnitEventUtil:
    @staticmethod
    def to_event_data(org_unit: OrgUnit) -> Dict[str, Any]:
        return {"id": org_unit.id, "name": org_unit.name, ...}
    
    @staticmethod
    async def publish(event_publisher, event_type: str, org_unit: OrgUnit) -> None:
        if not event_publisher:
            return
        data = OrgUnitEventUtil.to_event_data(org_unit)
        await event_publisher.publish_org_unit_updated(org_unit.id, data)
```

**Use Case SEBELUM (❌ SALAH)**:
```python
class UpdateOrgUnitUseCase:
    async def execute(self, ...):
        # ... logic
        await self._recalculate_path(org_unit)
        await self._handle_head_change(...)
        await self._publish_event("updated", org_unit)
    
    async def _recalculate_path(self, org_unit):  # ❌ Private method
        ...
    async def _handle_head_change(self, ...):     # ❌ Private method
        ...
    async def _publish_event(self, ...):          # ❌ Private method
        ...
```

**Use Case SESUDAH (✅ BENAR)**:
```python
from app.modules.org_units.utils import OrgUnitPathUtil, OrgUnitHeadUtil, OrgUnitEventUtil

class UpdateOrgUnitUseCase:
    async def execute(self, ...):
        # ... validation & field updates
        await self.commands.update(org_unit)
        
        if parent_changed:
            await OrgUnitPathUtil.recalculate_path(self.queries, self.commands, org_unit)
        
        if head_changed:
            await OrgUnitHeadUtil.handle_head_change(...)
        
        await OrgUnitEventUtil.publish(self.event_publisher, "updated", org_unit)
        return org_unit
```

**Benefits**:
- ✅ Use Case tetap clean (~50% lebih sedikit lines)
- ✅ Utils bisa dipakai di Use Case lain
- ✅ Easier to test (utils bisa di-unit test terpisah)
- ✅ DRY - tidak ada duplikasi code

### D. SERVICES / FACADE (`services/*.py`)
*   **Role**: **ORCHESTRATOR / WRAPPER**.
*   **Rules**:
    *   Hanya me-wire repository ke Use Cases.
    *   Convert Request -> DTO -> UseCase -> DTO -> Response.
    *   Menangani Formatting Response (Standard Response Wrapper).
*   **Naming**: `{Entity}Service` (e.g., `EmployeeService`).

```python
class EmployeeService:
    def __init__(self, queries, commands):
        self.create_uc = CreateEmployeeUseCase(commands)
    
    async def create(self, request: CreateRequest) -> DataResponse:
        dto = request.to_dto()
        result = await self.create_uc.execute(dto)
        return success_data_response(data=result)
```

### E. ROUTERS (`routers/*.py`)
*   **Role**: HTTP Gatekeeper.
*   **Rules**:
    *   **RBAC**: Wajib `@require_permission`.
    *   **DI**: Inject Service Facade.
    *   **No Logic**: Dilarang ada logic `if/else` bisnis di sini.
    *   Return hasil dari Service langsung.

**Router Declaration Format (WAJIB KONSISTEN)**:

```python
# Format WAJIB untuk setiap router file
router = APIRouter(prefix="/module-name", tags=["Module Display Name"])
```

**Contoh yang benar**:

| Module | Declaration |
|--------|-------------|
| auth | `APIRouter(prefix="/auth", tags=["Authentication"])` |
| employees | `APIRouter(prefix="/employees", tags=["Employees"])` |
| attendances | `APIRouter(prefix="/attendances", tags=["Attendances"])` |
| leave-requests | `APIRouter(prefix="/leave-requests", tags=["Leave Requests"])` |
| org-units | `APIRouter(prefix="/org-units", tags=["Organization Units"])` |
| assignments | `APIRouter(prefix="/assignments", tags=["Employee Assignments"])` |

**Centralized Router Registration** (`app/core/routers/routers.py`):

```python
def setup_routers(app: FastAPI) -> None:
    app.include_router(system_router, tags=["System"])
    
    routers = [
        auth.router,
        employees.router,
        # ... other routers
    ]
    
    for router in routers:
        app.include_router(router, prefix=settings.API_PREFIX)
```

**Rules**:
1. Setiap router WAJIB declare `prefix` dan `tags` di file router masing-masing
2. Centralized registration HANYA menambahkan API prefix (`/api/v1`)
3. Tags di router file akan otomatis muncul di Swagger docs

---

## 3. SCHEMAS (DTOs)

*   `requests.py`: Input validasi. (`CreateUserRequest`, `UpdateUserRequest`)
*   `responses.py`: Output schema. (`UserResponse`, `UserListItemResponse`)
*   `shared.py`: Enum atau struct yang dipakai di kedua file.

**Rule**: Pisahkan `DetailResponse` (semua field) dan `ListItemResponse` (ringkas) untuk performa list.

---

## 4. NAMING CONVENTIONS

| Item | Format | Contoh |
| :--- | :--- | :--- |
| File | `snake_case` | `user_service.py` |
| Class | `PascalCase` | `UserService` |
| Method | `snake_case` | `get_by_id` |
| Variable | `snake_case` | `user_data` |
| Constant | `UPPER_SNAKE` | `MAX_UPLOAD_SIZE` |
| URL | `kebab-case` | `/users/upload-photo` |
| Table | `snake_case` (plural) | `users`, `org_units` |

---

## 5. CHECKLIST SEBELUM CODING (WAJIB)

### ✅ Before Creating Logic
- [ ] Cek `utils/` (module level & core level). Jangan buat duplicate helper.
- [ ] Cek Service lain. Jangan duplikasi logic yang sama.
- [ ] Pastikan Repository (Query/Command) sudah ada.

### ✅ Before Creating Endpoint
- [ ] Cek method (GET vs POST vs PATCH). Gunakan PATCH untuk update partial.
- [ ] Static route (`/me`) harus di atas dynamic route (`/{id}`).
- [ ] Pastikan `@require_permission` sesuai.

### ✅ Code Quality
- [ ] Type Hints **WAJIB** di function args & return.
- [ ] Tidak ada `print()`, gunakan `logger`.
- [ ] Tidak ada hardcoded strings/magic numbers.
- [ ] Error handling pakai `app.core.exceptions`.

---

## 6. GCP STORAGE & FILES

*   **Bucket**: Private, akses via Signed URL.
*   **DB Storage**: Simpan **PATH** (bukan URL). URL expired dalam 7 hari.
*   **Upload**: Gunakan `app.core.utils.upload_file_to_gcp`.
*   **Validation**: Selalu validasi extension dan size di Router/Service.

---

**Ingat: Dokumen ini adalah "Hukum". Langgar aturan = Technical Debt.**