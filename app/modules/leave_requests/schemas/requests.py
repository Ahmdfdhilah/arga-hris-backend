from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator
from app.modules.leave_requests.schemas.shared import LeaveType


class LeaveRequestCreateRequest(BaseModel):
    """Request schema untuk membuat leave request (HR Admin)."""

    employee_id: int = Field(..., gt=0, description="ID employee dari workforce service")
    leave_type: LeaveType = Field(..., description=f"Jenis cuti ({LeaveType.values_string()})")
    start_date: date = Field(..., description="Tanggal mulai cuti")
    end_date: date = Field(..., description="Tanggal akhir cuti")
    reason: str = Field(..., min_length=1, max_length=1000, description="Alasan pengajuan cuti")

    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if v <= 0:
            raise ValueError('ID employee harus lebih besar dari 0')
        return v

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if not v or not v.strip():
            raise ValueError('Alasan cuti tidak boleh kosong')
        return v.strip()

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date'):
            if v < info.data['start_date']:
                raise ValueError('Tanggal akhir cuti harus lebih besar atau sama dengan tanggal mulai cuti')
        return v

    class Config:
        from_attributes = True


class LeaveRequestUpdateRequest(BaseModel):
    """Request schema untuk update leave request (HR Admin)."""

    leave_type: Optional[LeaveType] = Field(None, description=f"Jenis cuti ({LeaveType.values_string()})")
    start_date: Optional[date] = Field(None, description="Tanggal mulai cuti")
    end_date: Optional[date] = Field(None, description="Tanggal akhir cuti")
    reason: Optional[str] = Field(None, min_length=1, max_length=1000, description="Alasan pengajuan cuti")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Alasan cuti tidak boleh kosong')
            return v.strip()
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date'):
            if v < info.data['start_date']:
                raise ValueError('Tanggal akhir cuti harus lebih besar atau sama dengan tanggal mulai cuti')
        return v

    class Config:
        from_attributes = True
