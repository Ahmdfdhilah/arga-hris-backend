from app.core.exceptions.base import APIException


class BadRequestException(APIException):
    """400 Bad Request"""
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message, 400)


class UnauthorizedException(APIException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenException(APIException):
    """403 Forbidden"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class NotFoundException(APIException):
    """404 Not Found"""
    def __init__(self, message: str = "Not Found"):
        super().__init__(message, 404)


class ConflictException(APIException):
    """409 Conflict"""
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, 409)


class UnprocessableEntityException(APIException):
    """422 Unprocessable Entity"""
    def __init__(self, message: str = "Unprocessable Entity"):
        super().__init__(message, 422)
