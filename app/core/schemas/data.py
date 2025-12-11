from typing import Generic, TypeVar, Optional
from app.core.schemas.base import BaseResponse

T = TypeVar('T')


class DataResponse(BaseResponse, Generic[T]):
    """
    Generic data response with type safety.

    Usage:
        DataResponse[EmployeeResponse](
            error=False,
            message="Success",
            timestamp="2025-11-23T10:00:00Z",
            data=employee
        )

    The generic type T ensures type safety for the data field.
    """
    data: Optional[T] = None
