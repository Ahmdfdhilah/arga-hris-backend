from typing import Annotated
from fastapi import Depends
from app.core.dependencies.database import PostgresDB
from app.modules.users.users.repositories import UserQueries, UserCommands


def get_user_queries(db: PostgresDB) -> UserQueries:
    return UserQueries(db)


def get_user_commands(db: PostgresDB) -> UserCommands:
    return UserCommands(db)


UserQueriesDep = Annotated[UserQueries, Depends(get_user_queries)]
UserCommandsDep = Annotated[UserCommands, Depends(get_user_commands)]
