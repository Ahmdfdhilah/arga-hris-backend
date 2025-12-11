from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SubmissionStatus(str, Enum):
    """Status untuk work submission"""
    draft = "draft"
    submitted = "submitted"


class FileMetadata(BaseModel):
    """Metadata untuk file yang diupload"""
    file_name: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File path di GCP storage")
    file_size: int = Field(..., description="File size dalam bytes", gt=0)
    file_type: str = Field(..., description="MIME type dari file")
    file_url: Optional[str] = Field(None, description="Signed URL untuk download file")

    class Config:
        from_attributes = True
