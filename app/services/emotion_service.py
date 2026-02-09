"""
Emotion service untuk deteksi emosi dari lirik lagu.
Mendukung 2 mode:
1. Local mode: Menggunakan model ONNX lokal
2. Maintenance mode: Menampilkan pesan maintenance jika fitur belum tersedia
"""

from typing import Dict

import numpy as np

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

# Path ke model lokal
LOCAL_MODEL_PATH = Path(__file__).parent.parent / "dl" / "models" / "model.onnx"


class EmotionService:
    """Service untuk deteksi emosi dari teks."""
    
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
        
        # Buat dict semua emosi
        all_emotions = {}
        for i, label in enumerate(EMOTION_LABELS):
            if i < len(probabilities):
                all_emotions[label] = round(float(probabilities[i]), 4)
        
        return {
            "emotion": emotion,
            "confidence": round(confidence, 4),
            "all_emotions": all_emotions
        }
    
    async def predict_emotion(
        self,
        text: str,
        max_length: int = 128,
    ) -> Dict[str, any]:
        """
        Prediksi emosi dari teks.
        
        Mode operasi berdasarkan konfigurasi:
        1. Maintenance mode: Return error dengan pesan maintenance
        2. Local mode: Gunakan model lokal ONNX
        
        Args:
            text: Teks lirik lagu
            max_length: Panjang maksimum token
            
        Returns:
            Dict dengan emotion dan confidence
        """
        try:
            client = self._get_client()
            
            model_id = settings.repository_id
            api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
            logger.info(f"Calling HuggingFace Inference API: {api_url}")
            
            # Truncate text to prevent exceeding model's max token limit (512 tokens)
            # Using very conservative limit: 500 chars ≈ 125 tokens for safety
            # 
            # TODO: Ketika menggunakan model TinoIf/lme-emotion yang sudah di-deploy,
            #       bisa hapus/ubah limit ini jika model mendukung input lebih panjang
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
        
        # Cek apakah menggunakan model lokal
        if settings.use_local_model:
            logger.info("Using local ONNX model for emotion prediction")
            try:
                return self._predict_local(text, max_length)
            except AppException:
                raise
            except Exception as e:
                logger.error(f"Error predicting emotion with local model: {e}")
                raise AppException(
                    status_code=500,
                    detail=f"Failed to predict emotion: {str(e)}"
                )
        
        # Jika tidak local mode dan tidak maintenance, tampilkan error
        # karena API HuggingFace sedang bermasalah
        logger.error("HuggingFace Inference API is not available")
        raise AppException(
            status_code=503,
            detail="Emotion detection service is currently unavailable. HuggingFace API is experiencing issues."
        )


# Singleton instance
emotion_service = EmotionService()
