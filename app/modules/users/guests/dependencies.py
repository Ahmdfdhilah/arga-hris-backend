from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories.user_repository import UserRepository
from app.modules.users.guests.repositories.guest_repository import GuestRepository
from app.modules.users.rbac.repositories.role_repository import RoleRepository


def get_user_repository(db: PostgresDB) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_guest_repository(db: PostgresDB) -> GuestRepository:
    return GuestRepository(db)


GuestRepositoryDep = Annotated[GuestRepository, Depends(get_guest_repository)]


def get_role_repository(db: PostgresDB) -> RoleRepository:
    return RoleRepository(db)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]
