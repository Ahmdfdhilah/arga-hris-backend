"""
User Event Handlers - Handle SSO user events

SSO is the master for user profile data.
These handlers sync the local User replica when SSO publishes events.
"""

from app.core.messaging.consumer import handles, BaseEventHandler, DomainEvent
from app.config.database import get_db_context


@handles("user.created")
class UserCreatedHandler(BaseEventHandler):
    """
    Sync user from SSO when user.created event received.

    Idempotent: Uses sync_from_sso which is an upsert operation.
    """

    async def handle(self, event: DomainEvent) -> None:
        from app.modules.users.users.repositories import UserCommands

        async with get_db_context() as db:
            repo = UserCommands(db)

            await repo.sync_from_sso(
                sso_id=str(event.entity_id),
                name=event.data.get("name"),
                email=event.data.get("email"),
                phone=event.data.get("phone"),
                gender=event.data.get("gender"),
                avatar_path=event.data.get("avatar_path"),
            )

            await db.commit()
            self.logger.info(f"Synced user from SSO: {event.entity_id}")


@handles("user.updated")
class UserUpdatedHandler(BaseEventHandler):
    """
    Sync user profile updates from SSO.

    Idempotent: Uses sync_from_sso which is an upsert operation.
    """

    async def handle(self, event: DomainEvent) -> None:
        from app.modules.users.users.repositories import UserQueries, UserCommands

        async with get_db_context() as db:
            queries = UserQueries(db)
            commands = UserCommands(db)

            existing = await queries.get_by_id(str(event.entity_id))
            if not existing:
                self.logger.warning(
                    f"User not found locally, skipping update: {event.entity_id}"
                )
                return

            await commands.sync_from_sso(
                sso_id=str(event.entity_id),
                email=event.data.get("email"),
                phone=event.data.get("phone"),
                avatar_path=event.data.get("avatar_path"),
            )

            await db.commit()
            self.logger.info(f"Updated user from SSO: {event.entity_id}")


@handles("user.deleted")
class UserDeletedHandler(BaseEventHandler):
    """
    Deactivate user when deleted in SSO.

    Idempotent: Deactivating an already inactive user is safe.
    """

    async def handle(self, event: DomainEvent) -> None:
        from app.modules.users.users.repositories import UserQueries, UserCommands

        async with get_db_context() as db:
            queries = UserQueries(db)
            commands = UserCommands(db)

            user = await queries.get_by_id(str(event.entity_id))
            if not user:
                self.logger.warning(
                    f"User not found locally, skipping delete: {event.entity_id}"
                )
                return

            if user.is_active:
                await commands.deactivate(user.id)
                await db.commit()
                self.logger.info(f"Deactivated user from SSO: {event.entity_id}")
            else:
                self.logger.debug(f"User already inactive: {event.entity_id}")
