"""
History model.
Menyimpan riwayat interpretasi/emosi lagu pengguna.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class History(Base):
    """
    Model untuk tabel history.
    Menyimpan hasil interpretasi lagu oleh pengguna.
    
    Attributes:
        song_title: Judul lagu
        song_artist: Nama artis
        interpretation: Hasil interpretasi makna lagu
        emotion: Emosi yang terdeteksi dari lagu
        language_code: Kode bahasa (id, en, dll)
        user_id: Foreign key ke users
    """
    
    __tablename__ = "history"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    song_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    song_artist: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    interpretation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    emotion: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    language_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="id",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="histories",
    )
