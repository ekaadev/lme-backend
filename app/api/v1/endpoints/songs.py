"""
Songs endpoints.
Search dan explain lirik lagu.
"""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.genius_service import genius_service
from app.services.interpretation_service import interpretation_service
from app.schemas.songs import (
    ExplainRequest,
    ExplainResponse,
    ExplainResult,
    SongSearchResult,
)

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/search", response_model=List[SongSearchResult])
async def search_songs(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Max results"),
):
    """
    Search lagu dari Genius API.
    Endpoint ini tidak memerlukan autentikasi.
    """
    results = await genius_service.search_songs(query=q, limit=limit)
    return results


@router.post("/explain", response_model=ExplainResponse)
async def explain_songs(
    data: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Jelaskan lirik lagu.
    Mendukung multiple lagu sekaligus (max 10).
    Hasil akan disimpan ke history.
    """
    songs = [{"title": s.title, "artist": s.artist} for s in data.songs]
    
    results = await interpretation_service.explain_multiple_songs(
        songs=songs,
        user_id=current_user.id,
        db=db,
        language_code=data.language_code,
    )
    
    return ExplainResponse(
        results=[ExplainResult(**r) for r in results],
        total=len(results),
    )
