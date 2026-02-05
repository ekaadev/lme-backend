"""
Emotion service untuk deteksi emosi dari lirik lagu.
Menggunakan ONNX model untuk inference.
"""

import os
from typing import Dict, List, Optional

import numpy as np

from app.core.exceptions import AppException
from app.utils.logger import logger

# Path ke model ONNX
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dl", "models", "emotion_model.onnx"
)

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
    """Service untuk deteksi emosi dari teks."""
    
    def __init__(self):
        """Inisialisasi emotion service."""
        self._session = None
        self._tokenizer = None
    
    def _load_model(self):
        """Load ONNX model dan tokenizer."""
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
            
            # Auto-download dari Hugging Face jika tidak ada
            if not os.path.exists(MODEL_PATH):
                logger.warning(f"Model not found at {MODEL_PATH}")
                logger.info("Attempting to download from Hugging Face...")
                
                try:
                    from app.dl.download_model import download_model
                    download_model()
                except Exception as download_error:
                    logger.error(f"Failed to auto-download model: {download_error}")
                    raise AppException(
                        status_code=500,
                        detail=f"Emotion model not found at {MODEL_PATH} and auto-download failed: {download_error}"
                    )
            
            # Verify model exists after download attempt
            if not os.path.exists(MODEL_PATH):
                raise AppException(
                    status_code=500,
                    detail=f"Emotion model not found at {MODEL_PATH}"
                )
            
            logger.info(f"Loading emotion model from {MODEL_PATH}")
            
            # Load ONNX session
            self._session = ort.InferenceSession(
                MODEL_PATH,
                providers=["CPUExecutionProvider"]
            )
            
            # Load tokenizer - model uses roberta-base (English)
            # Vocab size must match: 50265
            self._tokenizer = AutoTokenizer.from_pretrained(
                "roberta-base"
            )
            
            logger.info("Emotion model loaded successfully")
            
        except ImportError as e:
            logger.error(f"Missing dependency for emotion service: {e}")
            raise AppException(
                status_code=500,
                detail="Missing dependency: onnxruntime or transformers"
            )
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            raise AppException(
                status_code=500,
                detail=f"Failed to load emotion model: {str(e)}"
            )
    
    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            self._load_model()
        return self._session
    
    @property
    def tokenizer(self):
        """Lazy load tokenizer."""
        if self._tokenizer is None:
            self._load_model()
        return self._tokenizer
    
    async def predict_emotion(
        self,
        text: str,
        max_length: int = 128,
    ) -> Dict[str, any]:
        """
        Prediksi emosi dari teks.
        
        Args:
            text: Teks lirik lagu
            max_length: Panjang maksimal token
            
        Returns:
            Dict dengan emotion dan confidence
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="np",
                max_length=max_length,
                truncation=True,
                padding="max_length",
            )
            
            # Run inference - hanya input_ids dan attention_mask
            input_feed = {
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.int64),
            }
            
            outputs = self.session.run(None, input_feed)
            
            # Get predictions
            logits = outputs[0]
            probabilities = self._softmax(logits[0])
            
            predicted_idx = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_idx])
            
            # Handle jika index melebihi jumlah labels
            if predicted_idx < len(EMOTION_LABELS):
                emotion = EMOTION_LABELS[predicted_idx]
            else:
                emotion = f"emotion_{predicted_idx}"
            
            return {
                "emotion": emotion,
                "confidence": round(confidence, 4),
                "all_emotions": {
                    label: round(float(prob), 4)
                    for label, prob in zip(EMOTION_LABELS, probabilities)
                    if label and prob
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting emotion: {e}")
            raise AppException(
                status_code=500,
                detail=f"Failed to predict emotion: {str(e)}"
            )
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Compute softmax values."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()


# Singleton instance
emotion_service = EmotionService()
