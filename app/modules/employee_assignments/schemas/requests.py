"""
Request schemas untuk Employee Assignments module.
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator


class AssignmentCreateRequest(BaseModel):
    """Request schema untuk membuat employee assignment."""

    employee_id: int = Field(..., gt=0, description="ID employee yang menggantikan")
    replaced_employee_id: int = Field(
        ..., gt=0, description="ID employee yang digantikan"
    )
    org_unit_id: int = Field(..., gt=0, description="ID org unit untuk context")
    start_date: date = Field(..., description="Tanggal mulai penggantian")
    end_date: date = Field(..., description="Tanggal akhir penggantian")
    leave_request_id: int = Field(..., gt=0, description="ID leave request terkait")
    reason: Optional[str] = Field(
        None, max_length=500, description="Alasan penggantian"
    )

    @field_validator("employee_id", "replaced_employee_id")
    @classmethod
    def validate_employee_ids(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ID employee harus lebih besar dari 0")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        if v and info.data.get("start_date"):
            if v < info.data["start_date"]:
                raise ValueError(
                    "Tanggal akhir harus lebih besar atau sama dengan tanggal mulai"
                )
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    class Config:
        from_attributes = True


class AssignmentCancelRequest(BaseModel):
    """Request schema untuk membatalkan assignment."""

    reason: Optional[str] = Field(None, max_length=500, description="Alasan pembatalan")

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    class Config:
        from_attributes = True
