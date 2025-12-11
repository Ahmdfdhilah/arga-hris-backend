from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.core.utils.logging import setup_logging
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
from app.modules.auth.routers import auth
from app.modules.users.rbac.routers import roles
from app.modules.employees.routers import employees
from app.modules.org_units.routers import org_units
from app.modules.attendance.routers import attendances
from app.modules.leave_requests.routers import leave_requests
from app.modules.work_submissions.routers import work_submissions
from app.modules.scheduled_jobs.routers import scheduled_jobs
from app.modules.dashboard.routers import dashboard
from app.tasks.scheduler_startup import setup_scheduler, shutdown_scheduler

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager untuk startup dan shutdown events.
    """
    await setup_scheduler()

    yield

    # Shutdown: Stop scheduler
    await shutdown_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

setup_cors(app)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )


app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(roles.router, prefix=settings.API_PREFIX)
app.include_router(employees.router, prefix=settings.API_PREFIX)
app.include_router(org_units.router, prefix=settings.API_PREFIX)
app.include_router(attendances.router, prefix=settings.API_PREFIX)
app.include_router(leave_requests.router, prefix=settings.API_PREFIX)
app.include_router(work_submissions.router, prefix=settings.API_PREFIX)
app.include_router(scheduled_jobs.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
