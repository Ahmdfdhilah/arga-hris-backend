from app.core.exceptions.base import APIException


class InternalServerException(APIException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message, 500)


class NotImplementedException(APIException):
    """501 Not Implemented"""
    def __init__(self, message: str = "Not Implemented"):
        super().__init__(message, 501)


class ServiceUnavailableException(APIException):
    """503 Service Unavailable"""
    def __init__(self, message: str = "Service Unavailable"):
        super().__init__(message, 503)
