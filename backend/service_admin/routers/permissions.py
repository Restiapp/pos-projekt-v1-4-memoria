"""
Permission Router for Module 6 - Phase 4.3.

This module provides CRUD API endpoints for managing permissions.
All endpoints are protected with permissions:manage permission.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.database import get_db
from backend.service_admin.services.permission_service import PermissionService
from backend.service_admin.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionListResponse
)
from backend.service_admin.models.employee import Employee
from backend.service_admin.dependencies import get_current_user, require_permission


# Router configuration
router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Permission not found"}}
)


def get_permission_service(db: Session = Depends(get_db)) -> PermissionService:
    """
    Dependency factory for PermissionService.

    Args:
        db: Database session

    Returns:
        PermissionService instance
    """
    return PermissionService(db)


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new permission",
    description="Create a new permission. Requires permissions:manage permission.",
    dependencies=[Depends(require_permission("permissions:manage"))]
)
async def create_permission(
    permission_data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
    current_user: Employee = Depends(get_current_user)
) -> PermissionResponse:
    """
    Create a new permission.

    Args:
        permission_data: Permission creation data
        service: PermissionService instance
        current_user: Authenticated user (from dependency)

    Returns:
        Created permission data

    Raises:
        HTTPException: If permission name already exists (400)
    """
    try:
        permission = service.create_permission(permission_data)
        return PermissionResponse.model_validate(permission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=PermissionListResponse,
    summary="Get all permissions",
    description="Retrieve all permissions with optional filtering. Requires permissions:manage permission.",
    dependencies=[Depends(require_permission("permissions:manage"))]
)
async def get_permissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    resource: Optional[str] = Query(None, description="Filter by resource (e.g., 'orders', 'inventory')"),
    action: Optional[str] = Query(None, description="Filter by action (e.g., 'view', 'create', 'delete')"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Filter by system permission flag"),
    service: PermissionService = Depends(get_permission_service),
    current_user: Employee = Depends(get_current_user)
) -> PermissionListResponse:
    """
    Retrieve all permissions with optional filtering and pagination.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        resource: Optional resource filter
        action: Optional action filter
        is_active: Optional active status filter
        is_system: Optional system permission filter
        service: PermissionService instance
        current_user: Authenticated user (from dependency)

    Returns:
        Paginated list of permissions with metadata
    """
    permissions = service.get_all_permissions(
        skip=skip,
        limit=limit,
        resource=resource,
        action=action,
        is_active=is_active,
        is_system=is_system
    )

    total = service.count_permissions(
        resource=resource,
        action=action,
        is_active=is_active,
        is_system=is_system
    )

    # Calculate page number (1-indexed)
    page = (skip // limit) + 1 if limit > 0 else 1

    return PermissionListResponse(
        items=[PermissionResponse.model_validate(p) for p in permissions],
        total=total,
        page=page,
        page_size=limit
    )


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by ID",
    description="Retrieve a specific permission by ID. Requires permissions:manage permission.",
    dependencies=[Depends(require_permission("permissions:manage"))]
)
async def get_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
    current_user: Employee = Depends(get_current_user)
) -> PermissionResponse:
    """
    Retrieve a specific permission by ID.

    Args:
        permission_id: Permission ID
        service: PermissionService instance
        current_user: Authenticated user (from dependency)

    Returns:
        Permission data

    Raises:
        HTTPException: If permission not found (404)
    """
    permission = service.get_permission(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found"
        )
    return PermissionResponse.model_validate(permission)


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Update permission",
    description="Update an existing permission. Requires permissions:manage permission.",
    dependencies=[Depends(require_permission("permissions:manage"))]
)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
    current_user: Employee = Depends(get_current_user)
) -> PermissionResponse:
    """
    Update an existing permission.

    Args:
        permission_id: Permission ID to update
        permission_data: Permission update data (all fields optional)
        service: PermissionService instance
        current_user: Authenticated user (from dependency)

    Returns:
        Updated permission data

    Raises:
        HTTPException: If permission not found (404) or validation error (400)
    """
    try:
        permission = service.update_permission(permission_id, permission_data)
        return PermissionResponse.model_validate(permission)
    except ValueError as e:
        # Check if it's a "not found" error or validation error
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete permission",
    description="Delete a permission (soft delete for system permissions). Requires permissions:manage permission.",
    dependencies=[Depends(require_permission("permissions:manage"))]
)
async def delete_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
    current_user: Employee = Depends(get_current_user)
) -> None:
    """
    Delete a permission.

    System permissions cannot be deleted, only deactivated.

    Args:
        permission_id: Permission ID to delete
        service: PermissionService instance
        current_user: Authenticated user (from dependency)

    Raises:
        HTTPException: If permission not found (404) or is system permission (400)
    """
    try:
        result = service.delete_permission(permission_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID {permission_id} not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Export the router
permissions_router = router
