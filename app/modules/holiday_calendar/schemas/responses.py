"""Response schemas untuk Holiday Calendar."""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class HolidayResponse(BaseModel):
    """Response untuk single holiday."""
    
    id: int
    date: date
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HolidayListItemResponse(BaseModel):
    """Response ringkas untuk list holiday."""
    
    id: int
    date: date
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class IsHolidayResponse(BaseModel):
    """Response untuk cek apakah tanggal adalah hari libur."""
    
    date: date
    is_holiday: bool
    holiday_name: Optional[str] = None
