"""
User model.
Menyimpan data pengguna aplikasi.
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.history import History
    from app.models.playlist import Playlist


class User(BaseModel):
    """
    Model untuk tabel users.
    
    Attributes:
        username: Username unik pengguna
        email: Email unik pengguna
        password_hash: Password yang sudah di-hash
        histories: Relasi ke history interpretasi lagu
        playlists: Relasi ke playlist pengguna
    """
    
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # Relationships
    histories: Mapped[List["History"]] = relationship(
        "History",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    playlists: Mapped[List["Playlist"]] = relationship(
        "Playlist",
        back_populates="user",
        cascade="all, delete-orphan",
    )
