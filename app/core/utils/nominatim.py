"""
Nominatim OpenStreetMap REST API Client

Client for reverse geocoding using Nominatim OpenStreetMap API.
Converts latitude/longitude coordinates to human-readable addresses.

**API Documentation:**
https://nominatim.openstreetmap.org/

**Usage Policy:**
- Requires User-Agent header (mandatory)
- Rate limit: Max 1 request per second for public endpoint
- Free to use with attribution

**Reverse Geocoding:**
Converts coordinates (lat, lon) to address string.

Example Response:
{
    "display_name": "Jl. Sudirman No. 1, Jakarta Pusat, DKI Jakarta, Indonesia",
    "address": {
        "road": "Jalan Sudirman",
        "suburb": "Jakarta Pusat",
        "city": "Jakarta",
        "state": "DKI Jakarta",
        "country": "Indonesia"
    }
}

**Error Handling:**
- Returns None if location not found
- Logs warnings for API errors
- Fire-and-forget pattern (doesn't block attendance operations)
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from app.config.settings import settings


class NominatimClient:
    """
    REST API client for Nominatim OpenStreetMap reverse geocoding

    Provides methods to convert coordinates to human-readable addresses.

    Configuration:
        NOMINATIM_BASE_URL: Base URL of Nominatim service (default: https://nominatim.openstreetmap.org)
        NOMINATIM_USER_AGENT: User agent for API requests (required by Nominatim)
        NOMINATIM_TIMEOUT: Request timeout in seconds (default: 10)

    Methods:
        reverse_geocode(): Convert lat/lon to address string
    """

    def __init__(self):
        self.base_url = settings.NOMINATIM_BASE_URL
        self.user_agent = settings.NOMINATIM_USER_AGENT
        self.timeout = settings.NOMINATIM_TIMEOUT
        self._last_request_time = 0
        self._rate_limit_delay = 1.0  # 1 second between requests

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for Nominatim API requests.
        User-Agent is REQUIRED by Nominatim usage policy.
        """
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    async def _respect_rate_limit(self):
        """
        Respect Nominatim rate limit (1 request per second).
        Waits if necessary before making next request.
        """
        current_time = asyncio.get_event_loop().time()
        time_since_last_request = current_time - self._last_request_time

        if time_since_last_request < self._rate_limit_delay:
            wait_time = self._rate_limit_delay - time_since_last_request
            await asyncio.sleep(wait_time)

        self._last_request_time = asyncio.get_event_loop().time()

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        language: str = "id"
    ) -> Optional[str]:
        """
        Convert latitude/longitude to human-readable address.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            language: Language code for address (default: 'id' for Indonesian)

        Returns:
            Address string or None if not found or error occurs
            Example: "Jl. Sudirman No. 1, Jakarta Pusat, DKI Jakarta, Indonesia"

        Note:
            This method uses fire-and-forget pattern - errors are logged but not raised
            to avoid blocking attendance operations if geocoding fails.
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                print(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
                return None

            if not (-180 <= longitude <= 180):
                print(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
                return None

            # Respect rate limit
            await self._respect_rate_limit()

            # Build request params
            params = {
                "format": "json",
                "lat": str(latitude),
                "lon": str(longitude),
                "accept-language": language,
                "addressdetails": "1",
                "zoom": "18",  # Building/POI level
            }

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/reverse",
                    params=params,
                    headers=self._get_headers(),
                )

                # Check for errors
                if response.status_code == 404:
                    print(f"Location not found for coordinates: {latitude}, {longitude}")
                    return None

                response.raise_for_status()
                data = response.json()

                # Extract display_name as the full address
                display_name = data.get("display_name")

                if display_name:
                    return display_name

                # Fallback: build address from components if display_name not available
                address = data.get("address", {})
                return self._build_address_from_components(address)

        except httpx.TimeoutException:
            print(f"Nominatim API timeout for coordinates: {latitude}, {longitude}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Nominatim API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error during reverse geocoding: {str(e)}")
            return None

    def _build_address_from_components(self, address: Dict[str, Any]) -> Optional[str]:
        """
        Build address string from address components.

        Args:
            address: Address components dict from Nominatim

        Returns:
            Formatted address string or None
        """
        if not address:
            return None

        # Build address parts in order of specificity
        parts = []

        # Street/road
        if "road" in address:
            parts.append(address["road"])

        # Building/house number
        if "house_number" in address:
            parts[-1] = f"{parts[-1]} No. {address['house_number']}" if parts else f"No. {address['house_number']}"

        # Suburb/neighborhood
        if "suburb" in address:
            parts.append(address["suburb"])
        elif "neighbourhood" in address:
            parts.append(address["neighbourhood"])

        # City
        if "city" in address:
            parts.append(address["city"])
        elif "town" in address:
            parts.append(address["town"])
        elif "village" in address:
            parts.append(address["village"])

        # State/province
        if "state" in address:
            parts.append(address["state"])

        # Country
        if "country" in address:
            parts.append(address["country"])

        return ", ".join(parts) if parts else None

    async def get_location_details(
        self,
        latitude: float,
        longitude: float,
        language: str = "id"
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed location information including all address components.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            language: Language code for address (default: 'id')

        Returns:
            Dict with full location details or None if error occurs
            Example:
            {
                "display_name": "Full address string",
                "address": {
                    "road": "Jalan Sudirman",
                    "city": "Jakarta",
                    "state": "DKI Jakarta",
                    "country": "Indonesia"
                },
                "lat": "-6.2088",
                "lon": "106.8456"
            }
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return None

            # Respect rate limit
            await self._respect_rate_limit()

            params = {
                "format": "json",
                "lat": str(latitude),
                "lon": str(longitude),
                "accept-language": language,
                "addressdetails": "1",
                "zoom": "18",
            }

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/reverse",
                    params=params,
                    headers=self._get_headers(),
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"Error getting location details: {str(e)}")
            return None


# Singleton instance
nominatim_client = NominatimClient()
