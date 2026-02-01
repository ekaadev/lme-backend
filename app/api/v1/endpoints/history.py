"""
History endpoints.
CRUD untuk riwayat interpretasi lagu.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.history import HistoryRepository
from app.schemas.history import HistoryCreate, HistoryResponse, HistoryListResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=List[HistoryListResponse])
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get history interpretasi lagu user.
    """
    history_repo = HistoryRepository(db)
    histories = await history_repo.get_by_user_id(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return histories


@router.get("/{history_id}", response_model=HistoryResponse)
async def get_history_detail(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detail history interpretasi.
    """
    history_repo = HistoryRepository(db)
    history = await history_repo.get(history_id)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History not found",
        )
    
    if history.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this history",
        )
    
    return history


@router.post("", response_model=HistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_history(
    data: HistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Simpan history interpretasi baru.
    """
    history_repo = HistoryRepository(db)
    
    history = await history_repo.create({
        "song_title": data.song_title,
        "song_artist": data.song_artist,
        "interpretation": data.interpretation,
        "emotion": data.emotion,
        "language_code": data.language_code,
        "user_id": current_user.id,
    })
    
    return history


@router.delete("/{history_id}", response_model=MessageResponse)
async def delete_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Hapus history interpretasi.
    """
    history_repo = HistoryRepository(db)
    history = await history_repo.get(history_id)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History not found",
        )
    
    if history.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this history",
        )
    
    await history_repo.delete(history_id)
    
    return {"message": "History deleted successfully"}


@router.get("/search/", response_model=List[HistoryListResponse])
async def search_history(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search history berdasarkan judul atau artis.
    """
    history_repo = HistoryRepository(db)
    histories = await history_repo.search_by_song(
        user_id=current_user.id,
        query=q,
    )
    return histories
