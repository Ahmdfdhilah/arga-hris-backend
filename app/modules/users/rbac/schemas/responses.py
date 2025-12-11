from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    resource: str
    action: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRolesPermissionsResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    roles: List[str]
    permissions: List[str]


class RoleAssignmentResponse(BaseModel):
    """Response untuk hasil assign/remove role"""
    user_id: int
    role_name: str


class MultipleRoleAssignmentResponse(BaseModel):
    """Response untuk hasil assign multiple roles"""
    user_id: int
    roles: List[str]
