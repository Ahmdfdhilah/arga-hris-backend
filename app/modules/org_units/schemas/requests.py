"""
Request schemas untuk Org Unit operations
Sesuai dengan models di workforce service: internal/models/organization_unit.go
Field mapping: org_unit_* -> * (remove prefix untuk simplicity)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class OrgUnitCreateRequest(BaseModel):
    """
    Request schema untuk membuat org unit baru
    
    Mapping ke workforce model:
    - code -> org_unit_code
    - name -> org_unit_name
    - type -> org_unit_type
    - parent_id -> org_unit_parent_id
    - level -> org_unit_level (auto-calculated)
    - path -> org_unit_path (auto-calculated)
    - head_id -> org_unit_head_id
    - description -> org_unit_description
    """
    
    code: str = Field(..., min_length=1, max_length=50, description="Kode unit organisasi (harus unik)")
    name: str = Field(..., min_length=1, max_length=255, description="Nama unit organisasi")
    type: str = Field(..., description="Tipe unit organisasi")
    parent_id: Optional[int] = Field(None, gt=0, description="ID parent unit organisasi (opsional)")
    head_id: Optional[int] = Field(None, gt=0, description="ID kepala unit (employee ID)")
    description: Optional[str] = Field(None, description="Deskripsi unit organisasi")
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Kode unit organisasi tidak boleh kosong')
        # Code should be alphanumeric with dash/underscore
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Kode unit organisasi hanya boleh mengandung huruf, angka, dash, dan underscore')
        return v.strip().upper()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama unit organisasi tidak boleh kosong')
        return v.strip()
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if not v or not v.strip():
            raise ValueError('Tipe unit organisasi tidak boleh kosong')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "IT-DEV",
                "name": "IT Development",
                "type": "department",
                "parent_id": 1,
                "head_id": 10,
                "description": "Departemen pengembangan teknologi informasi"
            }
        }


class OrgUnitUpdateRequest(BaseModel):
    """
    Request schema untuk update org unit
    
    Mapping ke workforce model (field yang bisa diupdate):
    - name -> org_unit_name
    - type -> org_unit_type
    - parent_id -> org_unit_parent_id
    - head_id -> org_unit_head_id
    - description -> org_unit_description
    - is_active -> is_active
    
    Note: level dan path akan auto-recalculated oleh backend
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nama unit organisasi")
    type: Optional[str] = Field(None, description="Tipe unit organisasi")
    parent_id: Optional[int] = Field(None, gt=0, description="ID parent unit organisasi")
    head_id: Optional[int] = Field(None, description="ID kepala unit (employee ID, null untuk hapus)")
    description: Optional[str] = Field(None, description="Deskripsi unit organisasi")
    is_active: Optional[bool] = Field(None, description="Status aktif unit organisasi")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Nama unit organisasi tidak boleh kosong')
            return v.strip()
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Tipe unit organisasi tidak boleh kosong')
            return v.strip()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "IT Development & Innovation",
                "head_id": 15,
                "description": "Departemen pengembangan dan inovasi teknologi informasi"
            }
        }


class OrgUnitBulkItem(BaseModel):
    """
    Single org unit item untuk bulk insert

    Mapping dari Excel 'Department':
    - Kode -> code
    - Nama -> name
    - Tipe -> type
    - Head Departement -> parent_code (kode parent department)
    - Head Email -> head_email
    - Deskripsi -> description
    """

    code: str = Field(..., min_length=1, max_length=50, description="Kode unit organisasi (harus unik)")
    name: str = Field(..., min_length=1, max_length=255, description="Nama unit organisasi")
    type: str = Field(..., description="Tipe unit organisasi")
    parent_code: Optional[str] = Field(None, max_length=50, description="Kode parent unit organisasi (opsional)")
    head_email: Optional[str] = Field(None, description="Email kepala unit (akan di-resolve ke employee ID)")
    description: Optional[str] = Field(None, description="Deskripsi unit organisasi")
    row_number: Optional[int] = Field(None, description="Nomor baris di Excel untuk tracking error")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Kode unit organisasi tidak boleh kosong')
        cleaned = v.replace('-', '').replace('_', '')
        if not cleaned.isalnum():
            raise ValueError('Kode unit organisasi hanya boleh mengandung huruf, angka, dash, dan underscore')
        return v.strip().upper()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nama unit organisasi tidak boleh kosong')
        return v.strip()

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if not v or not v.strip():
            raise ValueError('Tipe unit organisasi tidak boleh kosong')
        return v.strip()

    @field_validator('parent_code')
    @classmethod
    def validate_parent_code(cls, v):
        if v is not None and v.strip():
            return v.strip().upper()
        return None


class OrgUnitBulkInsertRequest(BaseModel):
    """Request schema untuk bulk insert org units"""

    items: List[OrgUnitBulkItem] = Field(..., min_length=1, description="List org units untuk di-insert")
    skip_errors: bool = Field(False, description="Skip item yang error dan lanjutkan processing")
