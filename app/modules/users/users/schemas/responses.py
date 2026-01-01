import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class UserResponse(BaseModel):
    id: uuid.UUID  # SSO UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithEmployeeResponse(BaseModel):
    id: uuid.UUID  # SSO UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    employee: Optional[dict] = None


class UserDetailResponse(BaseModel):
    id: uuid.UUID  # SSO UUID
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    employee_data: Optional[Dict[str, Any]] = None
    org_unit_data: Optional[Dict[str, Any]] = None
