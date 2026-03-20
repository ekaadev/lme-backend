"""
Interpretation service untuk menjelaskan lirik lagu.
Orchestrator yang menggunakan genius_service dan emotion_service.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.history import HistoryRepository
from app.services.genius_service import genius_service
from app.services.emotion_service import emotion_service
from app.utils.logger import logger


class InterpretationService:
    """Service untuk menjelaskan lirik lagu."""
    
    async def explain_song(
        self,
        song_title: str,
        song_artist: str,
        user_id: int,
        db: AsyncSession,
        language_code: str = "id",
    ) -> Dict[str, Any]:
        """
        Jelaskan lirik satu lagu.
        
        Args:
            song_title: Judul lagu
            song_artist: Nama artis
            user_id: ID user yang request
            db: Database session
            language_code: Kode bahasa output
            
        Returns:
            Dict dengan lirik, emosi, dan interpretasi
        """
        logger.info(f"Explaining song: {song_title} by {song_artist}")
        
        # Get lyrics dari Genius
        lyrics = await genius_service.get_lyrics(song_title, song_artist)
        
        if not lyrics:
            raise NotFoundError(detail=f"Lyrics not found for: {song_title} by {song_artist}")
        
        # Predict emotion
        emotion_result = await emotion_service.predict_emotion(lyrics)
        
        # TODO: Interpretasi menggunakan model DL
        interpretation = self._generate_placeholder_interpretation(
            song_title, song_artist, emotion_result["emotion"]
        )
        
        # Simpan ke history
        history_repo = HistoryRepository(db)
        history = await history_repo.create({
            "song_title": song_title,
            "song_artist": song_artist,
            "interpretation": interpretation,
            "emotion": emotion_result["emotion"],
            "language_code": language_code,
            "user_id": user_id,
        })
        
        return {
            "id": history.id,
            "song_title": song_title,
            "song_artist": song_artist,
            "lyrics": lyrics[:500] + "..." if len(lyrics) > 500 else lyrics,
            "emotion": emotion_result,
            "interpretation": interpretation,
        }
    
    async def explain_multiple_songs(
        self,
        songs: List[Dict[str, str]],
        user_id: int,
        db: AsyncSession,
        language_code: str = "id",
    ) -> List[Dict[str, Any]]:
        """
        Jelaskan lirik multiple lagu.
        
        Args:
            songs: List of {"title": str, "artist": str}
            user_id: ID user yang request
            db: Database session
            language_code: Kode bahasa output
            
        Returns:
            List of explanation results
        """
        results = []
        
        for song in songs:
            try:
                result = await self.explain_song(
                    song_title=song["title"],
                    song_artist=song["artist"],
                    user_id=user_id,
                    db=db,
                    language_code=language_code,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error explaining {song}: {e}")
                results.append({
                    "song_title": song["title"],
                    "song_artist": song["artist"],
                    "error": str(e),
                })
        
        return results
    
    def _generate_placeholder_interpretation(
        self,
        song_title: str,
        song_artist: str,
        emotion: str,
    ) -> str:
        """
        Generate placeholder interpretation.
        Akan diganti dengan model ML di masa depan.
        """
        return (
            f"Lagu '{song_title}' oleh {song_artist} memiliki nuansa emosi {emotion}. "
            f"Analisis mendalam tentang makna lirik akan segera hadir dalam pembaruan berikutnya. "
            f"Nantikan fitur interpretasi lengkap kami!"
        )


# Singleton instance
interpretation_service = InterpretationService()
