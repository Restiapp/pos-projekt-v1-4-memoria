"""
FastAPI Main Application - Service Orders
Modul 1: Rendelés és Konyha

Ez a fő alkalmazás fájl a Orders Service mikroszolgáltatáshoz.
Kezeli a rendeléseket, konyhai megjelenítést és a rendelési folyamatot.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.service_orders.config import settings

# Import database initialization
from backend.service_orders.models.database import init_db

# Import RBAC dependencies
from backend.service_admin.dependencies import require_permission

from backend.service_orders.routers import (
    tables_router,
    seats_router,
    orders_router,
    order_items_router,
    floorplan_router
)
from backend.service_orders.routers.rooms import router as rooms_router

# Create FastAPI application
app = FastAPI(
    title="Modul 1: Orders Service",
    description="POS System - Rendelés és Konyha Mikroszolgáltatás",
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

# Register routers with RBAC protection
app.include_router(
    rooms_router,
    prefix="/api/v1",
    tags=["Rooms"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
app.include_router(
    tables_router,
    prefix="/api/v1",
    tags=["Tables"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
app.include_router(
    seats_router,
    prefix="/api/v1",
    tags=["Seats"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
app.include_router(
    orders_router,
    prefix="/api/v1",
    tags=["Orders"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
app.include_router(
    order_items_router,
    prefix="/api/v1",
    tags=["Order Items"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
app.include_router(
    floorplan_router.floorplan_router,
    prefix="/api/v1",
    tags=["Floorplan"]
)


# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Alkalmazás indításakor futó eseménykezelő.
    Inicializálja az adatbázis kapcsolatot és egyéb erőforrásokat.
    """
    print("🚀 Starting Orders Service...")
    print("📊 Initializing database tables...")
    init_db()
    print(f"📊 Database URL: {str(settings.database_url).split('@')[1]}")
    print(f"🔗 Menu Service URL: {settings.menu_service_url}")
    print("✅ Orders Service initialized successfully!")


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
        "service": "orders",
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
        "service": "Orders Service",
        "module": "Modul 1: Rendelés és Konyha",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_orders.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
