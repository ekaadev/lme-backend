"""
Auth endpoints.
Login, register, logout, refresh token.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_cookie_settings,
    get_password_hash,
    verify_password,
    decode_token,
)
from app.core.exceptions import ConflictError, UnauthorizedError
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register user baru.
    """
    user_repo = UserRepository(db)
    
    # Cek email sudah terdaftar
    if await user_repo.exists_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Cek username sudah terdaftar
    if await user_repo.exists_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    
    # Create user
    user = await user_repo.create({
        "username": data.username,
        "email": data.email,
        "password_hash": get_password_hash(data.password),
    })
    
    return user


@router.post("/login")
async def login(
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login user dan set JWT cookie.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(data.email)
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    # Set cookies
    cookie_settings = get_cookie_settings()
    response.set_cookie(
        key="jwt",
        value=access_token,
        **cookie_settings,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=cookie_settings.get("secure", False),
        samesite=cookie_settings.get("samesite", "lax"),
        max_age=7 * 24 * 60 * 60,  # 7 days
    )
    
    return {
        "message": "Login successful",
        "user": UserResponse.model_validate(user),
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """
    Logout user dengan menghapus cookies.
    """
    response.delete_cookie("jwt")
    response.delete_cookie("refresh_token")
    
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token menggunakan refresh token.
    """
    from fastapi import Cookie
    
    # Ambil refresh token dari cookie
    # Note: Ini perlu adjustment untuk Cookie dependency
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise UnauthorizedError(detail="Invalid token type")
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify user exists
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Create new access token
    new_access_token = create_access_token(subject=str(user.id))
    
    cookie_settings = get_cookie_settings()
    response.set_cookie(
        key="jwt",
        value=new_access_token,
        **cookie_settings,
    )
    
    return {"message": "Token refreshed successfully"}
