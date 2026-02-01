"""
Security module untuk JWT dan password hashing.
Menggunakan python-jose untuk JWT dan bcrypt langsung untuk hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password plain text dengan hashed password.
    
    Args:
        plain_password: Password dalam plain text
        hashed_password: Password yang sudah di-hash
    
    Returns:
        True jika password cocok, False jika tidak
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    Hash password menggunakan bcrypt.
    
    Args:
        password: Password dalam plain text
    
    Returns:
        Password yang sudah di-hash
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Buat access token JWT.
    
    Args:
        subject: Subject token, biasanya user ID
        expires_delta: Waktu kadaluarsa token
        extra_data: Data tambahan yang akan disimpan di token
    
    Returns:
        JWT access token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    
    if extra_data:
        to_encode.update(extra_data)

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Buat refresh token JWT.
    Refresh token memiliki waktu kadaluarsa yang lebih lama.
    
    Args:
        subject: Subject token, biasanya user ID
        expires_delta: Waktu kadaluarsa token
    
    Returns:
        JWT refresh token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode dan validasi JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Payload dari token
    
    Raises:
        UnauthorizedError: Jika token tidak valid atau sudah kadaluarsa
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise UnauthorizedError(detail=f"Token validation failed: {str(e)}")


def get_cookie_settings(secure: bool = False) -> Dict[str, Any]:
    """
    Mendapatkan konfigurasi untuk HTTP-only cookie.
    
    Args:
        secure: Apakah cookie hanya dikirim via HTTPS
    
    Returns:
        Dictionary berisi konfigurasi cookie
    """
    # Determine samesite based on environment
    # DEVELOPMENT: 'lax' (localhost compatibility)
    # PRODUCTION: 'none' (cross-origin support, requires secure=True)
    is_production = settings.environment.upper() == "PRODUCTION"
    samesite = "none" if is_production else "lax"
    
    # In production with samesite=none, secure MUST be True
    if is_production:
        secure = True
    
    cookie_config = {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "max_age": settings.access_token_expire_minutes * 60,
    }
    
    # Add partitioned for CHIPS (Cookies Having Independent Partitioned State)
    # Required for samesite=none in Chrome
    if samesite == "none":
        cookie_config["partitioned"] = True
    
    return cookie_config
