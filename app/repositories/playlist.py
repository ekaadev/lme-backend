"""
Playlist repository untuk operasi database playlist.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.playlist import Playlist
from app.repositories.base import BaseRepository


class PlaylistRepository(BaseRepository[Playlist]):
    """Repository untuk Playlist model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Playlist, session)
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Playlist]:
        """
        Ambil playlists berdasarkan user_id.
        """
        result = await self.session.execute(
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .order_by(Playlist.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_songs(self, id: int) -> Optional[Playlist]:
        """
        Ambil playlist dengan songs (eager loading).
        """
        result = await self.session.execute(
            select(Playlist)
            .where(Playlist.id == id)
            .options(selectinload(Playlist.songs))
        )
        return result.scalar_one_or_none()
    
    async def is_owner(self, playlist_id: int, user_id: int) -> bool:
        """
        Cek apakah user adalah owner dari playlist.
        """
        playlist = await self.get(playlist_id)
        return playlist is not None and playlist.user_id == user_id
