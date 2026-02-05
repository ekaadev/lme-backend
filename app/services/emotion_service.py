"""
Emotion service untuk deteksi emosi dari lirik lagu.
Menggunakan Hugging Face Inference API untuk inference.
"""

import os
from typing import Dict

from huggingface_hub import InferenceClient

from app.core.exceptions import AppException
from app.utils.logger import logger


# Hugging Face configuration
HF_TOKEN = os.getenv("TOKEN_HF")
HF_MODEL_ID = os.getenv("REPOSIOTRY_ID", "ekaadev/lme-emotion-detection")

# Label emosi (sesuaikan dengan model)
EMOTION_LABELS = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]


class EmotionService:
    """Service untuk deteksi emosi dari teks menggunakan HuggingFace Inference API."""
    
    def __init__(self):
        """Inisialisasi emotion service."""
        self._client = None
    
    def _get_client(self) -> InferenceClient:
        """Lazy load inference client."""
        if self._client is None:
            if not HF_TOKEN:
                logger.warning("TOKEN_HF not set. API calls may fail for private models.")
            
            self._client = InferenceClient(token=HF_TOKEN)
            logger.info(f"Initialized HuggingFace Inference Client for model: {HF_MODEL_ID}")
        
        return self._client
    
    async def predict_emotion(
        self,
        text: str,
        max_length: int = 128,  # kept for API compatibility, not used in inference API
    ) -> Dict[str, any]:
        """
        Prediksi emosi dari teks menggunakan HuggingFace Inference API.
        
        Args:
            text: Teks lirik lagu
            max_length: Tidak digunakan (untuk kompatibilitas API)
            
        Returns:
            Dict dengan emotion dan confidence
        """
        try:
            client = self._get_client()
            
            logger.info(f"Calling HuggingFace Inference API for model: {HF_MODEL_ID}")
            
            # Call HuggingFace Inference API for text classification
            result = client.text_classification(
                text=text,
                model=HF_MODEL_ID,
            )
            
            logger.info(f"Inference API response: {result}")
            
            # Parse response - returns list of {label, score}
            if not result:
                raise AppException(
                    status_code=500,
                    detail="Empty response from Inference API"
                )
            
            # Get top prediction
            top_result = result[0] if isinstance(result, list) else result
            emotion = top_result.get("label", "unknown")
            confidence = top_result.get("score", 0.0)
            
            # Build all emotions dict from response
            all_emotions = {}
            if isinstance(result, list):
                for item in result:
                    label = item.get("label", "")
                    score = item.get("score", 0.0)
                    if label:
                        all_emotions[label] = round(float(score), 4)
            
            return {
                "emotion": emotion,
                "confidence": round(float(confidence), 4),
                "all_emotions": all_emotions
            }
            
        except Exception as e:
            logger.error(f"Error predicting emotion via Inference API: {e}")
            raise AppException(
                status_code=500,
                detail=f"Failed to predict emotion: {str(e)}"
            )


# Singleton instance
emotion_service = EmotionService()
