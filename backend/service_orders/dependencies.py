"""
FastAPI Dependencies - Service Orders Authentication
JWT token validation via HTTP to service_admin

This module provides authentication dependencies for service_orders
by validating JWT tokens through HTTP requests to service_admin.
"""

import os
from typing import Optional, Callable
import httpx

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# HTTP Bearer token scheme
security = HTTPBearer()

# Admin service URL from environment
ADMIN_SERVICE_URL = os.getenv("ADMIN_SERVICE_URL", "http://localhost:8008")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validates JWT token by calling service_admin /api/v1/auth/me endpoint.

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        dict: User data from service_admin

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Call service_admin to validate token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ADMIN_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


def require_permission(permission: str) -> Callable:
    """
    Creates a dependency that requires a specific permission.

    Args:
        permission: Required permission string (e.g., "orders:manage")

    Returns:
        Callable: FastAPI dependency function

    Example:
        @app.get("/orders", dependencies=[Depends(require_permission("orders:view"))])
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        """Check if current user has required permission"""
        user_permissions = current_user.get("permissions", [])

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )

        return current_user

    return permission_checker
