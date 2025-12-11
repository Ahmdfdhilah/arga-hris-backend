"""
Request schemas untuk Employee operations
Sesuai dengan models di workforce service: internal/models/employee.go
Field mapping: employee_* -> * (remove prefix untuk simplicity)

Workforce Model Fields:
- employee_number -> number
- employee_name -> name (combined from first_name + last_name)
- employee_email -> email
- employee_phone -> phone
- employee_position -> position
- employee_org_unit_id -> org_unit_id
- employee_supervisor_id -> supervisor_id
- employee_metadata -> metadata (JSONB)
- is_active -> is_active
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List


class EmployeeCreateRequest(BaseModel):
    """
    Request schema untuk membuat employee baru

    Note:
    - name akan di-combine dari first_name + last_name
    - date_of_birth, hire_date bisa disimpan di metadata jika perlu
    """

    number: str = Field(
        ..., min_length=1, max_length=50, description="Nomor karyawan (harus unik)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Nama belakang"
    )
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site' atau 'hybrid'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    org_unit_id: int = Field(..., gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(
        None, gt=0, description="ID atasan langsung (employee ID)"
    )

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Nomor karyawan tidak boleh kosong")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if not v or not v.strip():
            field_name = (
                "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            )
            raise ValueError(f"{field_name} tidak boleh kosong")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            # Remove common phone separators
            cleaned = (
                v.strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError(
                    "Nomor telepon hanya boleh mengandung angka dan tanda +"
                )
            return v.strip()
        return v

    @field_validator("employee_type")
    @classmethod
    def validate_employee_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid"]:
                raise ValueError("employee_type harus 'on_site' atau 'hybrid'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "number": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone": "+62812345678",
                "position": "Software Engineer",
                "employee_type": "on_site",
                "employee_gender": "male",
                "org_unit_id": 5,
                "supervisor_id": 3,
            }
        }


class EmployeeUpdateRequest(BaseModel):
    """
    Request schema untuk update employee

    Note:
    - name akan di-combine dari first_name + last_name jika keduanya ada
    - Email TIDAK BISA diubah karena merupakan core credential untuk login
    """

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama depan"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama belakang"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site' atau 'hybrid'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(
        None, description="ID atasan langsung (null untuk hapus)"
    )
    is_active: Optional[bool] = Field(None, description="Status aktif karyawan")

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if v is not None:
            if not v.strip():
                field_name = (
                    "Nama depan" if info.field_name == "first_name" else "Nama belakang"
                )
                raise ValueError(f"{field_name} tidak boleh kosong")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = (
                v.strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError(
                    "Nomor telepon hanya boleh mengandung angka dan tanda +"
                )
            return v.strip()
        return v

    @field_validator("employee_type")
    @classmethod
    def validate_employee_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid"]:
                raise ValueError("employee_type harus 'on_site' atau 'hybrid'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    class Config:
        from_attributes = True


class CreateEmployeeWithAccountRequest(BaseModel):
    """
    Request schema untuk membuat employee dengan account (unified)

    Mendukung 3 tipe account:
    - 'user': Employee dengan user account regular
    - 'guest': Employee dengan guest account (wajib ada guest fields)
    - 'none': Employee tanpa account
    """

    # Employee fields (wajib)
    number: str = Field(
        ..., min_length=1, max_length=50, description="Nomor karyawan (harus unik)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Nama belakang"
    )
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi (opsional)")

    # Employee fields (opsional)
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site' atau 'hybrid'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    supervisor_id: Optional[int] = Field(
        None, gt=0, description="ID atasan langsung (employee ID)"
    )

    # Account type
    account_type: str = Field(
        "none", description="Tipe akun: 'user', 'guest', atau 'none'"
    )

    # Guest fields (wajib untuk account_type='guest')
    guest_type: Optional[str] = Field(
        None, max_length=50, description="Tipe guest (wajib untuk guest)"
    )
    valid_from: Optional[str] = Field(
        None, description="Tanggal mulai berlaku (ISO format)"
    )
    valid_until: Optional[str] = Field(
        None, description="Tanggal akhir berlaku (ISO format, wajib untuk guest)"
    )
    sponsor_id: Optional[int] = Field(
        None, gt=0, description="ID sponsor (employee ID)"
    )
    notes: Optional[str] = Field(None, description="Catatan untuk guest")

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Nomor karyawan tidak boleh kosong")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if not v or not v.strip():
            field_name = (
                "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            )
            raise ValueError(f"{field_name} tidak boleh kosong")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = (
                v.strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError(
                    "Nomor telepon hanya boleh mengandung angka dan tanda +"
                )
            return v.strip()
        return v

    @field_validator("account_type")
    @classmethod
    def validate_account_type(cls, v):
        if v not in ["user", "guest", "none"]:
            raise ValueError("account_type harus 'user', 'guest', atau 'none'")
        return v

    @field_validator("employee_type")
    @classmethod
    def validate_employee_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid"]:
                raise ValueError("employee_type harus 'on_site' atau 'hybrid'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    class Config:
        from_attributes = True


class UpdateEmployeeWithAccountRequest(BaseModel):
    """
    Request schema untuk update employee dengan account (unified)

    Field dikategorikan menjadi:
    - Intersection: first_name, last_name, org_unit_id (update employee + user)
    - Employee-only: number, phone, position, supervisor_id (update employee saja)
    - Guest-only: valid_from, valid_until, guest_type, notes, sponsor_id (update guest saja)

    NOTE: Email TIDAK BISA diubah karena merupakan core credential untuk login dan authentication.
          Jika perlu mengubah email, user harus deactivate account lama dan buat account baru.
    """

    # Intersection fields (update employee + user)
    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama depan"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama belakang"
    )
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")

    # Employee-only fields
    number: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Nomor karyawan"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site' atau 'hybrid'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    supervisor_id: Optional[int] = Field(
        None, description="ID atasan langsung (null untuk hapus)"
    )

    # Guest-only fields
    valid_from: Optional[str] = Field(
        None, description="Tanggal mulai berlaku (ISO format)"
    )
    valid_until: Optional[str] = Field(
        None, description="Tanggal akhir berlaku (ISO format)"
    )
    guest_type: Optional[str] = Field(None, max_length=50, description="Tipe guest")
    notes: Optional[str] = Field(None, description="Catatan untuk guest")
    sponsor_id: Optional[int] = Field(None, description="ID sponsor (null untuk hapus)")

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if v is not None:
            if not v.strip():
                field_name = (
                    "Nama depan" if info.field_name == "first_name" else "Nama belakang"
                )
                raise ValueError(f"{field_name} tidak boleh kosong")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = (
                v.strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError(
                    "Nomor telepon hanya boleh mengandung angka dan tanda +"
                )
            return v.strip()
        return v

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Nomor karyawan tidak boleh kosong")
            return v.strip().upper()
        return v

    @field_validator("employee_type")
    @classmethod
    def validate_employee_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("employee_type harus 'on_site' atau 'hybrid'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "position": "Senior Software Engineer",
                "employee_type": "hybrid",
                "org_unit_id": 6,
            }
        }


class EmployeeBulkItem(BaseModel):
    """
    Single employee item untuk bulk insert

    Mapping dari Excel 'Karyawan':
    - Nomor -> number
    - Nama Depan -> first_name
    - Nama Belakang -> last_name
    - Email -> email
    - Department -> org_unit_code (akan di-resolve ke org_unit_id)
    - Nomor HP -> phone
    - Jabatan -> position
    - Tipe Karyawan -> employee_type
    - Jenis Karyawan -> account_type
    - Gender -> employee_gender
    - Awal Kontrak -> valid_from
    - Selesai Kontrak -> valid_until
    - Catatan -> notes
    """

    number: str = Field(
        ..., min_length=1, max_length=50, description="Nomor karyawan (harus unik)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Nama belakang"
    )
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    org_unit_name: str = Field(
        ..., description="Kode unit organisasi (akan di-resolve ke ID)"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site' atau 'hybrid', 'ho'"
    )
    account_type: str = Field(
        "user", description="Tipe akun: 'user', 'guest', atau 'none'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    valid_from: Optional[str] = Field(
        None, description="Tanggal mulai berlaku (ISO format)"
    )
    valid_until: Optional[str] = Field(
        None, description="Tanggal akhir berlaku (ISO format)"
    )
    notes: Optional[str] = Field(None, description="Catatan")
    row_number: Optional[int] = Field(
        None, description="Nomor baris di Excel untuk tracking error"
    )

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Nomor karyawan tidak boleh kosong")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if not v or not v.strip():
            field_name = (
                "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            )
            raise ValueError(f"{field_name} tidak boleh kosong")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = (
                v.strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError(
                    "Nomor telepon hanya boleh mengandung angka dan tanda +"
                )
            return v.strip()
        return v

    @field_validator("employee_type")
    @classmethod
    def validate_employee_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid", 'ho']:
                raise ValueError("employee_type harus 'on_site' , 'ho', atau 'hybrid'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    @field_validator("account_type")
    @classmethod
    def validate_account_type(cls, v):
        if v not in ["user", "guest", "none"]:
            raise ValueError("account_type harus 'user', 'guest', atau 'none'")
        return v

    @field_validator("org_unit_name")
    @classmethod
    def validate_org_unit_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Nama unit organisasi tidak boleh kosong")
        return v.strip().upper()


class EmployeeBulkInsertRequest(BaseModel):
    """Request schema untuk bulk insert employees"""

    items: List[EmployeeBulkItem] = Field(
        ..., min_length=1, description="List employees untuk di-insert"
    )
    skip_errors: bool = Field(
        False, description="Skip item yang error dan lanjutkan processing"
    )
