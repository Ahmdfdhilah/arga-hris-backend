from functools import wraps
from typing import List, Union
from app.core.exceptions import ForbiddenException


def require_permission(permission: Union[str, List[str]], require_all: bool = False):
    """
    Decorator to require specific permission(s) for an endpoint.

    Args:
        permission: Single permission string or list of permissions
        require_all: If True, user must have ALL permissions. If False, user needs ANY permission.

    Usage:
        @require_permission("employee.read")
        @require_permission(["employee.read", "employee.update"], require_all=True)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise ForbiddenException("Autentikasi pengguna diperlukan")

            # Super admin bypass
            user_roles = current_user.get("roles", []) if isinstance(current_user, dict) else getattr(current_user, "roles", [])
            if "super_admin" in user_roles:
                return await func(*args, **kwargs)

            # Check permissions
            user_permissions = current_user.get("permissions", []) if isinstance(current_user, dict) else getattr(current_user, "permissions", [])

            if isinstance(permission, str):
                # Single permission check
                if permission not in user_permissions:
                    raise ForbiddenException(
                        f"Akses ditolak. Memerlukan izin: {permission}"
                    )

            elif isinstance(permission, list):
                # Multiple permissions check
                if require_all:
                    # User must have ALL permissions
                    missing = [p for p in permission if p not in user_permissions]
                    if missing:
                        raise ForbiddenException(
                            f"Akses ditolak. Memerlukan semua izin: {', '.join(permission)}"
                        )
                else:
                    # User must have ANY permission
                    if not any(p in user_permissions for p in permission):
                        raise ForbiddenException(
                            f"Akses ditolak. Memerlukan salah satu izin: {', '.join(permission)}"
                        )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Union[str, List[str]]):
    """
    Decorator to require specific role(s) for an endpoint.

    Args:
        role: Single role string or list of roles

    Usage:
        @require_role("hr_admin")
        @require_role(["hr_admin", "super_admin"])
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")

            if not current_user:
                raise ForbiddenException("Autentikasi pengguna diperlukan")

            # Get user roles
            user_roles = current_user.get("roles", []) if isinstance(current_user, dict) else getattr(current_user, "roles", [])

            if isinstance(role, str):
                # Single role check
                if role not in user_roles:
                    raise ForbiddenException(f"Akses ditolak. Memerlukan role: {role}")

            elif isinstance(role, list):
                # Multiple roles check (user needs ANY of the roles)
                if not any(r in user_roles for r in role):
                    raise ForbiddenException(
                        f"Akses ditolak. Memerlukan salah satu role: {', '.join(role)}"
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def has_permission(user, permission: str) -> bool:
    """
    Helper function to check if user has a specific permission.

    Args:
        user: User dict or object with permissions attribute
        permission: Permission code to check

    Returns:
        True if user has permission, False otherwise
    """
    if not user:
        return False

    # Super admin has all permissions
    user_roles = user.get("roles", []) if isinstance(user, dict) else getattr(user, "roles", [])
    if "super_admin" in user_roles:
        return True

    user_permissions = user.get("permissions", []) if isinstance(user, dict) else getattr(user, "permissions", [])
    return permission in user_permissions


def has_role(user, role: str) -> bool:
    """
    Helper function to check if user has a specific role.

    Args:
        user: User dict or object with roles attribute
        role: Role name to check

    Returns:
        True if user has role, False otherwise
    """
    if not user:
        return False

    user_roles = user.get("roles", []) if isinstance(user, dict) else getattr(user, "roles", [])
    return role in user_roles


def has_any_role(user, roles: List[str]) -> bool:
    """
    Helper function to check if user has any of the specified roles.

    Args:
        user: User dict or object with roles attribute
        roles: List of role names to check

    Returns:
        True if user has any of the roles, False otherwise
    """
    if not user:
        return False

    user_roles = user.get("roles", []) if isinstance(user, dict) else getattr(user, "roles", [])
    return any(role in user_roles for role in roles)
