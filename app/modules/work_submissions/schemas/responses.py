from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, field_serializer
from app.modules.work_submissions.schemas.shared import FileMetadata, SubmissionStatus


class WorkSubmissionResponse(BaseModel):
    """Response schema untuk work submission detail."""

    id: int
    employee_id: int
    submission_month: date
    title: str
    description: Optional[str] = None
    files: List[FileMetadata] = Field(
        default_factory=list, description="List file dengan signed URLs"
    )
    status: SubmissionStatus
    submitted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("submission_month")
    def serialize_submission_month(self, submission_month: date, _info):
        """Serialize date to ISO format"""
        return submission_month.isoformat()

    @field_serializer("submitted_at", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info):
        """Serialize datetime to ISO format"""
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


class WorkSubmissionListResponse(BaseModel):
    """Response schema untuk work submission list dengan employee info."""

    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_number: Optional[str] = None
    submission_month: date
    title: str
    files_count: int = Field(default=0, description="Jumlah file yang diupload")
    status: SubmissionStatus
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("submission_month")
    def serialize_submission_month(self, submission_month: date, _info):
        """Serialize date to ISO format"""
        return submission_month.isoformat()

    @field_serializer("submitted_at", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info):
        """Serialize datetime to ISO format"""
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True
