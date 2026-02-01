"""
API v1 router.
Menggabungkan semua endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, history, playlist, songs

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(history.router)
api_router.include_router(playlist.router)
api_router.include_router(songs.router)
