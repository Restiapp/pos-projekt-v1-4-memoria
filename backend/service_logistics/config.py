"""
Configuration module for the Logistics Service (V3.0 Module).

This module uses Pydantic Settings to load and validate environment variables
from the .env file. All configuration values are type-checked and validated
at application startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from a .env file in the same directory
    as this module. All fields are required unless a default value is provided.
    """

    # Database Configuration
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection string",
        examples=["postgresql://pos_user:password@localhost:5432/pos_db"]
    )

    # Service Configuration
    port: int = Field(
        default=8005,
        description="Port on which the service will run",
        ge=1024,
        le=65535
    )

    # Orders Service URL (for delivery assignment)
    orders_service_url: str = Field(
        default="http://localhost:8002",
        description="URL of the Orders Service for delivery assignment"
    )

    # Admin Service URL (for authentication and RBAC)
    admin_service_url: str = Field(
        default="http://localhost:8008",
        description="URL of the Admin Service for authentication"
    )

    # Logistics Configuration
    default_delivery_time_minutes: int = Field(
        default=30,
        description="Default delivery time in minutes",
        ge=5,
        le=120
    )

    max_delivery_distance_km: float = Field(
        default=10.0,
        description="Maximum delivery distance in kilometers",
        ge=1.0,
        le=50.0
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
