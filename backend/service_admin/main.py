"""
Main application module for the Admin Service (Modul 8).

This module initializes the FastAPI application and configures:
- NTAK integration endpoints
- Administrative dashboard endpoints
- Inter-service communication
- Health checks and monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging

from backend.service_admin.config import settings
from backend.service_admin import __version__, __service_name__

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifespan events.

    Startup:
    - Initialize HTTP client for inter-service communication
    - Log service configuration

    Shutdown:
    - Close HTTP client connections
    """
    # Startup
    logger.info(f"Starting {__service_name__} v{__version__}")
    logger.info(f"NTAK Integration: {'Enabled' if settings.ntak_enabled else 'Disabled'}")
    logger.info(f"Port: {settings.port}")

    # Create HTTP client for inter-service communication
    app.state.http_client = httpx.AsyncClient(timeout=30.0)

    yield

    # Shutdown
    logger.info(f"Shutting down {__service_name__}")
    await app.state.http_client.aclose()


# Initialize FastAPI application
app = FastAPI(
    title="Admin Service (Modul 8)",
    description="NTAK Integration and Administrative Functions for POS System",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Check Endpoints
# ============================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for container orchestration.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": __service_name__,
        "version": __version__,
        "ntak_enabled": settings.ntak_enabled
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with service information.

    Returns:
        dict: Service metadata
    """
    return {
        "service": __service_name__,
        "version": __version__,
        "description": "Admin Service - NTAK Integration and Administrative Functions",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# ============================================
# Service Status Endpoint
# ============================================

@app.get("/status", tags=["Status"])
async def service_status():
    """
    Detailed service status including configuration and connectivity.

    Returns:
        dict: Comprehensive service status
    """
    status = {
        "service": __service_name__,
        "version": __version__,
        "port": settings.port,
        "ntak": {
            "enabled": settings.ntak_enabled,
            "api_url": settings.ntak_api_url,
            "restaurant_id": settings.ntak_restaurant_id,
            "report_interval": settings.ntak_report_interval
        },
        "connected_services": {
            "orders_service": settings.orders_service_url,
            "menu_service": settings.menu_service_url,
            "inventory_service": settings.inventory_service_url
        }
    }

    return status


# ============================================
# Router Registration
# ============================================

# Import routers
from backend.service_admin.routers import internal_router

# Register internal API router (V. Fázis - NTAK és Audit)
app.include_router(internal_router)

# Future router registration:
# - Admin dashboard router
# - System configuration router
# app.include_router(admin_router, prefix="/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_admin.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
