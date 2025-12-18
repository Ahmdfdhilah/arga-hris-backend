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
│   ├── main.py                         # Entry point
│   ├── config/settings.py              # Env vars
│   ├── core/                           # Shared Logic
│   │   ├── exceptions/                 # Custom Exceptions
│   │   ├── schemas/                    # BaseResponses
│   │   ├── security/                   # RBAC & Auth
│   │   └── utils/                      # Global Helpers
│   │
│   └── modules/{module_name}/          # Domain Modules
│       ├── models/                     # SQLAlchemy Models
│       ├── schemas/                    # Pydantic DTOs
│       ├── repositories/               # Data Access
│       │   ├── commands/               # Write Ops
│       │   └── queries/                # Read Ops
│       ├── use_cases/                  # Pure Business Logic (Atomic)
│       ├── services/                   # Facade / Wrappers
│       ├── utils/                      # Module-specific helpers
│       ├── dependencies.py             # DI Definitions
│       └── routers/                    # API Endpoints
└── docs/RULES.MD                       # THIS FILE
```

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