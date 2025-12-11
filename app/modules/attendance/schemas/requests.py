from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from app.modules.attendance.schemas.shared import AttendanceStatus


class CheckInRequest(BaseModel):
    """Request schema untuk check-in attendance."""

    notes: Optional[str] = Field(None, description="Catatan check-in")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude koordinat lokasi check-in")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude koordinat lokasi check-in")

    class Config:
        from_attributes = True


class CheckOutRequest(BaseModel):
    """Request schema untuk check-out attendance."""

    notes: Optional[str] = Field(None, description="Catatan check-out")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude koordinat lokasi check-out")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude koordinat lokasi check-out")

    class Config:
        from_attributes = True


class AttendanceCreateRequest(BaseModel):
    """Request schema untuk membuat attendance secara manual (admin)."""

    employee_id: int = Field(..., gt=0, description="ID employee dari workforce service")
    org_unit_id: Optional[int] = Field(None, gt=0, description="ID org unit untuk keperluan tampilan")
    attendance_date: date = Field(..., description="Tanggal kehadiran")
    status: AttendanceStatus = Field(..., description=f"Status kehadiran ({AttendanceStatus.values_string()})")
    check_in_time: Optional[datetime] = Field(None, description="Waktu check-in")
    check_out_time: Optional[datetime] = Field(None, description="Waktu check-out")
    check_in_notes: Optional[str] = Field(None, description="Catatan check-in")
    check_out_notes: Optional[str] = Field(None, description="Catatan check-out")

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if v <= 0:
            raise ValueError('ID employee harus lebih besar dari 0')
        return v

    @field_validator('check_out_time')
    @classmethod
    def validate_check_out_time(cls, v, info):
        if v and info.data.get('check_in_time'):
            if v <= info.data['check_in_time']:
                raise ValueError('Waktu check-out harus lebih besar dari waktu check-in')
        return v

    class Config:
        from_attributes = True


class AttendanceUpdateRequest(BaseModel):
    """Request schema untuk update attendance (admin)."""

    status: Optional[AttendanceStatus] = Field(None, description=f"Status kehadiran ({AttendanceStatus.values_string()})")
    check_in_time: Optional[datetime] = Field(None, description="Waktu check-in")
    check_out_time: Optional[datetime] = Field(None, description="Waktu check-out")
    check_in_notes: Optional[str] = Field(None, description="Catatan check-in")
    check_out_notes: Optional[str] = Field(None, description="Catatan check-out")

    @field_validator('check_out_time')
    @classmethod
    def validate_check_out_time(cls, v, info):
        if v and info.data.get('check_in_time'):
            if v <= info.data['check_in_time']:
                raise ValueError('Waktu check-out harus lebih besar dari waktu check-in')
        return v

    class Config:
        from_attributes = True


class BulkMarkPresentRequest(BaseModel):
    """Request schema untuk bulk mark present (admin)."""

    attendance_date: date = Field(..., description="Tanggal kehadiran untuk bulk mark present")
    notes: Optional[str] = Field(None, description="Catatan untuk bulk mark present (contoh: Libur Nasional)")

    @field_validator('attendance_date')
    @classmethod
    def validate_attendance_date(cls, v):
        if v > date.today():
            raise ValueError('Tanggal kehadiran tidak boleh melebihi hari ini')
        return v

    class Config:
        from_attributes = True


class MarkPresentByIdRequest(BaseModel):
    """Request schema untuk mark present by ID (admin)."""

    notes: Optional[str] = Field(None, description="Catatan untuk perubahan attendance")

    class Config:
        from_attributes = True