"""
User schemas untuk request dan response.
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base schema untuk User."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema untuk membuat user baru."""
    
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """Schema untuk update user."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase, TimestampSchema):
    """
    Schema untuk response user.
    Tidak termasuk password_hash untuk keamanan.
    """
    
    id: int


class UserInDB(UserResponse):
    """Schema internal yang termasuk password_hash."""
    
    password_hash: str
