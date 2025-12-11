"""
Core Schemas

Generic type-safe response schemas for the application.

Exports:
    - BaseResponse: Base response model
    - DataResponse[T]: Generic single data response
    - PaginatedResponse[T]: Generic paginated response
    - PaginationMeta: Pagination metadata
    - FileSchema: File upload/download schema

Helper functions:
    - create_success_response(): Create typed success response
    - create_error_response(): Create typed error response
    - create_paginated_response(): Create typed paginated response

Legacy helpers (deprecated):
    - success_data_response(): Returns dict
    - error_data_response(): Returns dict
    - paginated_data_response(): Returns dict
"""

from app.core.schemas.base import BaseResponse
from app.core.schemas.data import DataResponse
from app.core.schemas.pagination import PaginatedResponse, PaginationMeta
from app.core.schemas.file import FileSchema
from app.core.schemas.current_user import CurrentUser
from app.core.schemas.helpers import (
    create_success_response,
    create_error_response,
    create_paginated_response,
)

__all__ = [
    # Response models
    "BaseResponse",
    "DataResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "FileSchema",
    "CurrentUser",
    #  typed helpers
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
]
