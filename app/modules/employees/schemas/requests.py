"""
Request schemas untuk Employee operations

Profile data (name, email, phone, gender) goes through User/SSO.
Employee requests focus on employment data.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List


class EmployeeCreateRequest(BaseModel):
    """
    Request untuk membuat employee (internal use).
    Requires existing user_id - used when user already exists.
    """
    user_id: int = Field(..., gt=0, description="ID user (from SSO sync)")
    number: str = Field(..., min_length=1, max_length=50, description="Nomor karyawan")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    type: Optional[str] = Field(None, description="Tipe: 'on_site', 'hybrid', 'ho'")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(None, gt=0, description="ID atasan langsung")

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Nomor karyawan tidak boleh kosong")
        return v.strip().upper()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            if v not in ["on_site", "hybrid", "ho"]:
                raise ValueError("type harus 'on_site', 'hybrid', atau 'ho'")
        return v


class EmployeeUpdateRequest(BaseModel):
    """
    Request untuk update employee employment data.
    Profile updates (name, email, phone, gender) go through User/SSO.
    """
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    type: Optional[str] = Field(None, description="Tipe: 'on_site', 'hybrid', 'ho'")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(None, description="ID atasan langsung (null untuk hapus)")
    is_active: Optional[bool] = Field(None, description="Status aktif karyawan")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type harus 'on_site', 'hybrid', atau 'ho'")
        return v


class CreateEmployeeWithAccountRequest(BaseModel):
    """
    Request untuk membuat employee dengan SSO user account.
    
    Flow:
    1. Create SSO user (name, email, phone, gender)
    2. Sync user to local HRIS users table
    3. Create employee linked to user
    """
    # User profile fields (sent to SSO)
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nama belakang")
    email: EmailStr = Field(..., description="Email karyawan (harus unik)")
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    gender: Optional[str] = Field(None, description="Gender: 'male' atau 'female'")

    # Employee fields
    number: str = Field(..., min_length=1, max_length=50, description="Nomor karyawan")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    type: Optional[str] = Field(None, description="Tipe: 'on_site', 'hybrid', 'ho'")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(None, gt=0, description="ID atasan langsung")

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
            field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            raise ValueError(f"{field_name} tidak boleh kosong")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = v.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.replace("+", "").isdigit():
                raise ValueError("Nomor telepon hanya boleh mengandung angka dan tanda +")
            return v.strip()
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender harus 'male' atau 'female'")
        return v


class UpdateEmployeeWithAccountRequest(BaseModel):
    """
    Request untuk update employee dengan sync ke SSO.
    
    Profile updates (name, phone, gender) sync to SSO.
    Email CANNOT be changed (core credential).
    """
    # User profile fields (sync to SSO)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama depan")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama belakang")
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    gender: Optional[str] = Field(None, description="Gender: 'male' atau 'female'")

    # Employee fields
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    type: Optional[str] = Field(None, description="Tipe: 'on_site', 'hybrid', 'ho'")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID unit organisasi")
    supervisor_id: Optional[int] = Field(None, description="ID atasan langsung")

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v, info):
        if v is not None:
            if not v.strip():
                field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
                raise ValueError(f"{field_name} tidak boleh kosong")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            cleaned = v.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.replace("+", "").isdigit():
                raise ValueError("Nomor telepon hanya boleh mengandung angka dan tanda +")
            return v.strip()
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender harus 'male' atau 'female'")
        return v


class EmployeeBulkItem(BaseModel):
    """Single employee item untuk bulk insert dengan SSO account."""
    # User profile
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nama belakang")
    email: EmailStr = Field(..., description="Email karyawan")
    phone: Optional[str] = Field(None, max_length=50, description="Nomor telepon")
    gender: Optional[str] = Field(None, description="Gender: 'male' atau 'female'")

    # Employee data
    number: str = Field(..., min_length=1, max_length=50, description="Nomor karyawan")
    org_unit_name: str = Field(..., description="Nama unit organisasi")
    position: Optional[str] = Field(None, max_length=255, description="Jabatan/Posisi")
    type: Optional[str] = Field(None, description="Tipe: 'on_site', 'hybrid', 'ho'")

    # Tracking
    notes: Optional[str] = Field(None, description="Catatan")
    row_number: Optional[int] = Field(None, description="Nomor baris di Excel")

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
            field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            raise ValueError(f"{field_name} tidak boleh kosong")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type harus 'on_site', 'hybrid', atau 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender harus 'male' atau 'female'")
        return v

    @field_validator("org_unit_name")
    @classmethod
    def validate_org_unit_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Nama unit organisasi tidak boleh kosong")
        return v.strip().upper()


class EmployeeBulkInsertRequest(BaseModel):
    """Request untuk bulk insert employees dengan SSO accounts."""
    items: List[EmployeeBulkItem] = Field(..., min_length=1, description="List employees")
    skip_errors: bool = Field(False, description="Skip item yang error")
