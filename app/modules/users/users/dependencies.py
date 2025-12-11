from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories.user_repository import UserRepository

def get_user_repository(db: PostgresDB) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]