"""
Pydantic schemas for Role (Szerepkör) entities.

This module defines the request and response schemas for role operations
in the Service Admin module (Module 8), supporting the role-based access
control (RBAC) system with many-to-many relationships to permissions.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

# Import PermissionResponse for nested relationships
# Note: This will be a forward reference to avoid circular imports
# The actual import happens at runtime


class RoleBase(BaseModel):
    """Base schema for Role with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Role name",
        examples=["Admin", "Manager", "Waiter", "Kitchen Staff", "Cashier"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable description of the role",
        examples=[
            "Rendszergazda - teljes hozzáférés",
            "Menedzser - vezetői funkciók",
            "Pincér - rendelések kezelése",
            "Konyhai személyzet - konyhai műveletek",
            "Pénztáros - fizetések kezelése"
        ]
    )


class RoleCreate(RoleBase):
    """
    Schema for creating a new role.

    Optionally includes permission IDs to associate with the role during creation.
    """

    permission_ids: List[int] = Field(
        default_factory=list,
        description="List of permission IDs to associate with this role",
        examples=[[1, 2, 3], [5, 10, 15], []]
    )


class RoleUpdate(BaseModel):
    """Schema for updating an existing role."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Role name"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Human-readable description of the role"
    )
    permission_ids: Optional[List[int]] = Field(
        None,
        description="List of permission IDs to associate with this role (replaces existing)"
    )


class RoleInDB(RoleBase):
    """Schema for role as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique role identifier",
        examples=[1, 42, 100]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when role was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when role was last updated"
    )


class RoleResponse(RoleInDB):
    """
    Schema for role API responses.

    This is the basic response without nested permissions.
    Use RoleWithPermissionsResponse for detailed role information.
    """
    pass


class RoleWithPermissionsResponse(RoleInDB):
    """
    Schema for role API responses with nested permission details.

    This extended response includes the full list of permissions
    associated with this role, useful for detailed role views.
    """

    # Forward reference to avoid circular imports
    # The PermissionResponse schema will be imported from permission.py
    permissions: List["PermissionResponse"] = Field(  # type: ignore
        default_factory=list,
        description="List of permissions associated with this role"
    )


class RoleListResponse(BaseModel):
    """Schema for paginated role list responses."""

    items: list[RoleResponse] = Field(
        ...,
        description="List of roles"
    )
    total: int = Field(
        ...,
        description="Total number of roles",
        examples=[5, 10, 20]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[20]
    )


# This import is placed at the end to resolve forward references
# It will be needed when the schemas are actually used
try:
    from .permission import PermissionResponse
    # Update forward references for RoleWithPermissionsResponse
    RoleWithPermissionsResponse.model_rebuild()
except ImportError:
    # During schema definition, this import might not be available yet
    pass
