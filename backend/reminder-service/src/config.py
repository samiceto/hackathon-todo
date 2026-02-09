"""Configuration for Reminder Service."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/hackathon_todo"
    )

    # Dapr
    dapr_http_port: int = int(os.getenv("DAPR_HTTP_PORT", "3500"))
    dapr_grpc_port: int = int(os.getenv("DAPR_GRPC_PORT", "50001"))
    pubsub_name: str = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")

    # Service
    port: int = int(os.getenv("PORT", "8001"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Processing
    reminder_batch_size: int = int(os.getenv("REMINDER_BATCH_SIZE", "100"))

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
