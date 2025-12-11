"""
Response schemas untuk job management API.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class JobStatusResponse(BaseModel):
    """Schema response untuk status job"""
    job_id: str
    name: str
    description: Optional[str] = None
    next_run: Optional[str] = None
    trigger: str
    enabled: bool
    latest_execution: Optional["JobExecutionResponse"] = None

    class Config:
        from_attributes = True


class JobExecutionResponse(BaseModel):
    """Schema response untuk job execution log"""
    id: int
    job_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool
    message: Optional[str] = None
    error_trace: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobTriggerResultResponse(BaseModel):
    """Schema response untuk hasil manual trigger job"""
    job_id: str
    success: bool
    result: Optional[Any] = None


# Forward reference for JobStatusResponse
JobStatusResponse.model_rebuild()
