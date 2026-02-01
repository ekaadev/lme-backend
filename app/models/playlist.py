"""
Playlist model.
Menyimpan playlist lagu pengguna.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.song_saved import SongSaved
    from app.models.user import User


class Playlist(BaseModel):
    """
    Model untuk tabel playlist.
    
    Attributes:
        title: Judul playlist
        description: Deskripsi playlist
        user_id: Foreign key ke users
        songs: Relasi ke lagu-lagu yang disimpan
    """
    
    __tablename__ = "playlist"
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="playlists",
    )
    songs: Mapped[List["SongSaved"]] = relationship(
        "SongSaved",
        back_populates="playlist",
        cascade="all, delete-orphan",
    )
