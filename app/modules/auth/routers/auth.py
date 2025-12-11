"""
Auth Router

Endpoints for authentication operations like logout, token validation, etc.
"""

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import AuthServiceDep, TokenServiceDep
from app.modules.auth.schemas import (
    CurrentUserResponse,
    TokenInfoResponse,
    TokenValidateResponse,
    BlacklistStatsResponse,
    RefreshCacheResponse,
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
    Logout user by blacklisting current token

    This will:
    - Blacklist the current access token
    - Invalidate user cache
    - Token remains blacklisted until it expires naturally

    Note: This only logs out the current device/token.
    For logging out all devices, use /logout-all
    """
    await auth_service.logout(token)
    return create_success_response(message="Berhasil logout", data=None)


@router.post("/logout-all", response_model=DataResponse[None])
async def logout_all_sessions(
    auth_service: AuthServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[None]:
    """
    Logout user from ALL devices/sessions

    Use cases:
    - User changes password
    - Security breach detected
    - User wants to terminate all active sessions

    This will:
    - Revoke ALL user tokens across all devices
    - Invalidate user cache
    - User must login again on all devices
    """
    user_id = current_user.id
    await auth_service.logout_all_sessions(user_id)
    return create_success_response(message="Semua sesi telah dihentikan", data=None)


@router.post("/validate-token", response_model=DataResponse[TokenValidateResponse])
async def validate_token(
    token_service: TokenServiceDep,
    token: str = Depends(jwt_bearer),

) -> DataResponse[TokenValidateResponse]:
    """
    Validate if a token is still valid

    Checks:
    - Token signature validity
    - Token not expired
    - Token not blacklisted
    - User not globally revoked

    Returns: {"valid": true/false}
    """
    data = await token_service.validate_token_with_response(token)
    message = "Token is valid" if data.valid else "Token is invalid"
    return create_success_response(message=message, data=data)


@router.get("/token-info", response_model=DataResponse[TokenInfoResponse])
async def get_token_info(
    auth_service: AuthServiceDep,
    token: str = Depends(jwt_bearer),
) -> DataResponse[TokenInfoResponse]:
    """
    Get information about current token

    Useful for debugging and monitoring.
    Returns token metadata including:
    - user_id
    - jti (token ID)
    - exp (expiration time)
    - is_blacklisted status
    """
    data = await auth_service.get_token_info(token)
    return create_success_response(
        message="Token information berhasil diambil", data=data
    )


@router.post("/refresh-user-cache", response_model=DataResponse[RefreshCacheResponse])
@require_role(["hr_admin", "super_admin"])
async def refresh_user_cache(
    auth_service: AuthServiceDep,
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[RefreshCacheResponse]:
    """
    Manually refresh user cache (Admin only)

    Use cases:
    - After changing user roles/permissions
    - After updating user profile
    - When cache is suspected to be stale

    This will:
    - Invalidate old cache
    - Fetch fresh data from DB
    - Cache new data
    """
    data = await auth_service.refresh_user_cache(user_id)
    return create_success_response(
        message="User cache refresh skipped (caching disabled)", data=data
    )


@router.get("/blacklist-stats", response_model=DataResponse[BlacklistStatsResponse])
@require_role(["hr_admin", "super_admin"])
async def get_blacklist_stats(
    auth_service: AuthServiceDep,
    token_service: TokenServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[BlacklistStatsResponse]:
    """
    Get blacklist statistics (Admin only)

    Returns:
    - Number of blacklisted tokens
    - Number of globally revoked users

    Useful for monitoring and debugging.
    """
    data = await token_service.get_blacklist_stats_with_response()
    return create_success_response(
        message="Blacklist statistics retrieved successfully", data=data
    )


@router.get("/me", response_model=DataResponse[CurrentUserResponse])
async def get_current_user_info(
    auth_service: AuthServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[CurrentUserResponse]:
    """
    Get current authenticated user information

    Returns complete user data including:
    - User profile
    - Roles
    - Permissions
    - Employee ID (if linked)
    """
    data = await auth_service.get_current_user_info(current_user)
    return create_success_response(
        message="Current user information retrieved successfully", data=data
    )
