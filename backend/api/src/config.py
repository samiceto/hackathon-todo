"""Application configuration and settings.

Loads environment variables and provides typed settings for the application.
"""
from typing import List, Union
from pydantic import PostgresDsn, field_validator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


def parse_cors_origins(v: str | List[str] | None) -> List[str]:
    """Parse CORS_ORIGINS from various formats.

    Handles:
    - JSON array string: '["http://localhost:3000"]'
    - Comma-separated string: 'http://localhost:3000,https://example.com'
    - Python list: ["http://localhost:3000"]
    - Empty/None: returns default ["http://localhost:3000"]
    """
    # Handle None or empty string - return default
    if v is None or v == "":
        return ["http://localhost:3000"]

    if isinstance(v, str):
        # Remove any whitespace
        v = v.strip()

        # Empty after stripping
        if not v:
            return ["http://localhost:3000"]

        # Try parsing as JSON array
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            # Fallback: split by comma and filter empty strings
            origins = [origin.strip() for origin in v.split(",")]
            return [o for o in origins if o]

    # Already a list
    return v


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: PostgreSQL connection string from Neon
        BETTER_AUTH_SECRET: Shared secret for JWT token signing/verification
        CORS_ORIGINS: List of allowed CORS origins
        DEBUG: Enable debug mode
    """

    # Database configuration
    DATABASE_URL: PostgresDsn

    # Authentication
    BETTER_AUTH_SECRET: str

    # CORS configuration (stored as string to prevent auto-JSON parsing)
    cors_origins_raw: str = Field(
        default='["http://localhost:3000"]',
        alias="CORS_ORIGINS",
        exclude=True  # Exclude from serialization
    )

    # Application environment
    DEBUG: bool = True

    # JWT configuration
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse and return CORS origins as a list.

        This computed field prevents pydantic-settings from auto-parsing
        the CORS_ORIGINS env var as JSON, which fails on empty strings.
        """
        return parse_cors_origins(self.cors_origins_raw)

    @field_validator("BETTER_AUTH_SECRET")
    @classmethod
    def validate_secret_length(cls, v: str) -> str:
        """Ensure BETTER_AUTH_SECRET is at least 32 characters."""
        if len(v) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")
        return v


# Global settings instance
settings = Settings()
