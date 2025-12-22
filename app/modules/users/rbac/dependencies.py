from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories import UserQueries
from app.modules.users.rbac.repositories import RoleQueries, RoleCommands
from app.modules.users.rbac.services.role_service import RoleService


def get_user_queries(db: PostgresDB) -> UserQueries:
    return UserQueries(db)


UserQueriesDep = Annotated[UserQueries, Depends(get_user_queries)]


def get_role_queries(db: PostgresDB) -> RoleQueries:
    return RoleQueries(db)


RoleQueriesDep = Annotated[RoleQueries, Depends(get_role_queries)]


def get_role_commands(db: PostgresDB) -> RoleCommands:
    return RoleCommands(db)


RoleCommandsDep = Annotated[RoleCommands, Depends(get_role_commands)]


def get_role_service(
    role_queries: RoleQueriesDep,
    role_commands: RoleCommandsDep,
    user_queries: UserQueriesDep,
) -> RoleService:
    return RoleService(role_queries, role_commands, user_queries)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
