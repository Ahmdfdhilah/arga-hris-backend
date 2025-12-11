"""
Request schemas untuk job management API.
"""

from pydantic import BaseModel


class JobTriggerRequest(BaseModel):
    """Schema untuk trigger job manual"""
    pass  # Tidak butuh payload, job_id dari path parameter
