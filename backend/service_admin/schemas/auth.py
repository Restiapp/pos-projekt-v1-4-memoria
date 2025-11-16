"""
Pydantic schemas for Authentication (Hitelesítés) entities.

This module defines the request and response schemas for authentication operations
in the Service Admin module (Module 8), including login, token management, and
current user context for the role-based access control (RBAC) system.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    """
    Schema for employee login request.

    This schema defines the credentials required for an employee to
    authenticate and obtain an access token for API operations.
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Employee username",
        examples=["jkovacs", "mnagy", "admin"]
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Employee password",
        examples=["SecurePass123!", "MyP@ssw0rd"]
    )


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.

    This schema is returned after a successful login, providing the
    JWT access token and related metadata for authenticating subsequent
    API requests.
    """

    access_token: str = Field(
        ...,
        description="JWT access token for authenticating API requests",
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ]
    )
    token_type: str = Field(
        "bearer",
        description="Token type (always 'bearer' for JWT)",
        examples=["bearer"]
    )
    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds",
        examples=[3600, 7200, 86400]
    )
    issued_at: datetime = Field(
        ...,
        description="Timestamp when the token was issued",
        examples=["2024-01-15T14:30:00Z", "2024-02-20T18:45:00Z"]
    )


class CurrentUser(BaseModel):
    """
    Schema for the currently authenticated user context.

    This schema represents the current user's identity and permissions,
    typically extracted from the JWT token and used throughout the application
    to enforce role-based access control (RBAC).
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
        examples=["jkovacs", "mnagy", "admin"]
    )
    email: str = Field(
        ...,
        description="Employee email address",
        examples=["janos.kovacs@example.com", "maria.nagy@example.com"]
    )
    full_name: str = Field(
        ...,
        description="Employee full name",
        examples=["Kovács János", "Nagy Mária", "Admin User"]
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
    role_name: Optional[str] = Field(
        None,
        description="Role name for display purposes",
        examples=["Admin", "Manager", "Waiter", None]
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="List of permission names (e.g., 'view_orders', 'create_employee')",
        examples=[
            ["view_orders", "create_employee", "manage_inventory"],
            ["view_orders"],
            []
        ]
    )


class PasswordChangeRequest(BaseModel):
    """
    Schema for password change request.

    This schema is used when an authenticated employee wants to change
    their own password.
    """

    current_password: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Current password for verification",
        examples=["OldPass123!"]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="New password (minimum 8 characters)",
        examples=["NewSecurePass456!"]
    )


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset request (admin operation).

    This schema is used when an administrator resets another employee's
    password without requiring the current password.
    """

    employee_id: int = Field(
        ...,
        description="Employee ID whose password should be reset",
        examples=[1, 42, 100]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="New password (minimum 8 characters)",
        examples=["ResetPass789!"]
    )
