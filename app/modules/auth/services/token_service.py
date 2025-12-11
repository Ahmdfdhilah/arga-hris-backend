"""
Token Service

Handles token verification, validation, and blacklist checking.
"""

from typing import Dict, Any, Optional
from jose import JWTError, jwt
from app.config.settings import settings
from app.modules.auth.repositories.token_repository import TokenRepository
from app.modules.auth.schemas import TokenValidateResponse, BlacklistStatsResponse
from app.core.exceptions import UnauthorizedException


class TokenService:
    """Service for token operations"""

    def __init__(self, token_repo: TokenRepository):
        """
        Initialize TokenService

        Args:
            token_repo: TokenRepository instance
        """
        self.token_repo = token_repo
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token signature and structure

        Args:
            token: JWT token string

        Returns:
            Token payload

        Raises:
            UnauthorizedException: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload

        except JWTError as e:
            raise UnauthorizedException(f"Token tidak valid: {str(e)}")

    async def verify_and_check_blacklist(self, token: str) -> Dict[str, Any]:
        """
        Verify token and check if it's blacklisted

        Args:
            token: JWT token string

        Returns:
            Token payload if valid and not blacklisted

        Raises:
            UnauthorizedException: If token is invalid or blacklisted
        """
        # First verify token signature
        payload = await self.verify_token(token)

        # Check if token is blacklisted
        #TODO:
        # jti = payload.get("jti")
        # if not jti:
        #     raise UnauthorizedException("Token tidak memiliki JTI claim")

        # is_blacklisted = await self.token_repo.is_token_blacklisted(jti)
        # if is_blacklisted:
        #     raise UnauthorizedException("Token telah dicabut (pengguna sudah logout)")

        # Check if user is globally revoked
        user_id = payload.get("sub") or payload.get("sso_id")
        if user_id:
            is_user_revoked = await self.token_repo.is_user_revoked(str(user_id))
            if is_user_revoked:
                raise UnauthorizedException(
                    "Semua sesi pengguna telah dicabut. Silakan login kembali."
                )

        return payload

    async def blacklist_token(self, token: str) -> bool:
        """
        Blacklist a token (logout)

        Args:
            token: JWT token string

        Returns:
            True if blacklisted successfully
        """
        return await self.token_repo.blacklist_token(token)

    async def revoke_all_user_tokens(
        self,
        user_id: str,
        max_token_lifetime: int = 900
    ) -> bool:
        """
        Revoke all tokens for a user
        Use case: password change, security breach, etc.

        Args:
            user_id: User ID
            max_token_lifetime: Maximum token lifetime in seconds

        Returns:
            True if revoked successfully
        """
        return await self.token_repo.revoke_all_user_tokens(
            user_id,
            max_token_lifetime
        )

    async def unrevoke_user(self, user_id: str) -> bool:
        """
        Remove user-level revocation
        Use case: after password reset, security issue resolved

        Args:
            user_id: User ID

        Returns:
            True if unrevoked successfully
        """
        return await self.token_repo.unrevoke_user(user_id)

    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from token without verification
        Useful for logout when token might be expired

        Args:
            token: JWT token string

        Returns:
            User ID or None
        """
        try:
            payload = jwt.get_unverified_claims(token)
            return payload.get("sub") or payload.get("sso_id")
        except Exception:
            return None

    def extract_jti_from_token(self, token: str) -> Optional[str]:
        """
        Extract JTI from token without verification

        Args:
            token: JWT token string

        Returns:
            JTI or None
        """
        try:
            payload = jwt.get_unverified_claims(token)
            return payload.get("jti")
        except Exception:
            return None

    async def get_blacklist_stats(self) -> Dict[str, int]:
        """
        Get blacklist statistics

        Returns:
            Dict with statistics
        """
        return await self.token_repo.get_blacklist_stats()

    async def is_token_valid(self, token: str) -> bool:
        """
        Check if token is valid (signature + not blacklisted)
        Returns True/False instead of raising exception

        Args:
            token: JWT token string

        Returns:
            True if valid, False otherwise
        """
        try:
            await self.verify_and_check_blacklist(token)
            return True
        except Exception:
            return False

    async def validate_token_with_response(self, token: str) -> TokenValidateResponse:
        """
        Validate token and return response

        Args:
            token: JWT token string

        Returns:
            TokenValidateResponse dengan status validasi token
        """
        is_valid = await self.is_token_valid(token)
        return TokenValidateResponse(valid=is_valid)

    async def get_blacklist_stats_with_response(self) -> BlacklistStatsResponse:
        """
        Get blacklist statistics with response

        Returns:
            BlacklistStatsResponse dengan blacklist statistics
        """
        stats = await self.get_blacklist_stats()
        return BlacklistStatsResponse(
            blacklisted_tokens=stats.get("blacklisted_tokens", 0),
            revoked_users=stats.get("revoked_users", 0),
        )
