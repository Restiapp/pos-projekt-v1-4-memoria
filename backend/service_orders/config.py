"""
Configuration module for the Orders Service (Modul 1).

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
        default=8002,
        description="Port on which the service will run",
        ge=1024,
        le=65535
    )

    # Menu Service URL (for inter-service communication)
    menu_service_url: str = Field(
        default="http://localhost:8001",
        description="URL of the Menu Service for fetching product information"
    )

    # Admin Service URL (for NTAK reporting)
    admin_service_url: str = Field(
        default="http://localhost:8008",
        description="URL of the Admin Service for NTAK data reporting"
    )

    # Inventory Service URL (for stock deduction)
    inventory_service_url: str = Field(
        default="http://localhost:8003",
        description="URL of the Inventory Service for stock deduction"
    )

    # Order Configuration
    max_order_items: int = Field(
        default=50,
        description="Maximum number of items allowed in a single order",
        ge=1,
        le=100
    )

    # Kitchen Display Configuration
    kitchen_display_refresh_interval: int = Field(
        default=5,
        description="Kitchen display refresh interval in seconds",
        ge=1,
        le=60
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
