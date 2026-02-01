"""
Tests untuk configuration module.
"""

import pytest
from app.core.config import Settings, get_settings


class TestSettings:
    """Test class untuk Settings configuration."""

    def test_settings_loads_defaults(self):
        """Test bahwa settings memiliki default values."""
        settings = Settings()
        
        assert settings.app_name == "LyricMeaningExplanation"
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.jwt_algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30

    def test_settings_cors_origins_parsing_list(self):
        """Test parsing CORS origins dari list."""
        settings = Settings(cors_origins=["http://localhost:3000", "http://localhost:5173"])
        
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins

    def test_settings_cors_origins_parsing_json_string(self):
        """Test parsing CORS origins dari JSON string."""
        settings = Settings(cors_origins='["http://localhost:3000"]')
        
        assert len(settings.cors_origins) == 1
        assert settings.cors_origins[0] == "http://localhost:3000"

    def test_get_settings_singleton(self):
        """Test bahwa get_settings mengembalikan singleton."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Karena menggunakan lru_cache, harus sama
        assert settings1 is settings2


class TestSecurityFunctions:
    """Test class untuk security functions."""

    def test_password_hash_and_verify(self):
        """Test password hashing dan verification."""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_create_access_token(self):
        """Test pembuatan access token."""
        from app.core.security import create_access_token, decode_token
        
        subject = "user_123"
        token = create_access_token(subject=subject)
        
        assert token is not None
        assert isinstance(token, str)
        
        payload = decode_token(token)
        assert payload["sub"] == subject
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test pembuatan refresh token."""
        from app.core.security import create_refresh_token, decode_token
        
        subject = "user_123"
        token = create_refresh_token(subject=subject)
        
        assert token is not None
        
        payload = decode_token(token)
        assert payload["sub"] == subject
        assert payload["type"] == "refresh"


class TestExceptions:
    """Test class untuk custom exceptions."""

    def test_not_found_error(self):
        """Test NotFoundError."""
        from app.core.exceptions import NotFoundError
        
        exc = NotFoundError("User not found")
        
        assert exc.status_code == 404
        assert exc.detail == "User not found"

    def test_unauthorized_error(self):
        """Test UnauthorizedError."""
        from app.core.exceptions import UnauthorizedError
        
        exc = UnauthorizedError()
        
        assert exc.status_code == 401
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_external_api_error(self):
        """Test ExternalAPIError."""
        from app.core.exceptions import ExternalAPIError
        
        exc = ExternalAPIError(detail="Rate limit exceeded", service="Genius")
        
        assert exc.status_code == 502
        assert exc.service == "Genius"
        assert "Genius" in exc.detail


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test class untuk health check endpoint."""

    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
