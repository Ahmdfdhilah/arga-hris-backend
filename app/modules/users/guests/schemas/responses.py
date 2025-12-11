from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class GuestAccountResponse(BaseModel):
    """Response schema for guest account details"""
    id: int
    user_id: int
    guest_type: str
    valid_from: datetime
    valid_until: datetime
    sponsor_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GuestUserResponse(BaseModel):
    """Response schema for guest user with account details"""
    id: int
    sso_id: Optional[int] = None
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    account_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    guest_account: Optional[GuestAccountResponse] = None

    class Config:
        from_attributes = True


class GuestUserListResponse(BaseModel):
    """Response schema for paginated guest users list"""
    users: List[GuestUserResponse]
    pagination: Dict[str, Any]
