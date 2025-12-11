from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.modules.work_submissions.schemas.shared import SubmissionStatus


class WorkSubmissionCreateRequest(BaseModel):
    """Request schema untuk membuat work submission baru."""
    employee_id: int = Field(..., description="ID karyawan", gt=0)
    submission_month: date = Field(..., description="Bulan submission (format: YYYY-MM-DD)")
    title: str = Field(..., min_length=1, max_length=255, description="Judul submission")
    description: Optional[str] = Field(None, description="Deskripsi detail apa yang dikerjakan")
    status: SubmissionStatus = Field(default=SubmissionStatus.draft, description="Status submission")

    @field_validator('submission_month')
    @classmethod
    def normalize_to_first_day(cls, v: date) -> date:
        """Normalize submission_month to first day of month"""
        return date(v.year, v.month, 1)

    class Config:
        from_attributes = True



class WorkSubmissionUpdateRequest(BaseModel):
    """Request schema untuk update work submission."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Judul submission")
    description: Optional[str] = Field(None, min_length=1, description="Deskripsi detail")
    status: Optional[SubmissionStatus] = Field(None, description="Status submission")

    class Config:
        from_attributes = True

