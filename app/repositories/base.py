"""
Base repository dengan CRUD operations.
Pattern Repository untuk abstraksi database operations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base

# Generic type untuk model
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository dengan operasi CRUD standar.
    Semua repository lain harus inherit dari class ini.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Inisialisasi repository.
        
        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session
    
    async def get(self, id: int) -> Optional[ModelType]:
        """
        Ambil satu record berdasarkan ID.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Ambil multiple records dengan pagination.
        """
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """
        Hitung total records.
        """
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Buat record baru.
        
        Args:
            obj_in: Dictionary berisi data untuk create
        """
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db_obj: ModelType,
        obj_in: Dict[str, Any],
    ) -> ModelType:
        """
        Update record yang ada.
        
        Args:
            db_obj: Object yang akan di-update
            obj_in: Dictionary berisi data update
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """
        Hapus record berdasarkan ID.
        
        Returns:
            True jika berhasil dihapus, False jika tidak ditemukan
        """
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False
