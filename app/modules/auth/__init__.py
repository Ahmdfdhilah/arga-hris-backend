"""Auth module - simplified for SSO integration."""

from app.modules.auth.routers.auth import router as auth_router

__all__ = ["auth_router"]
