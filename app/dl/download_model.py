"""
Download emotion model from Hugging Face Hub.
Auto-downloads on startup if model doesn't exist.
"""
import os
from pathlib import Path

from app.utils.logger import logger

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "emotion_model.onnx"

# Hugging Face repo configuration - loaded from environment variables
# Default values if not set in env
HF_REPO_ID = os.getenv("REPOSIOTRY_ID", "ekaadev/lme-emotion-detection")
HF_FILENAME = "emotion_model.onnx"
HF_TOKEN = os.getenv("TOKEN_HF")  # Token for private repository access


def download_model():
    """Download model from Hugging Face if it doesn't exist yet."""
    if MODEL_PATH.exists():
        file_size = MODEL_PATH.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"Model already exists at {MODEL_PATH} ({file_size:.2f} MB)")
        return
    
    logger.info(f"Model not found at {MODEL_PATH}")
    logger.info(f"Downloading from Hugging Face: {HF_REPO_ID}/{HF_FILENAME}")
    
    # Warning if token is not set (for private repositories)
    if not HF_TOKEN:
        logger.warning("TOKEN_HF not set in environment variables. This may fail for private repositories.")
    else:
        logger.info("Using authentication token from TOKEN_HF environment variable")
    
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        from huggingface_hub import hf_hub_download
        import onnxruntime as ort
        
        # Download model from HF Hub with token authentication
        logger.info(f"Downloading model from {HF_REPO_ID}...")
        downloaded_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_FILENAME,
            token=HF_TOKEN,  # Token for private repository access
            cache_dir=None,  # Use default cache
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,  # Copy file directly
        )
        
        logger.info(f"Model successfully downloaded to: {downloaded_path}")
        
        # Verify file exists and has reasonable size
        if MODEL_PATH.exists():
            file_size = MODEL_PATH.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"Model file size: {file_size:.2f} MB")
            
            # Verify model can be loaded with ONNX Runtime
            try:
                session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
                logger.info("Model ready to use! (ONNX Runtime verification passed)")
            except Exception as ort_error:
                logger.error(f"Model downloaded but failed ONNX Runtime verification: {ort_error}")
                raise
        else:
            raise FileNotFoundError(f"Download succeeded but file not found at {MODEL_PATH}")
            
    except ImportError as ie:
        logger.error(f"Missing required package: {ie}")
        logger.error("Install with: pip install huggingface_hub onnxruntime")
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        logger.error("Make sure HF Token is correct and repository ID is valid.")
        raise


if __name__ == "__main__":
    download_model()
