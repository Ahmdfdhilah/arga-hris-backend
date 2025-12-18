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
        # 1. Create SSO User (Strict Sync)
        create_result = await sso_client.create_user(
            email=email,
            name=f"{first_name} {last_name}".strip(),
            phone=phone,
            gender=gender,
            role="user",
        )

        sso_user = None
        if not create_result.get("success"):
            # Check if user already exists
            existing_sso = await sso_client.get_user_by_email(email)
            if existing_sso:
                sso_user = existing_sso
            else:
                raise ConflictException(
                    f"Failed to create SSO user: {create_result.get('error')}"
                )
        else:
            sso_user = create_result["user"]

        # 2. Sync Local User
        local_user = await user_queries.get_by_email(email)
        if not local_user:
            # Create local user linked to SSO
            local_user = User(
                id=sso_user["id"],
                email=sso_user["email"],
                name=sso_user["name"],
                phone=sso_user.get("phone"),
                gender=sso_user.get("gender"),
                is_active=True,
                synced_at=datetime.utcnow(),
            )
            await user_commands.create(local_user)
        else:
            # Check ID mismatch
            if local_user.id != sso_user["id"]:
                logger.warning(
                    f"Local user ID mismatch for {email}. SSO ID: {sso_user['id']}, Local: {local_user.id}"
                )
                # In strict mode we might error, but for now allow reuse if email matches
                pass

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
        update_data keys: first_name, last_name, email, phone, gender.
        """
        local_user = await user_queries.get_by_id(user_id)
        if not local_user:
            raise NotFoundException(f"User with ID {user_id} not found")

        # 1. Prepare SSO Update Data
        sso_update_fields = {}

        # Handle Name Construction
        if "first_name" in update_data or "last_name" in update_data:
            existing_name = local_user.name or ""
            parts = existing_name.split(" ", 1)
            fn = parts[0] if len(parts) > 0 else ""
            ln = parts[1] if len(parts) > 1 else ""

            if "first_name" in update_data:
                fn = update_data["first_name"] or ""
            if "last_name" in update_data:
                ln = update_data["last_name"] or ""

            full_name = f"{fn} {ln}".strip()
            sso_update_fields["name"] = full_name

        if "email" in update_data:
            sso_update_fields["email"] = update_data["email"]
        if "phone" in update_data:
            sso_update_fields["phone"] = update_data["phone"]
        if "gender" in update_data:
            sso_update_fields["gender"] = update_data["gender"]

        # 2. Update SSO User
        if sso_update_fields:
            sso_result = await sso_client.update_user(
                user_id=local_user.id, **sso_update_fields
            )
            if not sso_result.get("success"):
                raise ConflictException(
                    f"Failed to update SSO user: {sso_result.get('error')}"
                )

            # 3. Update Local User based on SSO response (source of truth)
            sso_user = sso_result.get("user", {})
            local_user_update = {"synced_at": datetime.utcnow()}

            if "name" in sso_update_fields:
                local_user_update["name"] = sso_user.get(
                    "name", sso_update_fields["name"]
                )
            if "email" in sso_update_fields:
                local_user_update["email"] = sso_user.get(
                    "email", sso_update_fields["email"]
                )
            if "phone" in sso_update_fields:
                local_user_update["phone"] = sso_user.get(
                    "phone", sso_update_fields["phone"]
                )
            if "gender" in sso_update_fields:
                local_user_update["gender"] = sso_user.get(
                    "gender", sso_update_fields["gender"]
                )

            await user_commands.update(local_user.id, local_user_update)

    @staticmethod
    async def delete_sso_user(
        sso_client: SSOUserGRPCClient, user_commands: UserCommands, user_id: str
    ) -> None:
        """Delete SSO user and deactivate local user"""
        if user_id:
            # Delete in SSO
            result = await sso_client.delete_user(user_id)
            if not result.get("success"):
                raise ConflictException(
                    f"Failed to delete SSO user: {result.get('error')}"
                )

            # Deactivate locally
            await user_commands.deactivate(user_id)
