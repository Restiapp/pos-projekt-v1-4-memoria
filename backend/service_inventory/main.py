"""
FastAPI Main Application - Service Inventory
Module 5: Készletkezelés és AI OCR

Ez a fő alkalmazás fájl az Inventory Service mikroszolgáltatáshoz.
Kezeli a készletkezelést, receptúrákat, és Document AI OCR integrációt.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.service_inventory.config import settings

# Import database initialization
from backend.service_inventory.models.database import init_db

# Import RBAC dependencies
from backend.service_admin.dependencies import require_permission

# Import all routers
from backend.service_inventory.routers import (
    inventory_items_router,
    invoice_router,
    recipes_router,
    daily_inventory_router,
    waste_router,
    internal_router,
    osa_router,
)

# Create FastAPI application
app = FastAPI(
    title="Module 5: Inventory Service",
    description="POS System - Készletkezelés és AI OCR Mikroszolgáltatás",
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

# Register API Routers with RBAC protection
app.include_router(
    inventory_items_router,
    dependencies=[Depends(require_permission("inventory:manage"))]
)

app.include_router(
    invoice_router,
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(require_permission("inventory:manage"))]
)


# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Alkalmazás indításakor futó eseménykezelő.
    Inicializálja az adatbázis kapcsolatot és egyéb erőforrásokat.
    """
    print("🚀 Starting Inventory Service...")
    print("📊 Initializing database tables...")
    init_db()
    print(f"📊 Database URL: {str(settings.database_url).split('@')[1]}")
    print(f"🤖 Document AI Processor: {settings.documentai_processor_id}")
    print(f"☁️  GCS Bucket: {settings.gcs_bucket_name}")
    print("✅ Inventory Service initialized successfully!")


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
        "service": "inventory",
        "version": "0.1.0",
        "features": {
            "document_ai": "enabled",
            "gcs_storage": "enabled",
            "perpetual_inventory": "pending"
        }
    }


# Register API Routers with /api/v1 prefix and RBAC protection
app.include_router(
    recipes_router,
    prefix="/api/v1/inventory",
    tags=["Recipes"],
    dependencies=[Depends(require_permission("inventory:manage"))]
)

app.include_router(
    daily_inventory_router,
    prefix="/api/v1/inventory",
    tags=["Daily Inventory"],
    dependencies=[Depends(require_permission("inventory:manage"))]
)

# Waste Logging Router (with RBAC)
app.include_router(
    waste_router,
    prefix="/api/v1",
    tags=["Waste Logging"],
    dependencies=[Depends(require_permission("inventory:manage"))]
)

# V3.0/F3.A - NAV OSA Integration Router (with RBAC)
app.include_router(
    osa_router,
    prefix="/api/v1/inventory",
    tags=["NAV OSA Integration"],
    dependencies=[Depends(require_permission("inventory:manage"))]
)

# V3.0/F3.A - Internal API Router (NO RBAC - service-to-service trust)
app.include_router(
    internal_router,
    prefix="/api/v1/inventory",
    tags=["Internal API"]
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
        "service": "Inventory Service",
        "module": "Module 5: Készletkezelés és AI OCR",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_inventory.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
