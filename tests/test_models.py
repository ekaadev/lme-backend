"""
Tests untuk database models dan schemas.
"""

import pytest
from datetime import datetime, timezone

from app.models import User, History, Playlist, SongSaved
from app.schemas import (
    UserCreate,
    UserResponse,
    HistoryCreate,
    HistoryResponse,
    PlaylistCreate,
    PlaylistResponse,
    SongSavedCreate,
    SongSavedResponse,
    LoginRequest,
    RegisterRequest,
)


class TestUserSchema:
    """Test class untuk User schemas."""

    def test_user_create_valid(self):
        """Test membuat UserCreate dengan data valid."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"

    def test_user_create_invalid_email(self):
        """Test UserCreate dengan email tidak valid."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123"
            )

    def test_user_create_short_password(self):
        """Test UserCreate dengan password terlalu pendek."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="short"
            )


class TestHistorySchema:
    """Test class untuk History schemas."""

    def test_history_create_valid(self):
        """Test membuat HistoryCreate dengan data valid."""
        history = HistoryCreate(
            song_title="Bohemian Rhapsody",
            song_artist="Queen",
            interpretation="A song about life and death",
            emotion="melancholic",
            language_code="en"
        )
        
        assert history.song_title == "Bohemian Rhapsody"
        assert history.song_artist == "Queen"
        assert history.emotion == "melancholic"

    def test_history_create_default_language(self):
        """Test HistoryCreate dengan default language."""
        history = HistoryCreate(
            song_title="Test Song",
            song_artist="Test Artist"
        )
        
        assert history.language_code == "id"


class TestPlaylistSchema:
    """Test class untuk Playlist schemas."""

    def test_playlist_create_valid(self):
        """Test membuat PlaylistCreate dengan data valid."""
        playlist = PlaylistCreate(
            title="My Favorites",
            description="Collection of my favorite songs"
        )
        
        assert playlist.title == "My Favorites"
        assert playlist.description == "Collection of my favorite songs"

    def test_playlist_create_minimal(self):
        """Test PlaylistCreate dengan data minimal."""
        playlist = PlaylistCreate(title="Minimal Playlist")
        
        assert playlist.title == "Minimal Playlist"
        assert playlist.description is None


class TestSongSavedSchema:
    """Test class untuk SongSaved schemas."""

    def test_song_saved_create_valid(self):
        """Test membuat SongSavedCreate dengan data valid."""
        song = SongSavedCreate(
            song_title="Test Song",
            song_artist="Test Artist",
            playlist_id=1
        )
        
        assert song.song_title == "Test Song"
        assert song.playlist_id == 1


class TestAuthSchema:
    """Test class untuk Auth schemas."""

    def test_login_request_valid(self):
        """Test LoginRequest dengan data valid."""
        login = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        assert login.email == "test@example.com"

    def test_register_request_valid(self):
        """Test RegisterRequest dengan data valid."""
        register = RegisterRequest(
            username="newuser",
            email="new@example.com",
            password="password123"
        )
        
        assert register.username == "newuser"
        assert register.email == "new@example.com"
