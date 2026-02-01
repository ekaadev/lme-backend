"""
User repository untuk operasi database user.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository untuk User model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Ambil user berdasarkan email.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Ambil user berdasarkan username.
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Cek apakah email sudah terdaftar.
        """
        user = await self.get_by_email(email)
        return user is not None
    
    async def exists_by_username(self, username: str) -> bool:
        """
        Cek apakah username sudah terdaftar.
        """
        user = await self.get_by_username(username)
        return user is not None
