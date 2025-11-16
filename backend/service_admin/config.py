"""
Configuration module for the Admin Service (Modul 8).

This module uses Pydantic Settings to load and validate environment variables
from the .env file. All configuration values are type-checked and validated
at application startup.

Manages NTAK (National Tax and Customs Administration) integration settings
and inter-service communication URLs.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from a .env file in the same directory
    as this module. All fields are required unless a default value is provided.
    """

    # Service Configuration
    port: int = Field(
        default=8008,
        description="Port on which the Admin Service will run",
        ge=1024,
        le=65535
    )

    # NTAK Configuration
    ntak_enabled: bool = Field(
        default=True,
        description="Enable/disable NTAK reporting functionality"
    )

    ntak_api_url: str = Field(
        default="https://ntak-test.gov.hu/api/v1",
        description="NTAK API endpoint URL"
    )

    ntak_api_key: str = Field(
        ...,
        description="NTAK API authentication key"
    )

    ntak_restaurant_id: str = Field(
        default="REST12345",
        description="NTAK registered restaurant identifier"
    )

    ntak_tax_number: str = Field(
        ...,
        description="Restaurant tax identification number"
    )

    ntak_report_interval: int = Field(
        default=3600,
        description="NTAK reporting interval in seconds (default: 1 hour)",
        ge=60,
        le=86400
    )

    # Inter-Service Communication URLs
    orders_service_url: str = Field(
        default="http://localhost:8002",
        description="URL of the Orders Service for fetching order data"
    )

    menu_service_url: str = Field(
        default="http://localhost:8001",
        description="URL of the Menu Service for product information"
    )

    inventory_service_url: str = Field(
        default="http://localhost:8003",
        description="URL of the Inventory Service for stock data"
    )

    # Database Configuration (if needed for admin data)
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection string for admin data storage"
    )

    # Admin Service Settings
    admin_session_timeout: int = Field(
        default=3600,
        description="Admin session timeout in seconds (default: 1 hour)",
        ge=300,
        le=86400
    )

    admin_password_min_length: int = Field(
        default=8,
        description="Minimum password length for admin users",
        ge=6,
        le=128
    )

    # JWT Authentication Configuration (Module 6 - RBAC)
    jwt_secret_key: str = Field(
        ...,
        description="Secret key for JWT token signing (use strong random string)",
        min_length=32
    )

    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm (HS256, HS384, HS512)"
    )

    jwt_access_token_expire_minutes: int = Field(
        default=60,
        description="JWT access token expiration time in minutes",
        ge=5,
        le=1440
    )

    # PIN Code Configuration (Module 6 - RBAC)
    pin_code_min_length: int = Field(
        default=4,
        description="Minimum PIN code length for employee authentication",
        ge=4,
        le=8
    )

    pin_code_max_length: int = Field(
        default=6,
        description="Maximum PIN code length for employee authentication",
        ge=4,
        le=8
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )


# Create a singleton instance of settings
settings = Settings()
