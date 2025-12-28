from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UserCreateRequest(BaseModel):
    """Request schema for pre-creating user (admin only)"""
    email: EmailStr = Field(..., description="Email pengguna (harus unik)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan pengguna")
    last_name: Optional[str] = Field(None, max_length=100, description="Nama belakang pengguna")
    employee_id: Optional[int] = Field(None, gt=0, description="ID karyawan untuk dihubungkan (opsional)")
    is_active: bool = Field(True, description="Status aktif pengguna")

    @field_validator('first_name')
    @classmethod
    def validate_name(cls, v, info):
        if not v or not v.strip():
            raise ValueError('Nama depan tidak boleh kosong')
        if len(v) > 100:
            raise ValueError('Nama depan maksimal 100 karakter')
        return v.strip()
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v, info):
        if v and len(v) > 100:
            raise ValueError('Nama belakang maksimal 100 karakter')
        return v.strip() if v else ""


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama depan")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama belakang")

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v, info):
        if v is not None:
            if not v.strip():
                field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
                raise ValueError(f'{field_name} tidak boleh kosong')
            if len(v) > 100:
                field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
                raise ValueError(f'{field_name} maksimal 100 karakter')
            return v.strip()
        return v


class LinkEmployeeRequest(BaseModel):
    employee_id: int = Field(..., gt=0, description="ID karyawan untuk dihubungkan ke pengguna")

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if v <= 0:
            raise ValueError('ID karyawan harus lebih besar dari 0')
        return v
