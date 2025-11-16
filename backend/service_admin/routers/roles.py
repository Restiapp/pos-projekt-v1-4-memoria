"""
Role API Routes
Module 6: RBAC (Role-Based Access Control) - Phase 4.2

Ez a modul tartalmazza a Role (Szerepkör) entitáshoz kapcsolódó FastAPI végpontokat.
Implementálja a teljes CRUD műveletsort a szerepkörök kezeléséhez.

Biztonsági követelmények:
- Minden végpont védett a require_permission("roles:manage") függőséggel
- Csak jogosult felhasználók férhetnek hozzá a szerepkör-kezelő API-hoz
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.services.role_service import RoleService
from backend.service_admin.dependencies import require_permission, get_current_user
from backend.service_admin.models.employee import Employee
from backend.service_admin.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissionsResponse,
    RoleListResponse
)


# Router létrehozása
router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    dependencies=[Depends(require_permission("roles:manage"))]
)


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    """
    Dependency function a RoleService injektálásához.

    Args:
        db: Database session (injected)

    Returns:
        RoleService: Role service instance
    """
    return RoleService(db)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    description="""
    Create a new role in the RBAC system.

    This endpoint allows you to create a new role with permissions.

    **Security:**
    - Requires permission: `roles:manage`

    **Requirements:**
    - Role name is required (1-100 characters) and must be unique
    - Description is required (1-255 characters)
    - Optional: List of permission IDs to associate with the role

    **Returns:**
    - 201: Successfully created role with all details
    - 400: Invalid input data or duplicate role name
    - 403: Permission denied (missing roles:manage permission)
    - 404: One or more permission IDs not found
    """
)
def create_role(
    role_data: RoleCreate,
    service: RoleService = Depends(get_role_service),
    current_user: Employee = Depends(get_current_user)
):
    """
    Új szerepkör létrehozása.

    Args:
        role_data: RoleCreate schema with role details
        service: RoleService instance (injected)
        current_user: Current authenticated user (injected)

    Returns:
        RoleResponse: Created role details

    Raises:
        HTTPException 400: If role name already exists or validation fails
        HTTPException 404: If any permission_id not found
        HTTPException 403: If user lacks roles:manage permission
    """
    try:
        role = service.create_role(role_data)
        return role
    except HTTPException:
        # Re-raise HTTPException from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the role: {str(e)}"
        )


@router.get(
    "",
    response_model=RoleListResponse,
    summary="Get all roles with pagination",
    description="""
    Retrieve a paginated list of roles with optional filtering.

    This endpoint supports:
    - **Pagination**: Control the number of results and skip records
    - **Filtering**: Filter by active status, system role status

    **Security:**
    - Requires permission: `roles:manage`

    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 20, max: 100)
    - `is_active`: Filter by active status (optional)
    - `is_system`: Filter by system role status (optional)

    **Returns:**
    - 200: Paginated list of roles with metadata (total count, page info)
    - 403: Permission denied (missing roles:manage permission)
    """
)
def get_roles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Filter by system role status"),
    service: RoleService = Depends(get_role_service),
    current_user: Employee = Depends(get_current_user)
):
    """
    Szerepkörök listázása lapozással és szűréssel.

    Args:
        skip: Pagination offset
        limit: Page size
        is_active: Optional active status filter
        is_system: Optional system role filter
        service: RoleService instance (injected)
        current_user: Current authenticated user (injected)

    Returns:
        RoleListResponse: Paginated list with metadata

    Raises:
        HTTPException 403: If user lacks roles:manage permission
    """
    try:
        # Szerepkörök lekérése
        roles = service.get_all_roles(
            skip=skip,
            limit=limit,
            is_active=is_active,
            is_system=is_system
        )

        # Összesített számosság
        total = service.count_roles(
            is_active=is_active,
            is_system=is_system
        )

        # Oldalszám számítása
        page = (skip // limit) + 1 if limit > 0 else 1

        return RoleListResponse(
            items=roles,
            total=total,
            page=page,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving roles: {str(e)}"
        )


@router.get(
    "/{role_id}",
    response_model=RoleWithPermissionsResponse,
    summary="Get role by ID",
    description="""
    Retrieve a single role by its unique identifier with permissions.

    **Security:**
    - Requires permission: `roles:manage`

    **Path Parameters:**
    - `role_id`: Unique role identifier (integer)

    **Returns:**
    - 200: Role details with associated permissions
    - 404: Role not found
    - 403: Permission denied (missing roles:manage permission)
    """
)
def get_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
    current_user: Employee = Depends(get_current_user)
):
    """
    Szerepkör lekérdezése ID alapján.

    Args:
        role_id: Role unique identifier
        service: RoleService instance (injected)
        current_user: Current authenticated user (injected)

    Returns:
        RoleWithPermissionsResponse: Role details with permissions

    Raises:
        HTTPException 404: If role not found
        HTTPException 403: If user lacks roles:manage permission
    """
    try:
        role = service.get_role(role_id)
        return role
    except HTTPException:
        # Re-raise HTTPException from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the role: {str(e)}"
        )


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update role",
    description="""
    Update an existing role by its ID.

    This endpoint allows partial updates - you only need to provide the fields
    you want to change. All other fields will remain unchanged.

    **Security:**
    - Requires permission: `roles:manage`

    **Path Parameters:**
    - `role_id`: Unique role identifier (integer)

    **Request Body:**
    - Any combination of updatable fields (all optional)
    - `name`: New role name (must be unique)
    - `description`: New description
    - `permission_ids`: New list of permission IDs (replaces existing)

    **Returns:**
    - 200: Updated role details
    - 404: Role not found
    - 400: Invalid update data or duplicate role name
    - 403: Permission denied (missing roles:manage permission)
    """
)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    current_user: Employee = Depends(get_current_user)
):
    """
    Szerepkör frissítése.

    Args:
        role_id: Role unique identifier
        role_data: RoleUpdate schema with fields to update
        service: RoleService instance (injected)
        current_user: Current authenticated user (injected)

    Returns:
        RoleResponse: Updated role details

    Raises:
        HTTPException 404: If role not found
        HTTPException 400: If validation fails or role name already exists
        HTTPException 403: If user lacks roles:manage permission
    """
    try:
        role = service.update_role(role_id, role_data)
        return role
    except HTTPException:
        # Re-raise HTTPException from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the role: {str(e)}"
        )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete role",
    description="""
    Delete a role by its ID.

    **Warning:** This is a hard delete operation. The role will be permanently
    removed from the database.

    **Security:**
    - Requires permission: `roles:manage`
    - System roles (is_system=True) cannot be deleted

    **Path Parameters:**
    - `role_id`: Unique role identifier (integer)

    **Returns:**
    - 204: Role successfully deleted (no content)
    - 404: Role not found
    - 400: Cannot delete system role
    - 403: Permission denied (missing roles:manage permission)
    """
)
def delete_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
    current_user: Employee = Depends(get_current_user)
):
    """
    Szerepkör törlése.

    Args:
        role_id: Role unique identifier
        service: RoleService instance (injected)
        current_user: Current authenticated user (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If role not found
        HTTPException 400: If trying to delete a system role
        HTTPException 403: If user lacks roles:manage permission
    """
    try:
        service.delete_role(role_id)
        return None
    except HTTPException:
        # Re-raise HTTPException from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the role: {str(e)}"
        )


# Export the router
roles_router = router
