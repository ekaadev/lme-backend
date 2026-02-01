"""
Playlist schemas untuk request dan response.
"""

from typing import List, Optional

from pydantic import Field

from app.schemas.common import BaseSchema, TimestampSchema


class PlaylistBase(BaseSchema):
    """Base schema untuk Playlist."""
    
    title: str = Field(..., max_length=255)
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    """Schema untuk membuat playlist baru."""
    
    pass


class PlaylistUpdate(BaseSchema):
    """Schema untuk update playlist."""
    
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class PlaylistResponse(PlaylistBase, TimestampSchema):
    """Schema untuk response playlist."""
    
    id: int
    user_id: int


class PlaylistWithSongsResponse(PlaylistResponse):
    """Schema untuk response playlist dengan daftar lagu."""
    
    songs: List["SongSavedResponse"] = []


# Import lokal untuk menghindari circular import
from app.schemas.song_saved import SongSavedResponse  # noqa: E402

# Update forward reference
PlaylistWithSongsResponse.model_rebuild()
