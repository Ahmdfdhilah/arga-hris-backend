from datetime import datetime
from typing import Optional, Dict, Any
import logging

from app.modules.users.users.models.user import User
from app.modules.users.users.repositories import UserQueries, UserCommands
from app.grpc.clients.sso_client import SSOUserGRPCClient
from app.core.exceptions import ConflictException, NotFoundException

logger = logging.getLogger(__name__)


class SSOSyncUtil:
    """Utility for synchronizing Employee data with SSO Service"""

    @staticmethod
    async def create_sso_user(
        sso_client: SSOUserGRPCClient,
        user_queries: UserQueries,
        user_commands: UserCommands,
        email: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> User:
        """
        Create SSO user (if not exists) and sync to local User table.
        Returns the local User object.
        """
        create_result = await sso_client.create_user(
            email=email,
            name=f"{first_name} {last_name}".strip(),
            phone=phone,
            gender=gender,
            role="user",
        )

        sso_user = None
        if not create_result.get("success"):
            existing_sso = await sso_client.get_user_by_email(email)
            if existing_sso:
                sso_user = existing_sso
            else:
                raise ConflictException(
                    f"Failed to create SSO user: {create_result.get('error')}"
                )
        else:
            sso_user = create_result["user"]

        local_user = await user_queries.get_by_email(email)
        if not local_user:
            # Create new user model object
            new_user = User(
                id=sso_user["id"],
                email=sso_user["email"],
                name=sso_user["name"],
                phone=sso_user.get("phone"),
                gender=sso_user.get("gender"),
                is_active=True,
                synced_at=datetime.utcnow(),
            )
            local_user = await user_commands.create(new_user)
        else:
            if local_user.id != sso_user["id"]:
                logger.warning(
                    f"Local user ID mismatch for {email}. SSO ID: {sso_user['id']}, Local: {local_user.id}"
                )

        return local_user

    @staticmethod
    async def update_sso_user(
        sso_client: SSOUserGRPCClient,
        user_queries: UserQueries,
        user_commands: UserCommands,
        user_id: str,
        update_data: Dict[str, Any],
    ) -> None:
        """
        Update SSO user details and sync local User table.
        Only syncs email and phone to SSO (name and gender are not synced on update).
        """
        local_user = await user_queries.get_by_id(user_id)
        if not local_user:
            raise NotFoundException(f"User with ID {user_id} not found")

        sso_update_fields = {}

        if "email" in update_data:
            sso_update_fields["email"] = update_data["email"]
        if "phone" in update_data:
            sso_update_fields["phone"] = update_data["phone"]

        if sso_update_fields:
            sso_result = await sso_client.update_user(
                user_id=local_user.id, **sso_update_fields
            )
            if not sso_result.get("success"):
                raise ConflictException(
                    f"Failed to update SSO user: {sso_result.get('error')}"
                )

            sso_user = sso_result.get("user", {})

            # Update user model object directly
            local_user.synced_at = datetime.utcnow()
            if "email" in sso_update_fields:
                local_user.email = sso_user.get(
                    "email", sso_update_fields["email"]
                )
            if "phone" in sso_update_fields:
                local_user.phone = sso_user.get(
                    "phone", sso_update_fields["phone"]
                )

            await user_commands.update(local_user)

    @staticmethod
    async def delete_sso_user(
        sso_client: SSOUserGRPCClient, user_commands: UserCommands, user_id: str
    ) -> None:
        """Soft delete SSO user and deactivate local user"""
        if user_id:
            result = await sso_client.delete_user(user_id)
            if not result.get("success"):
                logger.warning(f"Failed to delete SSO user {user_id}: {result.get('error')}")

            # Deactivate locally
            await user_commands.deactivate(user_id)

    @staticmethod
    async def restore_sso_user(
        sso_client: SSOUserGRPCClient, user_commands: UserCommands, user_id: str
    ) -> None:
        """Restore SSO user and reactivate local user"""
        if user_id:
            result = await sso_client.update_user(user_id=user_id, status="active")
            if not result.get("success"):
                logger.warning(f"Failed to restore SSO user {user_id}: {result.get('error')}")

            await user_commands.activate(user_id)
