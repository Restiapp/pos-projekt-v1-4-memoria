"""
Employee Router - Munkatárs CRUD API végpontok
Module 6: RBAC - Phase 4.1 (Employee Router)

Ez a router felelős a munkatársak (employees) kezeléséért:
- CRUD műveletek (létrehozás, olvasás, frissítés, törlés)
- Szerepkör (role) hozzárendelés
- Jogosultság (permission) lekérdezés
- Összes végpont védett require_permission("employees:manage") jogosultsággal
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.models.role import Role
from backend.service_admin.models.permission import Permission
from backend.service_admin.services.employee_service import EmployeeService
from backend.service_admin.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

employees_router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# ============================================================================
# Dependencies
# ============================================================================

def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """
    Dependency injection az EmployeeService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        EmployeeService: Inicializált service instance
    """
    return EmployeeService(db)


# ============================================================================
# CRUD Endpoints
# ============================================================================

@employees_router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Munkatárs létrehozása",
    description="Új munkatárs létrehozása a rendszerben.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    """
    Új munkatárs létrehozása.

    **Jogosultság:** `employees:manage`

    Args:
        employee_data: Munkatárs adatok (EmployeeCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeResponse: Létrehozott munkatárs adatai

    Raises:
        HTTPException 400: Ha a felhasználónév már létezik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        # Schema field mapping: full_name -> name, password -> pin_code
        employee = service.create_employee(
            username=employee_data.username,
            name=employee_data.full_name,
            pin_code=employee_data.password,
            email=employee_data.email,
            is_active=employee_data.is_active
        )

        # Role hozzárendelés ha meg van adva
        if employee_data.role_id:
            service.assign_roles(employee.id, [employee_data.role_id])
            # Refresh employee to get updated roles
            employee = service.get_employee_by_id(employee.id)

        return EmployeeResponse.model_validate(employee)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba a munkatárs létrehozása során: {str(e)}"
        )


@employees_router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Munkatárs lekérése ID alapján",
    description="Egy adott munkatárs adatainak lekérése ID alapján.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def get_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    """
    Munkatárs lekérése ID alapján.

    **Jogosultság:** `employees:manage`

    Args:
        employee_id: Munkatárs egyedi azonosítója
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeResponse: Munkatárs adatai

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 403: Ha nincs jogosultság
    """
    employee = service.get_employee_by_id(employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Munkatárs nem található: {employee_id}"
        )

    return EmployeeResponse.model_validate(employee)


@employees_router.get(
    "",
    response_model=EmployeeListResponse,
    status_code=status.HTTP_200_OK,
    summary="Munkatársak listázása",
    description="Munkatársak listázása szűrési és lapozási lehetőségekkel.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def list_employees(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeListResponse:
    """
    Munkatársak listázása szűrési és lapozási lehetőségekkel.

    **Jogosultság:** `employees:manage`

    Args:
        is_active: Szűrés aktív státuszra (None = összes)
        search: Keresési kifejezés (név vagy username)
        page: Oldalszám (1-től kezdődik)
        page_size: Elemek száma oldalanként (max 100)
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeListResponse: Munkatársak listája és meta információk

    Raises:
        HTTPException 400: Ha az oldalszám vagy page_size érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    # Validáció
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Az oldalszám nem lehet kisebb mint 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A page_size értéke 1 és 100 között kell legyen"
        )

    # Lapozás számítás
    offset = (page - 1) * page_size

    # Munkatársak lekérése
    employees = service.list_employees(
        is_active=is_active,
        search=search,
        limit=page_size,
        offset=offset
    )

    # Összes munkatárs száma (szűrés figyelembevételével)
    total_count = service.count_employees(
        is_active=is_active,
        search=search
    )

    # Response összeállítása
    return EmployeeListResponse(
        items=[EmployeeResponse.model_validate(emp) for emp in employees],
        total=total_count,
        page=page,
        page_size=page_size
    )


@employees_router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Munkatárs frissítése",
    description="Meglévő munkatárs adatainak frissítése.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    """
    Munkatárs adatainak frissítése.

    **Jogosultság:** `employees:manage`

    Args:
        employee_id: Munkatárs egyedi azonosítója
        employee_data: Frissítendő adatok (EmployeeUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeResponse: Frissített munkatárs adatai

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 400: Ha a felhasználónév már létezik (más munkatársnál)
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        # Schema field mapping: full_name -> name, password -> pin_code
        employee = service.update_employee(
            employee_id=employee_id,
            name=employee_data.full_name,
            username=employee_data.username,
            email=employee_data.email,
            phone=None,  # Schema nem tartalmazza a phone mezőt
            pin_code=employee_data.password,
            is_active=employee_data.is_active
        )

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Munkatárs nem található: {employee_id}"
            )

        # Role frissítés ha meg van adva
        if employee_data.role_id is not None:
            service.assign_roles(employee.id, [employee_data.role_id])
            # Refresh employee to get updated roles
            employee = service.get_employee_by_id(employee.id)

        return EmployeeResponse.model_validate(employee)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba a munkatárs frissítése során: {str(e)}"
        )


@employees_router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Munkatárs törlése",
    description="Munkatárs törlése a rendszerből (hard delete).",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def delete_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> None:
    """
    Munkatárs törlése.

    **Jogosultság:** `employees:manage`

    **Figyelem:** Ez hard delete (fizikai törlés). Soft delete esetén
    használd a PUT /employees/{id} végpontot `is_active=False` értékkel.

    Args:
        employee_id: Munkatárs egyedi azonosítója
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 403: Ha nincs jogosultság
    """
    success = service.delete_employee(employee_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Munkatárs nem található: {employee_id}"
        )

    return None


# ============================================================================
# RBAC Endpoints
# ============================================================================

@employees_router.post(
    "/{employee_id}/roles",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Szerepkörök hozzárendelése",
    description="Szerepkörök (roles) hozzárendelése munkatárshoz.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def assign_roles(
    employee_id: int,
    role_ids: List[int],
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    """
    Szerepkörök hozzárendelése munkatárshoz.

    **Jogosultság:** `employees:manage`

    **Figyelem:** Ez a művelet felülírja a munkatárs meglévő szerepköreit.

    Args:
        employee_id: Munkatárs egyedi azonosítója
        role_ids: Szerepkör ID-k listája (request body)
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeResponse: Frissített munkatárs adatai

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 400: Ha valamelyik role_id nem létezik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        employee = service.assign_roles(employee_id, role_ids)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Munkatárs nem található: {employee_id}"
            )

        return EmployeeResponse.model_validate(employee)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba a szerepkörök hozzárendelése során: {str(e)}"
        )


@employees_router.get(
    "/{employee_id}/roles",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Munkatárs szerepköreinek lekérése",
    description="Egy munkatárshoz rendelt szerepkörök lekérése.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def get_employee_roles(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> List[dict]:
    """
    Munkatárs szerepköreinek lekérése.

    **Jogosultság:** `employees:manage`

    Args:
        employee_id: Munkatárs egyedi azonosítója
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        List[dict]: Szerepkörök listája

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 403: Ha nincs jogosultság
    """
    # Ellenőrizzük, hogy létezik-e a munkatárs
    employee = service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Munkatárs nem található: {employee_id}"
        )

    roles = service.get_employee_roles(employee_id)

    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at.isoformat() if role.created_at else None
        }
        for role in roles
    ]


@employees_router.get(
    "/{employee_id}/permissions",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Munkatárs jogosultságainak lekérése",
    description="Egy munkatárs összes jogosultságának lekérése (szerepkörökből aggregálva).",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def get_employee_permissions(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> List[dict]:
    """
    Munkatárs jogosultságainak lekérése.

    **Jogosultság:** `employees:manage`

    A jogosultságokat a munkatárs szerepköreiből aggregálja.

    Args:
        employee_id: Munkatárs egyedi azonosítója
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        List[dict]: Jogosultságok listája

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 403: Ha nincs jogosultság
    """
    # Ellenőrizzük, hogy létezik-e a munkatárs
    employee = service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Munkatárs nem található: {employee_id}"
        )

    permissions = service.get_employee_permissions(employee_id)

    return [
        {
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "resource": perm.resource,
            "action": perm.action,
            "created_at": perm.created_at.isoformat() if perm.created_at else None
        }
        for perm in permissions
    ]


# ============================================================================
# Utility Endpoints
# ============================================================================

@employees_router.get(
    "/username/{username}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
    summary="Munkatárs lekérése felhasználónév alapján",
    description="Munkatárs adatainak lekérése felhasználónév (username) alapján.",
    dependencies=[Depends(require_permission("employees:manage"))]
)
async def get_employee_by_username(
    username: str,
    current_user: Employee = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
    """
    Munkatárs lekérése felhasználónév alapján.

    **Jogosultság:** `employees:manage`

    Args:
        username: Felhasználónév
        current_user: Bejelentkezett felhasználó (dependency)
        service: EmployeeService instance (dependency)

    Returns:
        EmployeeResponse: Munkatárs adatai

    Raises:
        HTTPException 404: Ha a munkatárs nem található
        HTTPException 403: Ha nincs jogosultság
    """
    employee = service.get_employee_by_username(username)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Munkatárs nem található: {username}"
        )

    return EmployeeResponse.model_validate(employee)
