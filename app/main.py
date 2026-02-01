"""
Main application entry point.
FastAPI app initialization dengan middleware dan exception handlers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.db.session import close_db, init_db
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager untuk startup dan shutdown events.
    Menangani inisialisasi dan cleanup resources.
    """
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    """
    Factory function untuk membuat instance FastAPI.
    Dipisahkan untuk memudahkan testing.
    """
    app = FastAPI(
        title=settings.app_name,
        description="API untuk menjelaskan makna lirik lagu",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler untuk AppException
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handler untuk semua custom exceptions."""
        logger.warning(f"AppException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    
    # Global exception handler untuk unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handler untuk exception yang tidak tertangani."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Endpoint untuk health check."""
        return {"status": "healthy", "app": settings.app_name}
    
    # Include API routers
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    return app


# Instance aplikasi
app = create_app()
