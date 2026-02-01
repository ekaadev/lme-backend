"""
Songs schemas untuk search dan explain.
"""

from typing import List, Optional, Dict, Any

from pydantic import Field

from app.schemas.common import BaseSchema


class SongSearchResult(BaseSchema):
    """Schema untuk hasil search lagu."""
    
    id: Optional[int] = None
    title: str
    artist: str
    thumbnail: Optional[str] = None
    url: Optional[str] = None


class SongInput(BaseSchema):
    """Schema untuk input lagu yang akan dijelaskan."""
    
    title: str = Field(..., max_length=255)
    artist: str = Field(..., max_length=255)


class ExplainRequest(BaseSchema):
    """Schema untuk request explain."""
    
    songs: List[SongInput] = Field(..., min_length=1, max_length=10)
    language_code: str = Field(default="id", max_length=10)


class EmotionResult(BaseSchema):
    """Schema untuk hasil deteksi emosi."""
    
    emotion: str
    confidence: float
    all_emotions: Optional[Dict[str, float]] = None


class ExplainResult(BaseSchema):
    """Schema untuk hasil explain satu lagu."""
    
    id: Optional[int] = None
    song_title: str
    song_artist: str
    lyrics: Optional[str] = None
    emotion: Optional[EmotionResult] = None
    interpretation: Optional[str] = None
    error: Optional[str] = None


class ExplainResponse(BaseSchema):
    """Schema untuk response explain multiple songs."""
    
    results: List[ExplainResult]
    total: int
