"""
Playlist endpoints.
CRUD untuk playlist dan songs.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.playlist import PlaylistRepository
from app.repositories.song_saved import SongSavedRepository
from app.schemas.playlist import (
    PlaylistCreate,
    PlaylistResponse,
    PlaylistUpdate,
    PlaylistWithSongsResponse,
)
from app.schemas.song_saved import SongSavedCreate, SongSavedResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/playlist", tags=["playlist"])


@router.get("", response_model=List[PlaylistResponse])
async def get_playlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get semua playlist user.
    """
    playlist_repo = PlaylistRepository(db)
    playlists = await playlist_repo.get_by_user_id(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistWithSongsResponse)
async def get_playlist_detail(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detail playlist dengan songs.
    """
    playlist_repo = PlaylistRepository(db)
    playlist = await playlist_repo.get_with_songs(playlist_id)
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this playlist",
        )
    
    return playlist


@router.post("", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Buat playlist baru.
    """
    playlist_repo = PlaylistRepository(db)
    
    playlist = await playlist_repo.create({
        "title": data.title,
        "description": data.description,
        "user_id": current_user.id,
    })
    
    return playlist


@router.patch("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: int,
    data: PlaylistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update playlist.
    """
    playlist_repo = PlaylistRepository(db)
    playlist = await playlist_repo.get(playlist_id)
    
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this playlist",
        )
    
    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.description is not None:
        update_data["description"] = data.description
    
    if update_data:
        playlist = await playlist_repo.update(playlist, update_data)
    
    return playlist


@router.delete("/{playlist_id}", response_model=MessageResponse)
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Hapus playlist.
    """
    playlist_repo = PlaylistRepository(db)
    
    if not await playlist_repo.is_owner(playlist_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this playlist",
        )
    
    await playlist_repo.delete(playlist_id)
    
    return {"message": "Playlist deleted successfully"}


# Songs in playlist endpoints

@router.post("/{playlist_id}/songs", response_model=SongSavedResponse, status_code=status.HTTP_201_CREATED)
async def add_song_to_playlist(
    playlist_id: int,
    data: SongSavedCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tambah lagu ke playlist.
    """
    playlist_repo = PlaylistRepository(db)
    song_repo = SongSavedRepository(db)
    
    # Cek ownership
    if not await playlist_repo.is_owner(playlist_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add songs to this playlist",
        )
    
    # Cek song sudah ada
    if await song_repo.exists_in_playlist(playlist_id, data.song_title, data.song_artist):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Song already in playlist",
        )
    
    song = await song_repo.create({
        "song_title": data.song_title,
        "song_artist": data.song_artist,
        "playlist_id": playlist_id,
    })
    
    return song


@router.delete("/{playlist_id}/songs/{song_id}", response_model=MessageResponse)
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Hapus lagu dari playlist.
    """
    playlist_repo = PlaylistRepository(db)
    song_repo = SongSavedRepository(db)
    
    # Cek ownership
    if not await playlist_repo.is_owner(playlist_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove songs from this playlist",
        )
    
    song = await song_repo.get(song_id)
    if not song or song.playlist_id != playlist_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found in playlist",
        )
    
    await song_repo.delete(song_id)
    
    return {"message": "Song removed from playlist"}
