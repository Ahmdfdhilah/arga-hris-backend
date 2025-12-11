"""
Core exceptions untuk HRIS Service

Struktur exceptions:
- base.py: APIException base class
- client_error.py: 4xx HTTP errors
- server_error.py: 5xx HTTP errors
- custom_error.py: Custom business logic exceptions
"""

from app.core.exceptions.base import APIException

# Client errors (4xx)
from app.core.exceptions.client_error import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
)

# Server errors (5xx)
from app.core.exceptions.server_error import (
    InternalServerException,
    NotImplementedException,
    ServiceUnavailableException,
)

# Custom exceptions
from app.core.exceptions.custom_error import (
    ValidationException,
    FileValidationError,
    GRPCConnectionException,
    GRPCException,
    BusinessLogicException,
    ResourceLockedException,
)

__all__ = [
    # Base
    "APIException",
    # Client errors
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "UnprocessableEntityException",
    # Server errors
    "InternalServerException",
    "NotImplementedException",
    "ServiceUnavailableException",
    # Custom exceptions
    "ValidationException",
    "FileValidationError",
    "GRPCConnectionException",
    "GRPCException",
    "BusinessLogicException",
    "ResourceLockedException",
]
