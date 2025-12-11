from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.modules.users.rbac.services.role_service import RoleService


def get_user_repository(db: PostgresDB) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


def get_role_service(
    role_repo: RoleRepositoryDep,
    user_repo: UserRepositoryDep,
) -> RoleService:
    return RoleService(role_repo, user_repo)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
