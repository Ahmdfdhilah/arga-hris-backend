"""
JWKS (JSON Web Key Set) Client.

Fetches and caches the public key from SSO's JWKS endpoint for JWT verification.
"""

import time
import httpx
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
import base64

from app.config.settings import settings
from app.core.utils.logging import get_logger

logger = get_logger(__name__)


class JWKSClient:
    """Client to fetch and cache public keys from SSO JWKS endpoint."""

    def __init__(
        self,
        jwks_url: str,
        cache_ttl_seconds: int = 3600,
        fallback_pem_path: Optional[str] = None,
    ):
        self.jwks_url = jwks_url
        self.cache_ttl_seconds = cache_ttl_seconds
        self.fallback_pem_path = fallback_pem_path
        self._cached_pem: Optional[str] = None
        self._cache_expires_at: float = 0

    def _base64url_decode(self, data: str) -> bytes:
        """Decode base64url encoded string (no padding)."""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def _jwk_to_pem(self, jwk: dict) -> str:
        """Convert JWK to PEM format."""
        n = int.from_bytes(self._base64url_decode(jwk["n"]), byteorder="big")
        e = int.from_bytes(self._base64url_decode(jwk["e"]), byteorder="big")

        public_numbers = RSAPublicNumbers(e, n)
        public_key = public_numbers.public_key(default_backend())

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode("utf-8")

    def _fetch_jwks(self) -> Optional[dict]:
        """Fetch JWKS from SSO endpoint."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.jwks_url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch JWKS from {self.jwks_url}: {e}")
            return None

    def _load_fallback_pem(self) -> Optional[str]:
        """Load fallback PEM file."""
        if not self.fallback_pem_path:
            return None
        try:
            with open(self.fallback_pem_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load fallback PEM: {e}")
            return None

    def get_public_key(self, kid: Optional[str] = None) -> str:
        """
        Get the public key in PEM format.
        
        Args:
            kid: Key ID to match (optional). If not provided, uses first key.
            
        Returns:
            Public key in PEM format.
            
        Raises:
            RuntimeError: If no public key is available.
        """
        now = time.time()

        # Return cached key if still valid
        if self._cached_pem and now < self._cache_expires_at:
            return self._cached_pem

        # Try to fetch fresh JWKS
        jwks = self._fetch_jwks()
        if jwks and "keys" in jwks and len(jwks["keys"]) > 0:
            # Find matching key by kid, or use first key
            key = None
            if kid:
                for k in jwks["keys"]:
                    if k.get("kid") == kid:
                        key = k
                        break
            if not key:
                key = jwks["keys"][0]

            self._cached_pem = self._jwk_to_pem(key)
            self._cache_expires_at = now + self.cache_ttl_seconds
            logger.info(f"Fetched and cached public key from JWKS (kid={key.get('kid')})")
            return self._cached_pem

        # Fallback to file-based key
        fallback = self._load_fallback_pem()
        if fallback:
            logger.warning("Using fallback PEM file for public key")
            self._cached_pem = fallback
            # Cache fallback for shorter period to retry JWKS sooner
            self._cache_expires_at = now + 300  # 5 minutes
            return self._cached_pem

        # If we have stale cache, use it
        if self._cached_pem:
            logger.warning("JWKS unavailable, using stale cached key")
            return self._cached_pem

        raise RuntimeError("No public key available from JWKS or fallback")

    def clear_cache(self):
        """Clear the cached key (useful for testing or key rotation)."""
        self._cached_pem = None
        self._cache_expires_at = 0


# Singleton instance
_jwks_client: Optional[JWKSClient] = None


def get_jwks_client() -> JWKSClient:
    """Get or create the singleton JWKS client."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = JWKSClient(
            jwks_url=f"{settings.SSO_SERVICE_URL}/.well-known/jwks.json",
            cache_ttl_seconds=getattr(settings, "JWKS_CACHE_TTL_SECONDS", 3600),
            fallback_pem_path=settings.JWT_PUBLIC_KEY_PATH,
        )
    return _jwks_client
