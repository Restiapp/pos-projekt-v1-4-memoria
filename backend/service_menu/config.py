"""
Configuration module for the Menu Service (Modul 0).

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

    # Google Cloud Storage Configuration
    gcs_bucket_name: str = Field(
        ...,
        description="GCS bucket name for product images",
        min_length=3,
        max_length=63
    )

    # Google Cloud Project Configuration
    gcp_project_id: str = Field(
        ...,
        description="Google Cloud Project ID",
        min_length=6,
        max_length=30
    )

    # Vertex AI Configuration
    vertex_ai_location: str = Field(
        ...,
        description="Vertex AI region/location for Translation API",
        examples=["europe-west1", "us-central1"]
    )

    # Service Configuration
    port: int = Field(
        default=8001,
        description="Port on which the service will run",
        ge=1024,
        le=65535
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
