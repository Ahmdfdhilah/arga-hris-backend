"""
System and health check endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.config.settings import settings

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )
