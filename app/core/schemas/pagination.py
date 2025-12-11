from typing import List, Generic, TypeVar
from pydantic import BaseModel
from app.core.schemas.base import BaseResponse

T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata for paginated responses."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_prev_page: bool
    has_next_page: bool


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    Generic paginated response with type safety.

    Usage:
        PaginatedResponse[EmployeeResponse](
            error=False,
            message="Success",
            timestamp="2025-11-23T10:00:00Z",
            data=[employee1, employee2],
            meta=pagination_meta
        )

    The generic type T ensures type safety for items in the data list.
    """
    data: List[T]
    meta: PaginationMeta
