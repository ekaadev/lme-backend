"""
History repository untuk operasi database history.
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import History
from app.repositories.base import BaseRepository


class HistoryRepository(BaseRepository[History]):
    """Repository untuk History model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(History, session)
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[History]:
        """
        Ambil history berdasarkan user_id.
        """
        result = await self.session.execute(
            select(History)
            .where(History.user_id == user_id)
            .order_by(History.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def search_by_song(
        self,
        user_id: int,
        query: str,
    ) -> List[History]:
        """
        Cari history berdasarkan judul atau artis.
        """
        result = await self.session.execute(
            select(History)
            .where(
                History.user_id == user_id,
                (History.song_title.ilike(f"%{query}%")) |
                (History.song_artist.ilike(f"%{query}%"))
            )
            .order_by(History.created_at.desc())
        )
        return list(result.scalars().all())
