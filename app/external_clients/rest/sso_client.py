"""
SSO REST API Client

Client for syncing user data with SSO service via REST API with API key authentication.

**Architecture Pattern: Master-Slave Synchronization**
- HRIS is the MASTER data source for user management
- SSO is the SLAVE that gets synchronized automatically
- Changes in HRIS (create/update/deactivate) are propagated to SSO
- SSO sync failures do NOT block HRIS operations (fire-and-forget pattern)

**Smart Routing:**
- Regular users → POST /api/users (creates User only)
- Guest users → POST /api/guest (creates User + GuestAccount + auto-generates password)

**Authentication:**
All requests use X-API-Key header for service-to-service authentication.
API key configured in SSO_SERVICE_API_KEY environment variable.

**Error Handling:**
SSO sync uses fire-and-forget pattern:
- Success: user.sso_id is updated with SSO User.id
- Failure: Warning logged, HRIS operation continues
- Rationale: HRIS is source of truth, SSO downtime shouldn't block operations

**Data Mapping:**
- HRIS user.sso_id ←→ SSO User.id (primary key in users table)
- Guest metadata (valid_from, valid_until, etc) synced to SSO GuestAccount
- Passwords NOT stored in HRIS (SSO generates and manages them)
"""

import httpx
from typing import Dict, Any, Optional
from app.config.settings import settings


class SSOClient:
    """
    REST API client for SSO service with smart routing and error tolerance

    Provides single interface for creating users and guests while routing
    to appropriate SSO endpoints based on account type.

    Configuration:
        SSO_SERVICE_URL: Base URL of SSO service (e.g., http://localhost:8001)
        SSO_SERVICE_API_KEY: API key for service-to-service auth

    Methods:
        create_user(): Smart routing - calls appropriate endpoint based on account_type
        update_user(): Update user data in SSO
        activate_user(): Activate user account in SSO
        deactivate_user(): Deactivate user account in SSO
        get_user(): Fetch user data from SSO
        get_user_by_email(): Fetch user by email from SSO
    """

    def __init__(self):
        self.base_url = settings.SSO_SERVICE_URL
        self.api_key = settings.SSO_SERVICE_API_KEY
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with API key for service-to-service authentication"""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        account_type: str = "regular",
        guest_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create user in SSO service (smart routing to appropriate endpoint)

        Args:
            email: User email
            first_name: User first name
            last_name: User last name
            account_type: Account type (regular/guest)
            password: User password (optional - will generate random if None)
            guest_metadata: Guest metadata (for guest users - required if account_type='guest')

        Returns:
            Dict with user data from SSO (including sso_id)

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        if account_type == "guest":
            # Route to guest endpoint
            return await self._create_guest_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                guest_metadata=guest_metadata or {},
            )
        else:
            # Route to regular user endpoint
            return await self._create_regular_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
            )

    async def _create_regular_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
    ) -> Dict[str, Any]:
        """
        Create regular user via POST /api/users

        Args:
            email: User email
            first_name: User first name
            last_name: User last name

        Returns:
            Dict with user data including sso_id

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/users/",  # Add trailing slash to avoid redirect
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            # Ensure sso_id field exists (use id if sso_id not present)
            if "sso_id" not in data and "id" in data:
                data["sso_id"] = data["id"]

            return data

    async def _create_guest_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        guest_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create guest user via POST /api/guest

        Args:
            email: User email
            first_name: User first name
            last_name: User last name
            guest_metadata: Dict with guest_type, valid_from, valid_until, etc.

        Returns:
            Dict with user data including sso_id and temporary_password

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        # Build payload for guest creation
        # Ensure datetime values are ISO format strings (FastAPI will parse to datetime)
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "guest_type": str(guest_metadata.get("guest_type", "visitor")),  # Ensure string
            "valid_until": guest_metadata.get("valid_until"),
        }

        # Add optional fields
        if "valid_from" in guest_metadata:
            payload["valid_from"] = guest_metadata["valid_from"]

        if "notes" in guest_metadata:
            payload["notes"] = guest_metadata["notes"]

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/guest/",  # Add trailing slash to avoid redirect
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            # Response from guest endpoint already has sso_id
            # But ensure it exists for consistency
            if "sso_id" not in data and "user_id" in data:
                data["sso_id"] = data["user_id"]

            return data

    async def update_user(
        self,
        sso_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        guest_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update user in SSO service

        Args:
            sso_id: SSO user ID
            first_name: User first name
            last_name: User last name
            is_active: User active status
            guest_metadata: Guest metadata (for guest users)

        Returns:
            Dict with updated user data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        payload = {}

        if first_name is not None:
            payload["first_name"] = first_name

        if last_name is not None:
            payload["last_name"] = last_name

        if is_active is not None:
            payload["is_active"] = is_active

        if guest_metadata is not None:
            payload["guest_metadata"] = guest_metadata

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.put(
                f"{self.base_url}/api/users/sso/{sso_id}",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def deactivate_user(self, sso_id: str) -> Dict[str, Any]:
        """
        Deactivate user in SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with success message

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/users/sso/{sso_id}/deactivate",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def activate_user(self, sso_id: str) -> Dict[str, Any]:
        """
        Activate user in SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with success message

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/users/sso/{sso_id}/activate",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_user(self, sso_id: str) -> Dict[str, Any]:
        """
        Get user from SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with user data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/api/users/sso/{sso_id}",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def delete_user(self, sso_id: int) -> Dict[str, Any]:
        """
        Delete user in SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with success message (empty dict for 204 response)

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/api/users/sso/{sso_id}",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            # 204 No Content returns empty body
            if response.status_code == 204:
                return {}
            return response.json()

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user from SSO service by email

        Args:
            email: User email

        Returns:
            Dict with user data or None if not found

        Raises:
            httpx.HTTPStatusError: If request fails (except 404)
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/users/by-email/{email}",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise

    async def assign_application_to_user(
        self,
        sso_id: int,
        application_id: int,
    ) -> Dict[str, Any]:
        """
        Assign an application to a user in SSO service

        Args:
            sso_id: SSO user ID
            application_id: Application ID to assign

        Returns:
            Dict with updated user data including applications

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        payload = {
            "application_ids": [application_id]
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/users/{sso_id}/applications",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    # ==================== Guest Operations ====================

    async def update_guest_user(
        self,
        sso_id: int,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        notes: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update guest user in SSO service

        Args:
            sso_id: SSO user ID
            valid_from: New valid_from date (ISO format string)
            valid_until: New valid_until date (ISO format string)
            notes: Updated notes
            is_active: Updated active status

        Returns:
            Dict with updated guest user data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        payload = {}

        if valid_from is not None:
            payload["valid_from"] = valid_from

        if valid_until is not None:
            payload["valid_until"] = valid_until

        if notes is not None:
            payload["notes"] = notes

        if is_active is not None:
            payload["is_active"] = is_active

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}/api/guest/sso/{sso_id}",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def deactivate_guest_user(self, sso_id: int) -> Dict[str, Any]:
        """
        Deactivate guest user in SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with success message

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/guest/sso/{sso_id}/deactivate",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def reactivate_guest_user(self, sso_id: int) -> Dict[str, Any]:
        """
        Reactivate guest user in SSO service

        Args:
            sso_id: SSO user ID

        Returns:
            Dict with success message

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/guest/sso/{sso_id}/reactivate",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()


# Singleton instance
sso_client = SSOClient()
