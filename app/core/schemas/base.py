from pydantic import BaseModel


class BaseResponse(BaseModel):
    error: bool
    message: str
    timestamp: str  # ISO 8601 format
