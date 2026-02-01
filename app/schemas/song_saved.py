"""
SongSaved schemas untuk request dan response.
"""

from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class SongSavedBase(BaseSchema):
    """Base schema untuk SongSaved."""
    
    song_title: str = Field(..., max_length=255)
    song_artist: str = Field(..., max_length=255)


class SongSavedCreate(SongSavedBase):
    """Schema untuk menambah lagu ke playlist."""
    
    playlist_id: int


class SongSavedResponse(SongSavedBase):
    """Schema untuk response lagu yang disimpan."""
    
    id: int
    created_at: datetime
    playlist_id: int
