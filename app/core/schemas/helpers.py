"""
Response Helper Functions

Helper functions untuk membuat response sesuai standard perusahaan.

New typed versions (recommended):
- create_success_response() - Returns DataResponse[T]
- create_paginated_response() - Returns PaginatedResponse[T]

Legacy dict versions (deprecated):
- success_data_response() - Returns dict
- error_data_response() - Returns dict
- paginated_data_response() - Returns dict
"""

from typing import  List, TypeVar, Optional
from datetime import datetime
from app.core.utils.pagination import calculate_pagination_meta
from app.core.schemas.data import DataResponse
from app.core.schemas.pagination import PaginatedResponse, PaginationMeta

T = TypeVar('T')

def create_success_response(
    message: str,
    data: Optional[T] = None
) -> DataResponse[T]:
    """
    Create type-safe success data response.

    Args:
        message: Success message
        data: Response data with type T

    Returns:
        DataResponse[T] with structure:
        {
            "error": False,
            "message": "...",
            "timestamp": "2025-11-23T10:00:00.000Z",
            "data": ... (typed as T)
        }

    Example:
        response = create_success_response(
            message="Employee retrieved successfully",
            data=employee  # Type: EmployeeResponse
        )
        # Returns DataResponse[EmployeeResponse]
    """
    return DataResponse[T](
        error=False,
        message=message,
        timestamp=datetime.utcnow().isoformat() + "Z",
        data=data,
    )


def create_error_response(
    message: str,
    data: Optional[T] = None
) -> DataResponse[T]:
    """
    Create type-safe error data response.

    Args:
        message: Error message
        data: Additional error data (optional, typed as T)

    Returns:
        DataResponse[T] with structure:
        {
            "error": True,
            "message": "...",
            "timestamp": "2025-11-23T10:00:00.000Z",
            "data": ... (typed as T)
        }
    """
    return DataResponse[T](
        error=True,
        message=message,
        timestamp=datetime.utcnow().isoformat() + "Z",
        data=data,
    )


def create_paginated_response(
    message: str,
    data: List[T],
    page: int,
    limit: int,
    total_items: int,
) -> PaginatedResponse[T]:
    """
    Create type-safe paginated data response.

    Args:
        message: Success message
        data: List of data items (typed as List[T])
        page: Current page number
        limit: Items per page
        total_items: Total number of items

    Returns:
        PaginatedResponse[T] with structure:
        {
            "error": False,
            "message": "...",
            "timestamp": "2025-11-23T10:00:00.000Z",
            "data": [...] (typed as List[T]),
            "meta": {
                "page": 1,
                "limit": 10,
                "total_items": 100,
                "total_pages": 10,
                "has_prev_page": False,
                "has_next_page": True
            }
        }

    Example:
        response = create_paginated_response(
            message="Employees retrieved successfully",
            data=employees,  # Type: List[EmployeeResponse]
            page=1,
            limit=10,
            total_items=100
        )
        # Returns PaginatedResponse[EmployeeResponse]
    """
    meta_dict = calculate_pagination_meta(page, limit, total_items)
    meta = PaginationMeta(**meta_dict)

    return PaginatedResponse[T](
        error=False,
        message=message,
        timestamp=datetime.utcnow().isoformat() + "Z",
        data=data,
        meta=meta,
    )
