"""
Emotion service untuk deteksi emosi dari lirik lagu.
Menggunakan Hugging Face Inference API untuk inference.
"""

from typing import Dict

import httpx

from app.core.config import settings
from app.core.exceptions import AppException
from app.utils.logger import logger


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
    
    def _get_client(self) -> httpx.AsyncClient:
        """Lazy load HTTP client."""
        if self._client is None:
            # Use settings from pydantic which properly loads .env
            token = settings.token_hf
            model_id = settings.repository_id
            
            headers = {"Content-Type": "application/json"}
            
            if token:
                headers["Authorization"] = f"Bearer {token}"
                logger.info(f"Using HuggingFace token for authentication (token starts with: {token[:10]}...)")
            else:
                logger.warning("TOKEN_HF not set in .env file. API calls may fail for private models.")
            
            self._client = httpx.AsyncClient(headers=headers, timeout=60.0)
            logger.info(f"Initialized HTTP Client for model: {model_id}")
        
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
            
            model_id = settings.repository_id
            api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
            logger.info(f"Calling HuggingFace Inference API: {api_url}")
            
            
            max_chars = 500
            original_len = len(text)
            truncated_text = text[:max_chars] if original_len > max_chars else text
            logger.info(f"Input text length: {original_len} chars, sending: {len(truncated_text)} chars")
            
            # Call HuggingFace Inference API for text classification
            # wait_for_model: True untuk serverless - akan menunggu model loading
            response = await client.post(
                api_url,
                json={
                    "inputs": truncated_text,
                    "options": {"wait_for_model": True}
                }
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"Inference API error: {response.status_code} - {error_detail}")
                raise AppException(
                    status_code=500,
                    detail=f"Inference API error: {response.status_code} - {error_detail}"
                )
            
            result = response.json()
            logger.info(f"Inference API response: {result}")
            
            # Parse response - returns list of list of {label, score}
            # Format: [[{"label": "joy", "score": 0.9}, ...]]
            if not result:
                raise AppException(
                    status_code=500,
                    detail="Empty response from Inference API"
                )
            
            # Handle nested list format
            predictions = result[0] if isinstance(result, list) and len(result) > 0 else result
            if isinstance(predictions, list) and len(predictions) > 0:
                # Sort by score to get top prediction
                sorted_predictions = sorted(predictions, key=lambda x: x.get("score", 0), reverse=True)
                top_result = sorted_predictions[0]
            else:
                top_result = predictions
            
            emotion = top_result.get("label", "unknown")
            confidence = top_result.get("score", 0.0)
            
            # Build all emotions dict from response
            all_emotions = {}
            items = predictions if isinstance(predictions, list) else [predictions]
            for item in items:
                label = item.get("label", "")
                score = item.get("score", 0.0)
                if label:
                    all_emotions[label] = round(float(score), 4)
            
            return {
                "emotion": emotion,
                "confidence": round(float(confidence), 4),
                "all_emotions": all_emotions
            }
            
        except AppException:
            raise
        except Exception as e:
            logger.error(f"Error predicting emotion via Inference API: {e}")
            raise AppException(
                status_code=500,
                detail=f"Failed to predict emotion: {str(e)}"
            )


# Singleton instance
emotion_service = EmotionService()
