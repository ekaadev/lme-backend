"""
API dependencies.
Berisi dependencies untuk authentication dan database session.
"""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    jwt: Optional[str] = Cookie(None),
) -> User:
    """
    Dependency untuk mendapatkan current user dari JWT cookie.
    Raises HTTPException jika tidak terautentikasi.
    """
    if not jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(jwt)
        user_id = int(payload.get("sub"))
        token_type = payload.get("type")
        
        if token_type != "access":
            raise UnauthorizedError(detail="Invalid token type")
        
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    jwt: Optional[str] = Cookie(None),
) -> Optional[User]:
    """
    Dependency untuk mendapatkan current user (optional).
    Returns None jika tidak terautentikasi.
    """
    if not jwt:
        return None
    
    try:
        payload = decode_token(jwt)
        user_id = int(payload.get("sub"))
        
        user_repo = UserRepository(db)
        return await user_repo.get(user_id)
    except Exception:
        return None
