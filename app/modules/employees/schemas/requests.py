"""
Employee Request Schemas
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class EmployeeCreateRequest(BaseModel):
    """Create employee with SSO user account"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    code: str = Field(..., min_length=1, max_length=50)
    position: Optional[str] = Field(None, max_length=255)
    site: Optional[str] = None  # on_site, hybrid, ho
    type: Optional[str] = None  # fulltime, contract, intern
    org_unit_id: Optional[int] = Field(None, gt=0)
    supervisor_id: Optional[int] = Field(None, gt=0)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee code is required")
        return v.strip().upper()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @field_validator("site")
    @classmethod
    def validate_site(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("site must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["fulltime", "contract", "intern"]:
            raise ValueError("type must be 'fulltime', 'contract', or 'intern'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v


class EmployeeUpdateRequest(BaseModel):
    """
    Update employee fields.
    
    - first_name/last_name: Updates denormalized `name` on Employee only (NOT synced to SSO)
    - email/phone: Synced to SSO
    - Other fields: Employee-only
    
    Note: Sending null explicitly clears optional fields.
    """

    # Name fields (Employee-only, updates denormalized name, NOT synced to SSO)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    # SSO-synced fields (email/phone only)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    
    # Employee-only fields
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    position: Optional[str] = Field(None, max_length=255)
    site: Optional[str] = None  # on_site, hybrid, ho
    type: Optional[str] = None  # fulltime, contract, intern
    org_unit_id: Optional[int] = Field(None, gt=0)
    supervisor_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if v is not None and v != "" and not v.strip():
            raise ValueError("Employee code cannot be empty")
        return v.strip().upper() if v else v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and v != "":
            return v.strip()
        return v  # Allow None or empty string (for clearing)

    @field_validator("site")
    @classmethod
    def validate_site(cls, v):
        if v is not None and v != "" and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("site must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v != "" and v not in ["fulltime", "contract", "intern"]:
            raise ValueError("type must be 'fulltime', 'contract', or 'intern'")
        return v


class EmployeeBulkItem(BaseModel):
    """Single employee for bulk insert"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    code: str = Field(..., min_length=1, max_length=50)
    org_unit_id: Optional[int] = Field(None, gt=0)
    org_unit_name: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    site: Optional[str] = None  # on_site, hybrid, ho
    type: Optional[str] = None  # fulltime, contract, intern
    row_number: Optional[int] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        return v.strip().upper() if v else v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        return v.strip() if v else v

    @field_validator("site")
    @classmethod
    def validate_site(cls, v):
        if v is not None and v not in ["on_site", "hybrid", "ho"]:
            raise ValueError("site must be 'on_site', 'hybrid', or 'ho'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None and v not in ["fulltime", "contract", "intern"]:
            raise ValueError("type must be 'fulltime', 'contract', or 'intern'")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["male", "female"]:
            raise ValueError("gender must be 'male' or 'female'")
        return v
