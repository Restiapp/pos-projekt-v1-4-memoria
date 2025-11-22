"""
FastAPI Main Application - Service CRM
Module 5: Customer Relationship Management

Ez a fő alkalmazás fájl a CRM Service mikroszolgáltatáshoz.
Kezeli az ügyfeladatokat, címeket, kuponokat és ajándékkártyákat.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.service_crm.config import settings

# Import database initialization
from backend.service_crm.models.database import init_db

# Create FastAPI application
app = FastAPI(
    title="Module 5: CRM Service",
    description="POS System - Ügyfélkapcsolat-kezelés (CRM) Mikroszolgáltatás",
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

# Import routers
from backend.service_crm.routers import customers_router, coupons_router, gift_cards_router, addresses_router

# Register routers
app.include_router(
    customers_router,
    prefix="/api/v1/crm",
)

app.include_router(
    coupons_router,
    prefix="/api/v1/crm",
)

app.include_router(
    gift_cards_router,
    prefix="/api/v1/crm",
)

app.include_router(
    addresses_router,
    prefix="/api/v1/crm",
)


# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Alkalmazás indításakor futó eseménykezelő.
    Inicializálja az adatbázis kapcsolatot és egyéb erőforrásokat.
    """
    print("🚀 Starting CRM Service...")
    print("📊 Initializing database tables...")
    init_db()
    print(f"📊 Database URL: {str(settings.database_url).split('@')[1]}")
    print(f"🔗 Admin Service URL: {settings.admin_service_url}")
    print(f"🔗 Orders Service URL: {settings.orders_service_url}")
    print("✅ CRM Service initialized successfully!")


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
        "service": "crm",
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
        "service": "CRM Service",
        "module": "Module 5: Customer Relationship Management",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.service_crm.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
