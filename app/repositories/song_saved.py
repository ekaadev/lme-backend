"""
SongSaved repository untuk operasi database song saved.
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.song_saved import SongSaved
from app.repositories.base import BaseRepository


class SongSavedRepository(BaseRepository[SongSaved]):
    """Repository untuk SongSaved model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(SongSaved, session)
    
    async def get_by_playlist_id(
        self,
        playlist_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SongSaved]:
        """
        Ambil songs berdasarkan playlist_id.
        """
        result = await self.session.execute(
            select(SongSaved)
            .where(SongSaved.playlist_id == playlist_id)
            .order_by(SongSaved.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def exists_in_playlist(
        self,
        playlist_id: int,
        song_title: str,
        song_artist: str,
    ) -> bool:
        """
        Cek apakah lagu sudah ada di playlist.
        """
        result = await self.session.execute(
            select(SongSaved)
            .where(
                SongSaved.playlist_id == playlist_id,
                SongSaved.song_title == song_title,
                SongSaved.song_artist == song_artist,
            )
        )
        return result.scalar_one_or_none() is not None
