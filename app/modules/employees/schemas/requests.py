"""
Request schemas untuk Employee operations - Simplified (no guest handling)
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List


class EmployeeCreateRequest(BaseModel):
    """Request schema untuk membuat employee baru."""

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
        None, description="Tipe karyawan: 'on_site', 'hybrid', atau 'ho'"
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
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("employee_type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v


class EmployeeUpdateRequest(BaseModel):
    """Request schema untuk update employee."""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama depan"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Nama belakang"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site', 'hybrid', atau 'ho'"
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
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("employee_type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v


class CreateEmployeeWithAccountRequest(BaseModel):
    """
    Request schema untuk membuat employee dengan SSO user account.
    All employees get SSO user account automatically.
    """

    # Employee fields (required)
    number: str = Field(
        ..., min_length=1, max_length=50, description="Nomor karyawan (harus unik)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Nama belakang"
    )
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")

    # Employee fields (optional)
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site', 'hybrid', atau 'ho'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
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
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("employee_type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v


class UpdateEmployeeWithAccountRequest(BaseModel):
    """
    Request schema untuk update employee dengan sync ke SSO.
    
    NOTE: Email TIDAK BISA diubah karena core credential untuk login.
    """

    # Name fields (update employee + SSO)
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
        None, description="Tipe karyawan: 'on_site', 'hybrid', atau 'ho'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
    )
    supervisor_id: Optional[int] = Field(
        None, description="ID atasan langsung (null untuk hapus)"
    )

    # SSO profile fields (optional)
    alias: Optional[str] = Field(None, max_length=100, description="Alias/nickname")
    gender: Optional[str] = Field(None, max_length=20, description="Gender untuk SSO profile")
    address: Optional[str] = Field(None, max_length=500, description="Alamat")
    bio: Optional[str] = Field(None, max_length=1000, description="Bio")

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
                raise ValueError("employee_type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v


class EmployeeBulkItem(BaseModel):
    """Single employee item untuk bulk insert."""

    number: str = Field(
        ..., min_length=1, max_length=50, description="Nomor karyawan (harus unik)"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Nama belakang"
    )
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    org_unit_name: str = Field(
        ..., description="Nama unit organisasi (akan di-resolve ke ID)"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    employee_type: Optional[str] = Field(
        None, description="Tipe karyawan: 'on_site', 'hybrid', atau 'ho'"
    )
    employee_gender: Optional[str] = Field(
        None, description="Gender karyawan: 'male' atau 'female'"
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
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("employee_type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("employee_gender")
    @classmethod
    def validate_employee_gender(cls, v):
        if v is not None:
            if v not in ["male", "female"]:
                raise ValueError("employee_gender harus 'male' atau 'female'")
        return v

    @field_validator("org_unit_name")
    @classmethod
    def validate_org_unit_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Nama unit organisasi tidak boleh kosong")
        return v.strip().upper()


class EmployeeBulkInsertRequest(BaseModel):
    """Request schema untuk bulk insert employees."""

    items: List[EmployeeBulkItem] = Field(
        ..., min_length=1, description="List employees untuk di-insert"
    )
    skip_errors: bool = Field(
        False, description="Skip item yang error dan lanjutkan processing"
    )
