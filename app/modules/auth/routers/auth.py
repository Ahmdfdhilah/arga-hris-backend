"""Auth Router - Simplified for SSO Integration.

Only /me endpoint for getting current user info.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies.auth import get_current_user
from app.core.schemas import CurrentUser, DataResponse, create_success_response
from app.modules.auth.schemas import CurrentUserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=DataResponse[CurrentUserResponse])
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[CurrentUserResponse]:
    """Get current authenticated user information."""
    return create_success_response(
        message="Current user info",
        data=CurrentUserResponse(
            id=current_user.id,  # SSO UUID
            name=current_user.name,
            email=current_user.email,
            avatar_url=current_user.avatar_url,
            sso_role=current_user.sso_role,
            employee_id=current_user.employee_id,
            org_unit_id=current_user.org_unit_id,
            roles=current_user.roles,
            permissions=current_user.permissions,
            is_active=current_user.is_active,
        ),
    )
