from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, timezone


class CreateGuestRequest(BaseModel):
    """Request schema for creating guest user"""
    email: EmailStr = Field(..., description="Email guest (harus unik)")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nama depan")
    last_name: str = Field(..., min_length=1, max_length=100, description="Nama belakang")
    guest_type: str = Field(..., description="Tipe guest (intern/contractor/guest)")
    valid_until: datetime = Field(..., description="Tanggal berakhir akses")
    valid_from: Optional[datetime] = Field(None, description="Tanggal mulai akses (default: now)")
    sponsor_id: Optional[int] = Field(None, gt=0, description="ID sponsor/pembimbing")
    notes: Optional[str] = Field(None, max_length=500, description="Catatan tambahan")

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v, info):
        if not v or not v.strip():
            field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            raise ValueError(f'{field_name} tidak boleh kosong')
        if len(v) > 100:
            field_name = "Nama depan" if info.field_name == "first_name" else "Nama belakang"
            raise ValueError(f'{field_name} maksimal 100 karakter')
        return v.strip()

    @field_validator('guest_type')
    @classmethod
    def validate_guest_type(cls, v):
        if not v or not v.strip():
            raise ValueError('Tipe guest tidak boleh kosong')
        allowed_types = ['intern', 'contractor', 'guest']
        if v.strip().lower() not in allowed_types:
            raise ValueError(f'Tipe guest harus salah satu dari: {", ".join(allowed_types)}')
        return v.strip().lower()

    @field_validator('valid_until')
    @classmethod
    def validate_valid_until(cls, v):
        if not v:
            raise ValueError('Tanggal berakhir tidak boleh kosong')
        # Make timezone-aware if not already
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        # Validate valid_until is in the future
        now = datetime.now(timezone.utc)
        if v <= now:
            raise ValueError('Tanggal berakhir harus di masa depan')
        return v

    @field_validator('valid_from')
    @classmethod
    def validate_valid_from(cls, v, info):
        if v is not None:
            # Make timezone-aware if not already
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            # Check if valid_until exists and valid_from < valid_until
            if 'valid_until' in info.data:
                valid_until = info.data['valid_until']
                if valid_until and v >= valid_until:
                    raise ValueError('Tanggal mulai harus sebelum tanggal berakhir')
        return v


class UpdateGuestAccountRequest(BaseModel):
    """Request schema for updating guest account"""
    guest_type: Optional[str] = Field(None, description="Tipe guest (intern/contractor)")
    valid_from: Optional[datetime] = Field(None, description="Tanggal mulai akses")
    valid_until: Optional[datetime] = Field(None, description="Tanggal berakhir akses")
    sponsor_id: Optional[int] = Field(None, gt=0, description="ID sponsor/pembimbing")
    notes: Optional[str] = Field(None, max_length=500, description="Catatan tambahan")

    @field_validator('guest_type')
    @classmethod
    def validate_guest_type(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Tipe guest tidak boleh kosong')
            allowed_types = ['intern', 'contractor', 'guest']
            if v.strip().lower() not in allowed_types:
                raise ValueError(f'Tipe guest harus salah satu dari: {", ".join(allowed_types)}')
            return v.strip().lower()
        return v

    @field_validator('valid_until')
    @classmethod
    def validate_valid_until(cls, v, info):
        if v is not None and 'valid_from' in info.data:
            valid_from = info.data['valid_from']
            if valid_from and v <= valid_from:
                raise ValueError('Tanggal berakhir harus setelah tanggal mulai')
        return v
