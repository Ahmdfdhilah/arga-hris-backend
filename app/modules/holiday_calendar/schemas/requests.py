"""Request schemas untuk Holiday Calendar."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as DateType


class CreateHolidayRequest(BaseModel):
    """Request untuk membuat holiday baru."""
    
    date: DateType = Field(..., description="Tanggal libur")
    name: str = Field(..., min_length=1, max_length=255, description="Nama hari libur")
    description: Optional[str] = Field(None, description="Deskripsi tambahan")


class UpdateHolidayRequest(BaseModel):
    """Request untuk update holiday."""
    
    date: Optional[DateType] = Field(None, description="Tanggal libur")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nama hari libur")
    description: Optional[str] = Field(None, description="Deskripsi tambahan")
    is_active: Optional[bool] = Field(None, description="Status aktif")

