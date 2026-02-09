"""
Emotion service untuk deteksi emosi dari lirik lagu.
Mendukung 2 mode:
1. Local mode: Menggunakan model ONNX lokal
2. Maintenance mode: Menampilkan pesan maintenance jika fitur belum tersedia
"""

import os
from pathlib import Path
from typing import Dict, Optional

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
        self._session = None
        self._tokenizer = None
        self._is_initialized = False
        
    def _initialize_local_model(self) -> None:
        """
        Inisialisasi model lokal menggunakan ONNX Runtime.
        Model di-load dari app/dl/models/model.onnx.
        """
        if self._is_initialized:
            return
            
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
            
            # Cek apakah file model ada
            if not LOCAL_MODEL_PATH.exists():
                raise AppException(
                    status_code=500,
                    detail=f"Model file not found at {LOCAL_MODEL_PATH}"
                )
            
            logger.info(f"Loading local ONNX model from: {LOCAL_MODEL_PATH}")
            
            # Load ONNX session
            self._session = ort.InferenceSession(
                str(LOCAL_MODEL_PATH),
                providers=['CPUExecutionProvider']
            )
            
            # Load tokenizer dari HuggingFace (model yang sama)
            hf_model_id = os.getenv("REPOSIOTRY_ID", "SamLowe/roberta-base-go_emotions")
            logger.info(f"Loading tokenizer from: {hf_model_id}")
            self._tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
            
            self._is_initialized = True
            logger.info("Local emotion model initialized successfully")
            
        except ImportError as e:
            logger.error(f"Missing dependencies for local model: {e}")
            raise AppException(
                status_code=500,
                detail="Missing dependencies: onnxruntime or transformers not installed"
            )
        except Exception as e:
            logger.error(f"Failed to initialize local model: {e}")
            raise AppException(
                status_code=500,
                detail=f"Failed to initialize local model: {str(e)}"
            )
    
    def _predict_local(self, text: str, max_length: int = 128) -> Dict[str, any]:
        """
        Prediksi emosi menggunakan model lokal.
        
        Args:
            text: Teks lirik lagu
            max_length: Panjang maksimum token
            
        Returns:
            Dict dengan emotion dan confidence
        """
        # Pastikan model sudah di-load
        self._initialize_local_model()
        
        # Tokenize input
        inputs = self._tokenizer(
            text,
            return_tensors="np",
            truncation=True,
            padding="max_length",
            max_length=max_length
        )
        
        # Jalankan inference
        input_feed = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        }
        
        # Cek apakah model membutuhkan token_type_ids
        input_names = [inp.name for inp in self._session.get_inputs()]
        if "token_type_ids" in input_names:
            input_feed["token_type_ids"] = inputs.get(
                "token_type_ids", 
                np.zeros_like(inputs["input_ids"])
            ).astype(np.int64)
        
        # Jalankan inference
        outputs = self._session.run(None, input_feed)
        logits = outputs[0][0]  # Ambil output pertama
        
        # Apply softmax untuk mendapatkan probabilitas
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum()
        
        # Ambil emosi dengan confidence tertinggi
        top_idx = np.argmax(probabilities)
        emotion = EMOTION_LABELS[top_idx] if top_idx < len(EMOTION_LABELS) else "unknown"
        confidence = float(probabilities[top_idx])
        
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
        # Cek apakah dalam mode maintenance
        if settings.emotion_service_maintenance:
            logger.warning("Emotion service is in maintenance mode")
            raise AppException(
                status_code=503,
                detail="Emotion detection service is currently under maintenance. Please try again later."
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
