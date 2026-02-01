"""
Genius service untuk integrasi dengan Genius API.
Menggunakan lyricsgenius library untuk search dan get lyrics.
"""

from typing import Any, Dict, List, Optional

import lyricsgenius

from app.core.config import settings
from app.core.exceptions import ExternalAPIError, NotFoundError
from app.utils.logger import logger


class GeniusService:
    """Service untuk interaksi dengan Genius API."""
    
    def __init__(self):
        """Inisialisasi Genius client."""
        self._genius: Optional[lyricsgenius.Genius] = None
    
    @property
    def genius(self) -> lyricsgenius.Genius:
        """Lazy initialization untuk Genius client."""
        if self._genius is None:
            if not settings.genius_access_token:
                raise ExternalAPIError(detail="Genius access token not configured")
            
            self._genius = lyricsgenius.Genius(
                settings.genius_access_token,
                verbose=False,
                remove_section_headers=True,
                skip_non_songs=True,
                excluded_terms=["(Remix)", "(Live)"],
                retries=3,
                timeout=15,
            )
        return self._genius
    
    async def search_songs(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search lagu berdasarkan query.
        
        Args:
            query: Kata kunci pencarian
            limit: Jumlah hasil maksimal
            
        Returns:
            List of song info (title, artist, thumbnail, etc)
        """
        try:
            logger.info(f"Searching songs with query: {query}")
            
            # lyricsgenius search returns search hits
            search_result = self.genius.search_songs(query)
            
            if not search_result or "hits" not in search_result:
                return []
            
            songs = []
            for hit in search_result["hits"][:limit]:
                result = hit.get("result", {})
                songs.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "artist": result.get("primary_artist", {}).get("name"),
                    "thumbnail": result.get("song_art_image_thumbnail_url"),
                    "url": result.get("url"),
                })
            
            return songs
            
        except Exception as e:
            logger.error(f"Error searching songs: {str(e)}")
            raise ExternalAPIError(detail=f"Failed to search songs: {str(e)}")
    
    async def get_lyrics(
        self,
        song_title: str,
        artist: str,
    ) -> Optional[str]:
        """
        Ambil lirik lagu berdasarkan judul dan artis.
        
        Args:
            song_title: Judul lagu
            artist: Nama artis
            
        Returns:
            Lirik lagu atau None jika tidak ditemukan
        """
        try:
            logger.info(f"Getting lyrics for: {song_title} by {artist}")
            
            # Try API first
            try:
                song = self.genius.search_song(song_title, artist)
                if song and song.lyrics:
                    return song.lyrics
            except Exception as api_error:
                logger.warning(f"API method failed: {api_error}, trying fallback...")
            
            # Fallback: search dan scrape dari URL
            search_results = await self.search_songs(f"{song_title} {artist}", limit=1)
            if not search_results or not search_results[0].get("url"):
                logger.warning(f"Song not found: {song_title} by {artist}")
                return None
            
            # Scrape lyrics dari URL
            song_url = search_results[0]["url"]
            lyrics = self._scrape_lyrics_from_url(song_url)
            
            if not lyrics:
                logger.warning(f"No lyrics found at: {song_url}")
                return None
            
            return lyrics
            
        except Exception as e:
            logger.error(f"Error getting lyrics: {str(e)}")
            raise ExternalAPIError(detail=f"Failed to get lyrics: {str(e)}")
    
    def _scrape_lyrics_from_url(self, url: str) -> Optional[str]:
        """Scrape lyrics dari Genius URL menggunakan BeautifulSoup."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Genius menggunakan div dengan data-lyrics-container="true"
            lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
            
            if not lyrics_divs:
                return None
            
            # Gabungkan semua lyrics sections
            lyrics_text = "\n\n".join(div.get_text(separator="\n") for div in lyrics_divs)
            
            return lyrics_text.strip()
            
        except Exception as e:
            logger.error(f"Error scraping lyrics from {url}: {e}")
            return None


# Singleton instance
genius_service = GeniusService()
