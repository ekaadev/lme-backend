"""
Configuration module untuk aplikasi.
Menggunakan Pydantic Settings untuk load dan validasi environment variables.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Konfigurasi aplikasi yang di-load dari environment variables.
    Semua setting divalidasi secara otomatis oleh Pydantic.
    """

    # Application Settings
    environment: str = "DEVELOPMENT"  # DEVELOPMENT or PRODUCTION
    app_name: str = "LyricMeaningExplanation"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database Settings
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/lme_db"

    # Security Settings
    secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis Cache Settings
    redis_url: str = "redis://localhost:6379/0"

    # External API
    genius_access_token: str = ""

    # Hugging Face Settings
    token_hf: str = ""
    repository_id: str = "TinoIf/lme-emotion"

    # Domain
    domain: str = "localhost"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS origins dari string JSON atau list.
        Contoh: '["http://localhost:3000"]' -> ["http://localhost:3000"]
        """
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Jika bukan JSON, split by comma
                return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Factory function untuk mendapatkan instance Settings.
    Menggunakan lru_cache untuk singleton pattern.
    """
    return Settings()


# Instance global untuk kemudahan import
settings = get_settings()
