"""
Centralized middleware and exception handler configuration.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import APIException
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.error_handler import (
    api_exception_handler,
    request_validation_exception_handler,
    pydantic_validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)


def setup_middleware(app: FastAPI) -> None:
    """
    Setup all middleware and exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Setup CORS middleware
    setup_cors(app)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Register exception handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
