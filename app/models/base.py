"""
Base model untuk semua SQLAlchemy models.
Menyediakan common fields dan utility methods.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TimestampMixin:
    """
    Mixin untuk menambahkan created_at dan updated_at fields.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """
    Base model dengan id dan timestamps.
    Semua model harus inherit dari class ini.
    """
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model instance ke dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
