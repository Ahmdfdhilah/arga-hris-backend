from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from app.modules.users.rbac.dependencies import RoleServiceDep
from app.modules.users.rbac.schemas.requests import (
    AssignRoleRequest,
    RemoveRoleRequest,
    AssignRolesRequest,
)
from app.modules.users.rbac.schemas.responses import (
    RoleResponse,
    PermissionResponse,
    UserRolesPermissionsResponse,
    RoleAssignmentResponse,
    MultipleRoleAssignmentResponse,
)
from app.core.dependencies.auth import get_current_user
from app.core.security.rbac import require_role, require_permission
from app.core.schemas import DataResponse, CurrentUser

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.get("/permissions", response_model=DataResponse[List[PermissionResponse]])
@require_permission("roles:read")
async def list_all_permissions(
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[PermissionResponse]]:
    """
    Get all available permissions (Admin only)

    Returns:
        List of all permissions in the system

    Permission required: roles:read
    """
    return await service.get_all_permissions()


@router.get("", response_model=DataResponse[List[RoleResponse]])
@require_permission("roles:read")
async def list_all_roles(
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[List[RoleResponse]]:
    """
    Get all available roles (Admin only)

    Returns:
        List of all roles in the system

    Permission required: roles:read
    """
    return await service.get_all_roles()


@router.get("/{user_id}", response_model=DataResponse[UserRolesPermissionsResponse])
@require_permission("roles:read")
async def get_user_roles_and_permissions(
    user_id: str,
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[UserRolesPermissionsResponse]:
    """
    Get user's roles and permissions (Admin only)

    Returns:
        UserRolesPermissionsResponse dengan roles dan permissions user

    Permission required: roles:read
    """
    return await service.get_user_roles_and_permissions(user_id)


@router.post("/{user_id}/assign", response_model=DataResponse[RoleAssignmentResponse])
@require_permission("roles:write")
async def assign_role_to_user(
    user_id: str,
    request: AssignRoleRequest,
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[RoleAssignmentResponse]:
    """
    Assign a role to user (Admin only)

    Args:
        user_id: User ID
        request: Role assignment request

    Returns:
        Success response

    Permission required: roles:write
    """
    return await service.assign_role_by_name(user_id, request.role_name)


@router.post("/{user_id}/remove", response_model=DataResponse[RoleAssignmentResponse])
@require_permission("roles:write")
async def remove_role_from_user(
    user_id: str,
    request: RemoveRoleRequest,
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[RoleAssignmentResponse]:
    """
    Remove a role from user (Admin only)

    Args:
        user_id: User ID
        request: Role removal request

    Returns:
        Success response

    Permission required: roles:write
    """
    return await service.remove_role_by_name(user_id, request.role_name)


@router.post(
    "/{user_id}/assign-multiple",
    response_model=DataResponse[MultipleRoleAssignmentResponse],
)
@require_permission("roles:write")
async def assign_multiple_roles_to_user(
    user_id: str,
    request: AssignRolesRequest,
    service: RoleServiceDep,
    current_user: CurrentUser = Depends(get_current_user),
) -> DataResponse[MultipleRoleAssignmentResponse]:
    """
    Assign multiple roles to user at once (Admin only)

    Args:
        user_id: User ID
        request: Multiple roles assignment request

    Returns:
        Success response

    Permission required: roles:write
    """
    return await service.assign_multiple_roles(user_id, request.role_names)
