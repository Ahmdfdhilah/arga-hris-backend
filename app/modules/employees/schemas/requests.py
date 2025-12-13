"""
Employee Request Schemas
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List


class EmployeeCreateRequest(BaseModel):
    """Create employee with SSO user account"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    number: str = Field(..., min_length=1, max_length=50)
    position: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = None
    org_unit_id: Optional[int] = Field(None, gt=0)
    supervisor_id: Optional[int] = Field(None, gt=0)

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee number is required")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v


class EmployeeUpdateRequest(BaseModel):
    """Update employee - profile changes sync to SSO"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = None
    org_unit_id: Optional[int] = Field(None, gt=0)
    supervisor_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v


class EmployeeBulkItem(BaseModel):
    """Single employee for bulk insert"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    number: str = Field(..., min_length=1, max_length=50)
    org_unit_id: Optional[int] = Field(None, gt=0)
    org_unit_name: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = None
    row_number: Optional[int] = None

    @field_validator("number")
    @classmethod
    def validate_number(cls, v):
        return v.strip().upper() if v else v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        return v.strip() if v else v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("type must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v
