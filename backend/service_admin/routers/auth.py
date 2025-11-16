"""
Authentication Router - Bejelentkezés és Felhasználókezelés
Module 6: RBAC (Role-Based Access Control) - Phase 4.4

Ez a router felelős az autentikációs végpontokért:
- PIN-alapú bejelentkezés (POST /auth/login)
- Aktuális felhasználó adatai (GET /auth/me)
- JWT token generálás és kezelés
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.auth_service import AuthService
from backend.service_admin.dependencies import get_current_user
from backend.service_admin.schemas.auth import LoginRequest, TokenResponse
from backend.service_admin.config import settings


# Initialize router
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Dependency: AuthService factory
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Dependency injection az AuthService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        AuthService: Inicializált AuthService instance
    """
    return AuthService(db)


# ============================================================================
# POST /auth/login - PIN-alapú Bejelentkezés
# ============================================================================

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="PIN-alapú Bejelentkezés",
    description="Alkalmazotti bejelentkezés PIN kóddal. Sikeres bejelentkezés után JWT token-t ad vissza."
)
async def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    PIN-alapú bejelentkezés JWT token generálással.

    Ez a végpont:
    1. Ellenőrzi a felhasználónevet és PIN kódot (AuthService.authenticate_employee)
    2. Generál egy JWT access token-t (AuthService.create_token_with_permissions)
    3. Visszaadja a token-t és a kapcsolódó metaadatokat

    Args:
        credentials: LoginRequest (username, password/PIN)
        auth_service: AuthService dependency

    Returns:
        TokenResponse: JWT access token és metaadatok

    Raises:
        HTTPException 401: Ha hibás a felhasználónév vagy PIN kód
        HTTPException 403: Ha inaktív a felhasználó (már az authenticate_employee-ban ellenőrzött)

    Example Request:
        POST /auth/login
        {
            "username": "jkovacs",
            "password": "1234"
        }

    Example Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 3600,
            "issued_at": "2024-01-15T14:30:00Z"
        }
    """
    # 1. Alkalmazott hitelesítése (username + PIN kód ellenőrzés)
    employee = auth_service.authenticate_employee(
        username=credentials.username,
        pin_code=credentials.password  # "password" mező tartalmazza a PIN kódot
    )

    # 2. Hitelesítés sikertelen ellenőrzés
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hibás felhasználónév vagy PIN kód",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. JWT token generálás az alkalmazott jogosultságaival
    # A create_token_with_permissions metódus tartalmazza:
    # - employee_id (sub)
    # - username
    # - roles (szerepkörök)
    # - permissions (jogosultságok)
    access_token = auth_service.create_token_with_permissions(employee)

    # 4. Token response összeállítása
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,  # percből másodpercbe
        issued_at=datetime.utcnow()
    )


# ============================================================================
# GET /auth/me - Aktuális Bejelentkezett Felhasználó Adatai
# ============================================================================

@auth_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Aktuális Felhasználó Adatai",
    description="JWT token alapján lekéri a bejelentkezett felhasználó adatait, szerepköreit és jogosultságait."
)
async def get_current_user_info(
    current_user: Employee = Depends(get_current_user)
):
    """
    Aktuális bejelentkezett felhasználó adatainak lekérése.

    Ez a végpont:
    1. JWT token-ből azonosítja a felhasználót (get_current_user dependency)
    2. Visszaadja a felhasználó alapadatait
    3. Visszaadja a felhasználó szerepköreit (roles)
    4. Visszaadja a felhasználó jogosultságait (permissions)

    Args:
        current_user: Employee objektum (get_current_user dependency által injektálva)

    Returns:
        dict: Felhasználó adatai, szerepkörei és jogosultságai

    Raises:
        HTTPException 401: Ha a token érvénytelen vagy lejárt
        HTTPException 403: Ha a felhasználó inaktív

    Example Request:
        GET /auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response:
        {
            "id": 1,
            "username": "jkovacs",
            "name": "Kovács János",
            "email": "janos.kovacs@example.com",
            "phone": "+36301234567",
            "is_active": true,
            "roles": [
                {
                    "id": 1,
                    "name": "Admin",
                    "description": "Teljes hozzáférés"
                }
            ],
            "permissions": [
                "orders:view",
                "orders:create",
                "admin:all"
            ],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T14:30:00Z"
        }
    """
    # Szerepkörök összegyűjtése
    roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description
        }
        for role in current_user.roles
    ]

    # Jogosultságok összegyűjtése (Employee.permissions property)
    # A permissions property egy set, ezért listává konvertáljuk
    permissions: List[str] = [perm.name for perm in current_user.permissions]

    # Felhasználó adatainak visszaadása
    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "roles": roles,
        "permissions": permissions,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }
