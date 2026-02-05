"""
Genius service untuk integrasi dengan Genius API.
Menggunakan httpx untuk direct API calls yang lebih stabil.
"""

from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.exceptions import ExternalAPIError
from app.utils.logger import logger


# Genius API base URL
GENIUS_API_BASE = "https://api.genius.com"


class GeniusService:
    """Service untuk interaksi dengan Genius API."""
    
    def __init__(self):
        """Inisialisasi Genius client."""
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            if not settings.genius_access_token:
                raise ExternalAPIError(detail="Genius access token not configured")
            
            headers = {
                "Authorization": f"Bearer {settings.genius_access_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            
            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=30.0,
            )
            logger.info("Initialized Genius API client")
        
        return self._client
    
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
            
            client = self._get_client()
            
            response = await client.get(
                f"{GENIUS_API_BASE}/search",
                params={"q": query}
            )
            
            if response.status_code != 200:
                logger.error(f"Genius API error: {response.status_code} - {response.text}")
                raise ExternalAPIError(detail=f"Genius API error: {response.status_code}")
            
            data = response.json()
            hits = data.get("response", {}).get("hits", [])
            
            songs = []
            for hit in hits[:limit]:
                result = hit.get("result", {})
                songs.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "artist": result.get("primary_artist", {}).get("name"),
                    "thumbnail": result.get("song_art_image_thumbnail_url"),
                    "url": result.get("url"),
                })
            
            return songs
            
        except ExternalAPIError:
            raise
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
            
            # Search for the song first
            search_results = await self.search_songs(f"{song_title} {artist}", limit=1)
            
            if not search_results:
                logger.warning(f"Song not found: {song_title} by {artist}")
                return None
            
            song_url = search_results[0].get("url")
            if not song_url:
                logger.warning(f"No URL found for: {song_title}")
                return None
            
            # Scrape lyrics from the Genius page
            lyrics = await self._scrape_lyrics_from_url(song_url)
            
            if not lyrics:
                logger.warning(f"No lyrics found at: {song_url}")
                return None
            
            return lyrics
            
        except ExternalAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting lyrics: {str(e)}")
            raise ExternalAPIError(detail=f"Failed to get lyrics: {str(e)}")
    
    async def _scrape_lyrics_from_url(self, url: str) -> Optional[str]:
        """Scrape lyrics dari Genius URL menggunakan BeautifulSoup."""
        try:
            # Use a separate client for scraping (no auth header needed)
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                timeout=15.0,
                follow_redirects=True,
            ) as scrape_client:
                response = await scrape_client.get(url)
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
