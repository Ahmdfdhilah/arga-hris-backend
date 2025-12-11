from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import APIException
from app.core.schemas.helpers import create_error_response
from app.core.utils.logging import get_logger
from app.core.utils.validation import translate_validation_error

logger = get_logger(__name__)


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler untuk semua APIException

    APIException sudah memiliki status_code dan message,
    jadi tinggal return dengan format yang sesuai.
    """
    if not isinstance(exc, APIException):
        return JSONResponse(
            status_code=500,
            content=create_error_response("Unexpected error").model_dump(),
        )
    
    logger.error(f"API Exception: {exc.status_code} - {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.message).model_dump(),
    )


async def request_validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler untuk validation error dari FastAPI request"""
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=500,
            content=create_error_response("Unexpected error").model_dump(),
        )
    
    errors = []
    for error in exc.errors():
        translated = translate_validation_error(error)
        errors.append(translated)
    
    error_message = "; ".join(errors)
    logger.error(f"Validation error: {error_message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Data tidak valid",
            "errors": errors,
            "data": None,
        },
    )


async def pydantic_validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler untuk validation error dari Pydantic model"""
    if not isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=500,
            content=create_error_response("Unexpected error").model_dump(),
        )
    
    errors = []
    for error in exc.errors():
        translated = translate_validation_error(error)
        errors.append(translated)
    
    error_message = "; ".join(errors)
    logger.error(f"Validation error: {error_message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Data tidak valid",
            "errors": errors,
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler untuk validation error generic"""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content=create_error_response("Validation error").model_dump(),
    )


async def sqlalchemy_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler untuk database errors"""
    if not isinstance(exc, SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content=create_error_response("Unexpected error").model_dump(),
        )
    
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=create_error_response("Database operation failed").model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler untuk unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=create_error_response("An unexpected error occurred").model_dump(),
    )
