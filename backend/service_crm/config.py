"""
Configuration module for the CRM Service (Module 5).

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
        default=8004,
        description="Port on which the CRM service will run",
        ge=1024,
        le=65535
    )

    # Admin Service URL (for authentication/authorization)
    admin_service_url: str = Field(
        default="http://localhost:8008",
        description="URL of the Admin Service for authentication"
    )

    # Orders Service URL (for customer order history)
    orders_service_url: str = Field(
        default="http://localhost:8002",
        description="URL of the Orders Service for customer purchase history"
    )

    # CRM Configuration
    customer_loyalty_points_enabled: bool = Field(
        default=True,
        description="Enable loyalty points system for customers"
    )

    default_loyalty_points_ratio: float = Field(
        default=0.01,
        description="Default loyalty points earned per HUF spent (1% = 0.01)",
        ge=0.0,
        le=1.0
    )

    coupon_max_discount_percentage: float = Field(
        default=50.0,
        description="Maximum discount percentage allowed for coupons",
        ge=0.0,
        le=100.0
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
