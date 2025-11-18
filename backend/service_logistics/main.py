"""
FastAPI Main Application - Service Logistics
V3.0 Module: Kiszállítási Szolgáltatás

Ez a fő alkalmazás fájl a Logistics Service mikroszolgáltatáshoz.
Kezeli a kiszállítási zónákat, futárokat és a kiszállítási folyamatot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_logistics.config import settings

# Import database initialization
from backend.service_logistics.models.database import init_db

# Create FastAPI application
app = FastAPI(
    title="V3.0: Logistics Service",
    description="POS System - Kiszállítási Mikroszolgáltatás",
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

# TODO: Register routers when created
# app.include_router(
#     delivery_zones_router,
#     prefix="/api/v1",
#     tags=["Delivery Zones"]
# )
# app.include_router(
#     couriers_router,
#     prefix="/api/v1",
#     tags=["Couriers"]
# )


# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Alkalmazás indításakor futó eseménykezelő.
    Inicializálja az adatbázis kapcsolatot és egyéb erőforrásokat.
    """
    print("🚀 Starting Logistics Service...")
    print("📊 Initializing database tables...")
    init_db()
    print(f"📊 Database URL: {str(settings.database_url).split('@')[1]}")
    print(f"🔗 Orders Service URL: {settings.orders_service_url}")
    print("✅ Logistics Service initialized successfully!")


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
        "service": "logistics",
        "version": "0.1.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Gyökér végpont - szolgáltatás információk.

    Returns:
        dict: Szolgáltatás alapinformációk
    """
    return {
        "service": "Logistics Service",
        "module": "V3.0: Kiszállítási Szolgáltatás",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_logistics.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
