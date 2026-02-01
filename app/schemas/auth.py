"""
Auth schemas untuk login dan register.
"""

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema


class LoginRequest(BaseSchema):
    """Schema untuk login request."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseSchema):
    """Schema untuk register request."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class TokenResponse(BaseSchema):
    """Schema untuk token response."""
    
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """Schema untuk JWT token payload."""
    
    sub: str  # User ID
    type: str  # access atau refresh
    exp: int  # Expiration timestamp
