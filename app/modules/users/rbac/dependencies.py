from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.repositories.role_repository import RoleRepository
from app.modules.users.rbac.services.role_service import RoleService


def get_user_queries(db: PostgresDB) -> UserQueries:
    return UserQueries(db)


UserQueriesDep = Annotated[UserQueries, Depends(get_user_queries)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


def get_role_service(
    role_repo: RoleRepositoryDep,
    user_queries: UserQueriesDep,
) -> RoleService:
    return RoleService(role_repo, user_queries)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
