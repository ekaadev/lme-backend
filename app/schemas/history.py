"""
History schemas untuk request dan response.
"""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common import BaseSchema


class HistoryBase(BaseSchema):
    """Base schema untuk History."""
    
    song_title: str = Field(..., max_length=255)
    song_artist: str = Field(..., max_length=255)
    language_code: str = Field(default="id", max_length=10)


class HistoryCreate(HistoryBase):
    """Schema untuk membuat history baru."""
    
    interpretation: Optional[str] = None
    emotion: Optional[str] = Field(None, max_length=100)


class HistoryResponse(HistoryBase):
    """Schema untuk response history."""
    
    id: int
    interpretation: Optional[str] = None
    emotion: Optional[str] = None
    created_at: datetime
    user_id: int


class HistoryListResponse(BaseSchema):
    """Schema untuk list history."""
    
    id: int
    song_title: str
    song_artist: str
    emotion: Optional[str] = None
    created_at: datetime
