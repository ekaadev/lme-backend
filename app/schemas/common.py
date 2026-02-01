"""
Common schemas yang digunakan di berbagai tempat.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema dengan konfigurasi standar."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Untuk mapping dari ORM models
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    """Schema dengan timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


# Generic type untuk pagination
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Response schema untuk data yang di-paginate.
    
    Attributes:
        items: List of items
        total: Total jumlah items
        page: Halaman saat ini
        size: Jumlah items per halaman
        pages: Total jumlah halaman
    """
    
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseSchema):
    """Response schema untuk pesan sederhana."""
    
    message: str
    detail: Optional[str] = None
