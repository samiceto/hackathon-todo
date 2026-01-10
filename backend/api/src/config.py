"""Application configuration and settings.

Loads environment variables and provides typed settings for the application.
"""
from typing import List
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


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

    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

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

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS_ORIGINS from JSON string or list.

        Allows CORS_ORIGINS to be specified as:
        - JSON array string: '["http://localhost:3000"]'
        - Python list: ["http://localhost:3000"]
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fallback: split by comma
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("BETTER_AUTH_SECRET")
    @classmethod
    def validate_secret_length(cls, v: str) -> str:
        """Ensure BETTER_AUTH_SECRET is at least 32 characters."""
        if len(v) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")
        return v


# Global settings instance
settings = Settings()
