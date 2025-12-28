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
        name: str,
        phone: Optional[str] = None,
    ) -> User:
        """
        Create SSO user (if not exists), assign to apps, and sync to local User table.
        Returns the local User object.
        """
        from app.config.settings import settings

        app_codes = [settings.CLIENT_ID, settings.PM_APP_CODE]
        
        # First check if SSO user already exists by email
        existing_sso = await sso_client.get_user_by_email(email)
        sso_user = None
        
        if existing_sso:
            # User exists, just assign to apps
            sso_user = existing_sso
            await sso_client.assign_user_to_apps(sso_user["id"], app_codes)
            logger.info(f"SSO user {email} already exists, assigned to apps")
        else:
            # Create new SSO user
            create_result = await sso_client.create_user(
                email=email,
                name=name,
                phone=phone,
                role="user",
                app_codes=app_codes,
            )
            
            if not create_result.get("success"):
                error_msg = create_result.get("error", "Unknown error")
                # Check for specific constraint violations
                if "phone" in error_msg and "unique" in error_msg.lower():
                    raise ConflictException(f"Nomor telepon '{phone}' sudah digunakan oleh user lain")
                elif "email" in error_msg and "unique" in error_msg.lower():
                    raise ConflictException(f"Email '{email}' sudah digunakan")
                else:
                    raise ConflictException(f"Gagal membuat SSO user: {error_msg}")
            
            sso_user = create_result["user"]

        # Sync to local user table
        local_user = await user_queries.get_by_email(email)
        if not local_user:
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
        If SSO user not found, logs warning and updates local user only.
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
                error_msg = sso_result.get("error", "")
                if "tidak ditemukan" in error_msg or "not found" in error_msg.lower():
                    logger.warning(
                        f"SSO user {user_id} not found, updating local user only"
                    )
                else:
                    raise ConflictException(
                        f"Failed to update SSO user: {error_msg}"
                    )
            else:
                sso_user = sso_result.get("user", {})

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
        """Remove user from HRIS and PM apps (app-specific delete), deactivate local user."""
        from app.config.settings import settings
        
        if user_id:
            app_codes = [settings.CLIENT_ID, settings.PM_APP_CODE]
            result = await sso_client.remove_user_from_apps(user_id, app_codes)
            if not result.get("success"):
                logger.warning(f"Failed to remove user {user_id} from apps: {result.get('error')}")
            else:
                logger.info(f"Removed user {user_id} from apps {app_codes}, remaining: {result.get('remaining_apps')}")

            await user_commands.deactivate(user_id)

    @staticmethod
    async def restore_sso_user(
        sso_client: SSOUserGRPCClient, user_commands: UserCommands, user_id: str
    ) -> None:
        """Re-assign user to HRIS and PM apps, reactivate local user."""
        from app.config.settings import settings
        
        if user_id:
            app_codes = [settings.CLIENT_ID, settings.PM_APP_CODE]
            result = await sso_client.assign_user_to_apps(user_id, app_codes)
            if not result.get("success"):
                logger.warning(f"Failed to assign user {user_id} to apps: {result.get('error')}")
            else:
                logger.info(f"Assigned user {user_id} to apps {app_codes}")

            await user_commands.activate(user_id)
