"""
Auth Router - Simplified for SSO Integration

Most auth is handled by SSO directly. These endpoints are for compatibility.
"""

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import AuthServiceDep
from app.modules.auth.schemas import (
    CurrentUserResponse,
    TokenValidateResponse,
)
from app.core.dependencies.auth import get_current_user, jwt_bearer
from app.core.security.rbac import require_role
from app.core.schemas import CurrentUser, DataResponse, create_success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/logout", response_model=DataResponse[None])
async def logout(
    auth_service: AuthServiceDep,
    token: str = Depends(jwt_bearer),
) -> DataResponse[None]:
    """
    Logout current session.
    
    Note: For single device logout, frontend should call SSO directly.
    This endpoint is for backward compatibility.
    """
    await auth_service.logout(token)
    return create_success_response(message="Berhasil logout", data=None)


@router.post("/logout-all", response_model=DataResponse[None])
async def logout_all_sessions(
    auth_service: AuthServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[None]:
    """
    Logout user from ALL devices/sessions via SSO.
    """
    await auth_service.logout_all_sessions(current_user.id)
    return create_success_response(message="Semua sesi telah dihentikan", data=None)


@router.post("/validate-token", response_model=DataResponse[TokenValidateResponse])
async def validate_token(
    auth_service: AuthServiceDep,
    token: str = Depends(jwt_bearer),
) -> DataResponse[TokenValidateResponse]:
    """
    Validate if a token is still valid via SSO.
    """
    is_valid = await auth_service.validate_token(token)
    return create_success_response(
        message="Token valid" if is_valid else "Token invalid",
        data=TokenValidateResponse(valid=is_valid)
    )


@router.get("/me", response_model=DataResponse[CurrentUserResponse])
async def get_current_user_info(
    auth_service: AuthServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[CurrentUserResponse]:
    """
    Get current authenticated user information.
    Combines SSO user data with HRIS-specific roles/permissions.
    """
    data = await auth_service.get_current_user_info(current_user)
    return create_success_response(
        message="Current user information retrieved successfully", data=data
    )
