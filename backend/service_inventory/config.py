"""
Configuration module for the Inventory Service (Module 5).

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

    # Google Cloud Project Configuration
    gcp_project_id: str = Field(
        ...,
        description="Google Cloud Project ID",
        min_length=6,
        max_length=30
    )

    # Document AI Configuration
    documentai_processor_id: str = Field(
        ...,
        description="Document AI Processor ID for invoice/receipt OCR",
        min_length=10
    )

    documentai_location: str = Field(
        default="eu",
        description="Document AI processor location (e.g., 'eu', 'us')",
    )

    # Google Cloud Storage Configuration (for invoice uploads)
    gcs_bucket_name: str = Field(
        ...,
        description="GCS bucket name for invoice/receipt documents",
        min_length=3,
        max_length=63
    )

    # Google Application Credentials
    google_application_credentials: str = Field(
        ...,
        description="Path to Google Cloud service account JSON key file",
        examples=["/app/credentials/service-account.json"]
    )

    # Service Configuration
    port: int = Field(
        default=8003,
        description="Port on which the Inventory service will run",
        ge=1024,
        le=65535
    )

    # Menu Service URL (for product reference validation)
    menu_service_url: str = Field(
        default="http://localhost:8000",
        description="URL of the Menu Service for inter-service communication"
    )

    # NAV OSA (Online Számlázó Alkalmazás) Configuration
    # NOTE: NAV credentials are loaded from separate env vars via nav_config.py
    # These are optional documentation fields
    nav_enable_real_api: bool = Field(
        default=False,
        description="Enable real NAV API calls (default: false for MOCK mode)"
    )

    nav_default_test_mode: bool = Field(
        default=True,
        description="Use NAV test environment by default (recommended)"
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
