"""JWT utility for token verification."""

from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from app.config.settings import settings
from app.core.exceptions import UnauthorizedException
from app.core.security.jwks_client import get_jwks_client


def _get_public_key() -> str:
    """Get public key from JWKS client (cached, with fallback)."""
    return get_jwks_client().get_public_key()


def verify_token_locally(token: str) -> dict:
    """
    Verify JWT token locally using cached public key.
    
    Args:
        token: encoded JWT token string
        
    Returns:
        dict: Decoded payload
        
    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, _get_public_key(), algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        token_client_id = payload.get("client_id")
        if token_client_id != settings.CLIENT_ID:
            raise UnauthorizedException(
                f"Token not valid for this application. Expected '{settings.CLIENT_ID}', got '{token_client_id}'"
            )

        return payload
    except JWTError as e:
        raise UnauthorizedException(f"Invalid token: {str(e)}")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )

jwt_bearer = JWTBearer()
