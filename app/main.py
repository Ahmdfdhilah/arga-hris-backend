"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from app.config.settings import settings
from app.core.utils.logging import setup_logging
from app.core.utils.lifespan import lifespan
from app.middleware import setup_middleware
from app.core.routers import setup_routers

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ARGA HRIS Service - Human Resources Information System",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

# Setup middleware and exception handlers
setup_middleware(app)

# Setup routers
setup_routers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
