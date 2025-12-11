"""
Custom exceptions untuk use cases khusus

Berisi exception-exception yang tidak termasuk kategori client/server errors standar
tapi spesifik untuk business logic aplikasi.
"""

from app.core.exceptions.base import APIException


class ValidationException(APIException):
    """
    Exception untuk validation errors

    Raised ketika input data tidak memenuhi kriteria validasi business logic.

    HTTP Status Code: 400 Bad Request

    Example:
        >>> raise ValidationException("Email sudah terdaftar")
        >>> raise ValidationException("Tanggal mulai harus sebelum tanggal akhir")
    """
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 400)


class FileValidationError(APIException):
    """
    Exception untuk file validation errors

    Raised ketika uploaded file tidak memenuhi kriteria validasi:
    - File type tidak diizinkan
    - File size melebihi limit
    - File content tidak sesuai dengan extension

    HTTP Status Code: 400 Bad Request

    Example:
        >>> raise FileValidationError("File terlalu besar. Maximum size: 5 MB")
        >>> raise FileValidationError("File type 'image/svg+xml' tidak diizinkan")
    """
    def __init__(self, message: str = "File validation failed"):
        super().__init__(message, 400)


class GRPCConnectionException(APIException):
    """
    Exception untuk GRPC connection errors

    Raised ketika gagal connect ke GRPC service.

    HTTP Status Code: 503 Service Unavailable

    Example:
        >>> raise GRPCConnectionException("EmployeeService", "Connection timeout")
    """
    def __init__(self, service: str, message: str = "Failed to connect to service"):
        full_message = f"{message}: {service}"
        super().__init__(full_message, 503)


class GRPCException(APIException):
    """
    Exception untuk general GRPC errors

    Raised ketika terjadi error dari GRPC service call.

    HTTP Status Code: 502 Bad Gateway

    Example:
        >>> raise GRPCException("EmployeeService", "Internal server error")
    """
    def __init__(self, service: str, message: str):
        full_message = f"gRPC error dari {service}: {message}"
        super().__init__(full_message, 502)


class BusinessLogicException(APIException):
    """
    Exception untuk business logic errors

    Raised ketika operasi tidak dapat dilakukan karena business rules.

    HTTP Status Code: 422 Unprocessable Entity

    Example:
        >>> raise BusinessLogicException("Tidak dapat menghapus user yang masih memiliki attendance aktif")
    """
    def __init__(self, message: str):
        super().__init__(message, 422)


class ResourceLockedException(APIException):
    """
    Exception untuk locked resource

    Raised ketika resource sedang digunakan/locked oleh proses lain.

    HTTP Status Code: 423 Locked

    Example:
        >>> raise ResourceLockedException("Attendance sedang dalam proses approval")
    """
    def __init__(self, message: str = "Resource is locked"):
        super().__init__(message, 423)
