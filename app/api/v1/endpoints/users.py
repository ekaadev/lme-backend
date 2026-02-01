"""
Users endpoints.
Get current user, update profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current logged in user.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile.
    """
    user_repo = UserRepository(db)
    
    update_data = {}
    
    # Check username conflict
    if data.username and data.username != current_user.username:
        if await user_repo.exists_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        update_data["username"] = data.username
    
    # Check email conflict
    if data.email and data.email != current_user.email:
        if await user_repo.exists_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        update_data["email"] = data.email
    
    # Update password
    if data.password:
        update_data["password_hash"] = get_password_hash(data.password)
    
    if update_data:
        user = await user_repo.update(current_user, update_data)
        return user
    
    return current_user
