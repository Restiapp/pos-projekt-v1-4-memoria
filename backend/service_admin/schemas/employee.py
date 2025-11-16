"""
Pydantic schemas for Employee (Munkatárs) entities.

This module defines the request and response schemas for employee operations
in the Service Admin module (Module 8), including employee management and
role-based access control (RBAC).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class EmployeeBase(BaseModel):
    """Base schema for Employee with common fields."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Unique username for login",
        examples=["jkovacs", "mnagy", "admin"]
    )
    email: EmailStr = Field(
        ...,
        description="Employee email address",
        examples=["janos.kovacs@example.com", "maria.nagy@example.com"]
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Employee full name",
        examples=["Kovács János", "Nagy Mária", "Tóth Péter"]
    )
    is_active: bool = Field(
        True,
        description="Flag indicating if the employee account is active",
        examples=[True, False]
    )
    role_id: Optional[int] = Field(
        None,
        description="Role identifier for RBAC (foreign key to Role)",
        examples=[1, 2, 3, None]
    )


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Employee password (will be hashed before storage)",
        examples=["SecurePass123!", "MyP@ssw0rd"]
    )


class EmployeeUpdate(BaseModel):
    """Schema for updating an existing employee."""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Unique username for login"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Employee email address"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Employee full name"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Flag indicating if the employee account is active"
    )
    role_id: Optional[int] = Field(
        None,
        description="Role identifier for RBAC"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=255,
        description="New password (will be hashed before storage)"
    )


class EmployeeInDB(EmployeeBase):
    """Schema for employee as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique employee identifier",
        examples=[1, 42, 100]
    )
    password_hash: str = Field(
        ...,
        description="Hashed employee password"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when employee was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when employee was last updated"
    )


class EmployeeResponse(BaseModel):
    """
    Schema for employee API responses.

    Note: This excludes the password_hash field for security reasons.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique employee identifier",
        examples=[1, 42, 100]
    )
    username: str = Field(
        ...,
        description="Employee username",
        examples=["jkovacs", "mnagy"]
    )
    email: EmailStr = Field(
        ...,
        description="Employee email address",
        examples=["janos.kovacs@example.com"]
    )
    full_name: str = Field(
        ...,
        description="Employee full name",
        examples=["Kovács János"]
    )
    is_active: bool = Field(
        ...,
        description="Flag indicating if the employee account is active",
        examples=[True, False]
    )
    role_id: Optional[int] = Field(
        None,
        description="Role identifier for RBAC",
        examples=[1, 2, 3, None]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when employee was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when employee was last updated"
    )


class EmployeeListResponse(BaseModel):
    """Schema for paginated employee list responses."""

    items: list[EmployeeResponse] = Field(
        ...,
        description="List of employees"
    )
    total: int = Field(
        ...,
        description="Total number of employees",
        examples=[10, 50, 100]
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
