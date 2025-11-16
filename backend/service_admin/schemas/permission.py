"""
Pydantic schemas for Permission (Jogosultság) entities.

This module defines the request and response schemas for permission operations
in the Service Admin module (Module 8), enabling fine-grained access control
within the role-based access control (RBAC) system.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PermissionBase(BaseModel):
    """Base schema for Permission with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern="^[a-z_]+$",
        description="Permission name in snake_case (e.g., 'view_orders', 'create_employee')",
        examples=["view_orders", "create_employee", "delete_product", "manage_inventory"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable description of the permission",
        examples=[
            "Rendelések megtekintése",
            "Munkatársak létrehozása",
            "Termékek törlése",
            "Készletkezelés"
        ]
    )
    resource: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Resource/entity this permission applies to (e.g., 'orders', 'employees', 'products')",
        examples=["orders", "employees", "products", "inventory", "menu", "tables"]
    )
    action: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Action allowed on the resource (e.g., 'view', 'create', 'update', 'delete', 'manage')",
        examples=["view", "create", "update", "delete", "manage"]
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating an existing permission."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern="^[a-z_]+$",
        description="Permission name in snake_case"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Human-readable description of the permission"
    )
    resource: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Resource/entity this permission applies to"
    )
    action: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Action allowed on the resource"
    )


class PermissionInDB(PermissionBase):
    """Schema for permission as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique permission identifier",
        examples=[1, 42, 100]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when permission was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when permission was last updated"
    )


class PermissionResponse(PermissionInDB):
    """Schema for permission API responses."""
    pass


class PermissionListResponse(BaseModel):
    """Schema for paginated permission list responses."""

    items: list[PermissionResponse] = Field(
        ...,
        description="List of permissions"
    )
    total: int = Field(
        ...,
        description="Total number of permissions",
        examples=[20, 50, 100]
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
