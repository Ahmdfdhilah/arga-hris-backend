"""
User Events Module - Auto-register handlers

Import this module at app startup to register all user event handlers
with the EventHandlerRegistry.
"""

from app.modules.users.users.events.handlers import (
    UserCreatedHandler,
    UserUpdatedHandler,
    UserDeletedHandler,
)

__all__ = [
    "UserCreatedHandler",
    "UserUpdatedHandler",
    "UserDeletedHandler",
]
