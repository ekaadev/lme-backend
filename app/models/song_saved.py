"""
SongSaved model.
Menyimpan lagu yang disimpan dalam playlist.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.playlist import Playlist


class SongSaved(Base):
    """
    Model untuk tabel songs_saved.
    Lagu yang disimpan ke dalam playlist.
    
    Attributes:
        song_title: Judul lagu
        song_artist: Nama artis
        playlist_id: Foreign key ke playlist
    """
    
    __tablename__ = "songs_saved"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    song_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    song_artist: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Foreign Key
    playlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("playlist.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationship
    playlist: Mapped["Playlist"] = relationship(
        "Playlist",
        back_populates="songs",
    )
