"""
FastAPI Main Application - Service Menu
Module 0: Terméktörzs és Menü

Ez a fő alkalmazás fájl a Menu Service mikroszolgáltatáshoz.
Regisztrálja az összes routert és konfigurálja a middleware-eket.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database initialization
from backend.service_menu.database import init_db

# Import all routers
from backend.service_menu.routers import (
    categories_router,
    products_router,
    modifier_groups_router,
    images_router,
    channels_router,
)

# Create FastAPI application
app = FastAPI(
    title="Modul 0: Menu Service",
    description="POS System - Terméktörzs és Menü Mikroszolgáltatás",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Minden origin engedélyezése (development)
    allow_credentials=True,
    allow_methods=["*"],  # Minden HTTP metódus engedélyezése
    allow_headers=["*"],  # Minden header engedélyezése
)


# Startup Event - Database Initialization
@app.on_event("startup")
async def startup_event():
    """
    Alkalmazás indításakor futó eseménykezelő.
    Inicializálja az adatbázis táblákat (development célból).
    """
    print("🚀 Starting Menu Service...")
    print("📊 Initializing database tables...")
    init_db()
    print("✅ Database tables initialized successfully!")


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """
    Egészségügyi állapot ellenőrző végpont.

    Returns:
        dict: Status és verzió információk
    """
    return {
        "status": "ok",
        "version": "0.1.0"
    }


# Register API Routers with /api/v1 prefix
app.include_router(
    categories_router,
    prefix="/api/v1",
    tags=["Categories"]
)

app.include_router(
    products_router,
    prefix="/api/v1",
    tags=["Products"]
)

app.include_router(
    modifier_groups_router,
    prefix="/api/v1",
    tags=["Modifier Groups"]
)

app.include_router(
    images_router,
    prefix="/api/v1",
    tags=["Images"]
)

app.include_router(
    channels_router,
    prefix="/api/v1",
    tags=["Channels"]
)


# Root endpoint
@app.get("/")
async def root():
    """
    Gyökér végpont - szolgáltatás információk.

    Returns:
        dict: Szolgáltatás alapinformációk
    """
    return {
        "service": "Menu Service",
        "module": "Modul 0: Terméktörzs és Menü",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_menu.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
