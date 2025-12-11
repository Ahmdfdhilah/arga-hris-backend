from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config.settings import settings
from app.core.exceptions import UnauthorizedException


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise UnauthorizedException(f"Token tidak valid: {str(e)}")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise UnauthorizedException("Token telah kadaluarsa")
        return payload
    except UnauthorizedException:
        raise
    except Exception as e:
        raise UnauthorizedException(f"Verifikasi token gagal: {str(e)}")


def get_user_from_token(token: str) -> Dict[str, Any]:
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedException("Payload token tidak valid")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token tidak memiliki identitas pengguna")

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "sso_id": payload.get("sso_id"),
    }
