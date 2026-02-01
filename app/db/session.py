"""
Database session management.
Menggunakan SQLAlchemy async dengan PostgreSQL.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Buat async engine untuk PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries saat debug mode
    future=True,
    pool_pre_ping=True,  # Cek koneksi sebelum digunakan
    pool_size=5,
    max_overflow=10,
)

# Session factory untuk membuat session baru
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Base class untuk semua model SQLAlchemy.
    Semua model harus mewarisi class ini.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency untuk mendapatkan database session.
    Session akan di-close otomatis setelah request selesai.
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inisialisasi database.
    Membuat semua tabel yang belum ada.
    Catatan: Di production, gunakan Alembic untuk migrasi.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Menutup koneksi database.
    Dipanggil saat aplikasi shutdown.
    """
    await engine.dispose()
