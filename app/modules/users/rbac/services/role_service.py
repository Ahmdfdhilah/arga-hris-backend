from typing import List
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.schemas.responses import (
    RoleResponse,
    PermissionResponse,
    UserRolesPermissionsResponse,
    RoleAssignmentResponse,
    MultipleRoleAssignmentResponse,
)
from app.core.exceptions import NotFoundException
from app.core.schemas import (
    DataResponse,
    create_success_response,
)


class RoleService:
    def __init__(
        self,
        role_repo: RoleRepository,
        user_repo: UserRepository,
    ):
        self.role_repo = role_repo
        self.user_repo = user_repo

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Get list of role names for a user"""
        return await self.role_repo.get_user_roles(user_id)

    async def get_user_permissions(self, user_id: int) -> List[str]:
        """Get list of permission codes for a user"""
        return await self.role_repo.get_user_permissions(user_id)

    async def assign_role_by_name(
        self, user_id: int, role_name: str
    ) -> DataResponse[RoleAssignmentResponse]:
        """
        Assign role ke user berdasarkan nama role

        Args:
            user_id: ID user
            role_name: Nama role yang akan di-assign

        Returns:
            DataResponse dengan RoleAssignmentResponse

        Raises:
            NotFoundException: Jika user atau role tidak ditemukan
        """
        # Validate user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        role = await self.role_repo.get_role_by_name(role_name)
        if not role:
            raise NotFoundException(f"Role '{role_name}' tidak ditemukan")

        await self.role_repo.assign_role(user_id, role.id)

        response_data = RoleAssignmentResponse(
            user_id=user_id,
            role_name=role_name
        )

        return create_success_response(
            message=f"Role '{role_name}' berhasil di-assign ke user",
            data=response_data
        )

    async def remove_role_by_name(
        self, user_id: int, role_name: str
    ) -> DataResponse[RoleAssignmentResponse]:
        """
        Remove role dari user berdasarkan nama role

        Args:
            user_id: ID user
            role_name: Nama role yang akan di-remove

        Returns:
            DataResponse dengan RoleAssignmentResponse

        Raises:
            NotFoundException: Jika user atau role tidak ditemukan
        """
        # Validate user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        role = await self.role_repo.get_role_by_name(role_name)
        if not role:
            raise NotFoundException(f"Role '{role_name}' tidak ditemukan")

        await self.role_repo.remove_role(user_id, role.id)

        response_data = RoleAssignmentResponse(
            user_id=user_id,
            role_name=role_name
        )

        return create_success_response(
            message=f"Role '{role_name}' berhasil di-remove dari user",
            data=response_data
        )

    async def assign_multiple_roles(
        self, user_id: int, role_names: List[str]
    ) -> DataResponse[MultipleRoleAssignmentResponse]:
        """
        Assign multiple roles ke user sekaligus

        Args:
            user_id: ID user
            role_names: List nama role yang akan di-assign

        Returns:
            DataResponse dengan MultipleRoleAssignmentResponse

        Raises:
            NotFoundException: Jika user atau salah satu role tidak ditemukan
        """
        # Validate user exists
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        for role_name in role_names:
            role = await self.role_repo.get_role_by_name(role_name)
            if not role:
                raise NotFoundException(f"Role '{role_name}' tidak ditemukan")
            await self.role_repo.assign_role(user_id, role.id)

        response_data = MultipleRoleAssignmentResponse(
            user_id=user_id,
            roles=role_names
        )

        return create_success_response(
            message="Multiple roles berhasil di-assign ke user",
            data=response_data
        )

    async def get_user_roles_and_permissions(
        self, user_id: int
    ) -> DataResponse[UserRolesPermissionsResponse]:
        """
        Get roles dan permissions user

        Args:
            user_id: ID user

        Returns:
            DataResponse dengan UserRolesPermissionsResponse

        Raises:
            NotFoundException: Jika user tidak ditemukan
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(f"User dengan ID {user_id} tidak ditemukan")

        roles = await self.role_repo.get_user_roles(user_id)
        permissions = await self.role_repo.get_user_permissions(user_id)

        response_data = UserRolesPermissionsResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=roles,
            permissions=permissions,
        )

        return create_success_response(
            message="User roles dan permissions berhasil diambil",
            data=response_data
        )

    async def get_all_roles(self) -> DataResponse[List[RoleResponse]]:
        """
        Get semua roles yang tersedia

        Returns:
            DataResponse dengan list RoleResponse
        """
        roles = await self.role_repo.get_all_roles()
        # Convert SQLAlchemy models to Pydantic schemas
        roles_data: List[RoleResponse] = [
            RoleResponse.model_validate(role) for role in roles
        ]
        return create_success_response(
            message="Roles berhasil diambil",
            data=roles_data
        )

    async def get_all_permissions(self) -> DataResponse[List[PermissionResponse]]:
        """
        Get semua permissions yang tersedia

        Returns:
            DataResponse dengan list PermissionResponse
        """
        permissions = await self.role_repo.get_all_permissions()
        # Convert SQLAlchemy models to Pydantic schemas
        permissions_data: List[PermissionResponse] = [
            PermissionResponse.model_validate(perm) for perm in permissions
        ]
        return create_success_response(
            message="Permissions berhasil diambil",
            data=permissions_data
        )
