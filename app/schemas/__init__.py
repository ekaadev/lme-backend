"""
Schemas package.
Export semua Pydantic schemas.
"""

from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload, TokenResponse
from app.schemas.common import BaseSchema, MessageResponse, PaginatedResponse, TimestampSchema
from app.schemas.history import HistoryCreate, HistoryListResponse, HistoryResponse
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistResponse,
    PlaylistUpdate,
    PlaylistWithSongsResponse,
)
from app.schemas.song_saved import SongSavedCreate, SongSavedResponse
from app.schemas.user import UserCreate, UserInDB, UserResponse, UserUpdate

__all__ = [
    # Common
    "BaseSchema",
    "TimestampSchema",
    "PaginatedResponse",
    "MessageResponse",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "TokenPayload",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # History
    "HistoryCreate",
    "HistoryResponse",
    "HistoryListResponse",
    # Playlist
    "PlaylistCreate",
    "PlaylistUpdate",
    "PlaylistResponse",
    "PlaylistWithSongsResponse",
    # SongSaved
    "SongSavedCreate",
    "SongSavedResponse",
]
