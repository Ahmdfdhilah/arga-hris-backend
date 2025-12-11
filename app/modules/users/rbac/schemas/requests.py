from pydantic import BaseModel, Field, field_validator
from typing import List


class AssignRoleRequest(BaseModel):
    role_name: str = Field(..., min_length=1, description="Nama role untuk diberikan ke pengguna")

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama role tidak boleh kosong')
        return v.strip()


class RemoveRoleRequest(BaseModel):
    role_name: str = Field(..., min_length=1, description="Nama role untuk dihapus dari pengguna")

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama role tidak boleh kosong')
        return v.strip()


class AssignRolesRequest(BaseModel):
    role_names: List[str] = Field(..., min_length=1, description="Daftar nama role untuk diberikan ke pengguna")

    @field_validator('role_names')
    @classmethod
    def validate_role_names(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Daftar role tidak boleh kosong')

        cleaned_roles = []
        for role in v:
            if not role or not role.strip():
                raise ValueError('Nama role tidak boleh kosong')
            cleaned_roles.append(role.strip())

        return cleaned_roles
