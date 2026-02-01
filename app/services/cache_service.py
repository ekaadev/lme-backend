"""
Cache service untuk caching request yang sama.
Menggunakan Redis sebagai backend.
"""

import json
from typing import Any, Optional

from app.core.config import settings
from app.utils.logger import logger


class CacheService:
    """Service untuk caching menggunakan Redis."""
    
    def __init__(self):
        """Inisialisasi cache service."""
        self._redis = None
    
    async def _get_redis(self):
        """Lazy initialization untuk Redis client."""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                
                self._redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self._redis = None
        
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Ambil value dari cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value atau None
        """
        redis = await self._get_redis()
        if redis is None:
            return None
        
        try:
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600,
    ) -> bool:
        """
        Simpan value ke cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: TTL in seconds (default 1 hour)
            
        Returns:
            True jika berhasil
        """
        redis = await self._get_redis()
        if redis is None:
            return False
        
        try:
            await redis.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Hapus key dari cache."""
        redis = await self._get_redis()
        if redis is None:
            return False
        
        try:
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def make_lyrics_key(self, song_title: str, artist: str) -> str:
        """Generate cache key untuk lyrics."""
        return f"lyrics:{song_title.lower()}:{artist.lower()}"
    
    def make_emotion_key(self, text_hash: str) -> str:
        """Generate cache key untuk emotion."""
        return f"emotion:{text_hash}"


# Singleton instance
cache_service = CacheService()
