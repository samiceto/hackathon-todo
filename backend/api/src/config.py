"""Application configuration and settings.

Loads environment variables and provides typed settings for the application.
Supports Dapr Secrets API for fetching secrets from Kubernetes Secrets or other secret stores.
"""
from typing import List, Union, Optional, Dict, Any
from pydantic import PostgresDsn, field_validator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import logging
import os

logger = logging.getLogger(__name__)


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

    # OpenAI API
    OPENAI_API_KEY: str

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


# Dapr Secrets Integration (T085)
class DaprSecretsConfig:
    """Helper class for fetching secrets from Dapr Secrets API.

    This class provides methods to fetch secrets from Dapr Secrets Store
    instead of directly from environment variables. This enables:
    - Centralized secret management via Kubernetes Secrets, Vault, or cloud secret stores
    - Automatic secret rotation without application restart
    - Better security by avoiding hardcoded secrets in environment variables

    Usage:
        >>> dapr_secrets = DaprSecretsConfig(
        ...     secret_store_name="kubernetes-secrets",
        ...     use_dapr=True
        ... )
        >>> api_key = dapr_secrets.get_secret("OPENAI_API_KEY")

    Fallback: If Dapr is not available or use_dapr=False, falls back to os.getenv()
    """

    def __init__(
        self,
        secret_store_name: str = "kubernetes-secrets",
        use_dapr: bool = False,
        dapr_http_port: int = 3500
    ):
        """Initialize DaprSecretsConfig.

        Args:
            secret_store_name: Name of the Dapr Secrets Store component
            use_dapr: Whether to use Dapr Secrets API (default: False = use env vars)
            dapr_http_port: Dapr HTTP port (default: 3500)
        """
        self.secret_store_name = secret_store_name
        self.use_dapr = use_dapr
        self.dapr_http_port = dapr_http_port
        self._cache: Dict[str, str] = {}

    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret value from Dapr Secrets Store or environment variable.

        Args:
            secret_key: Name of the secret to fetch
            default: Default value if secret not found

        Returns:
            Secret value or default

        Example:
            >>> config = DaprSecretsConfig(use_dapr=True)
            >>> api_key = config.get_secret("OPENAI_API_KEY")
        """
        # Check cache first
        if secret_key in self._cache:
            return self._cache[secret_key]

        # Use Dapr if enabled
        if self.use_dapr:
            try:
                from dapr.clients import DaprClient

                with DaprClient(http_port=self.dapr_http_port) as client:
                    # Fetch secret from Dapr Secrets Store
                    secret_response = client.get_secret(
                        store_name=self.secret_store_name,
                        key=secret_key
                    )

                    # Dapr returns dict with secret key -> secret value
                    secret_value = secret_response.secret.get(secret_key)

                    if secret_value:
                        # Cache the secret
                        self._cache[secret_key] = secret_value
                        logger.info(f"Fetched secret from Dapr: {secret_key}")
                        return secret_value
                    else:
                        logger.warning(
                            f"Secret not found in Dapr store: {secret_key}. "
                            f"Falling back to environment variable."
                        )

            except Exception as e:
                logger.warning(
                    f"Failed to fetch secret from Dapr: {secret_key}. "
                    f"Error: {str(e)}. Falling back to environment variable."
                )

        # Fallback: Use environment variable
        env_value = os.getenv(secret_key, default)
        if env_value:
            self._cache[secret_key] = env_value
        return env_value

    def get_all_secrets(self) -> Dict[str, str]:
        """Get all secrets from Dapr Secrets Store.

        Returns:
            Dictionary of secret_key -> secret_value

        Example:
            >>> config = DaprSecretsConfig(use_dapr=True)
            >>> secrets = config.get_all_secrets()
            >>> print(secrets.keys())
            dict_keys(['OPENAI_API_KEY', 'BETTER_AUTH_SECRET'])
        """
        if not self.use_dapr:
            logger.warning("get_all_secrets() only works with use_dapr=True")
            return {}

        try:
            from dapr.clients import DaprClient

            with DaprClient(http_port=self.dapr_http_port) as client:
                # Fetch all secrets from Dapr Secrets Store
                bulk_response = client.get_bulk_secret(
                    store_name=self.secret_store_name
                )

                # Convert to flat dict
                all_secrets = {}
                for secret_key, secret_data in bulk_response.secrets.items():
                    all_secrets[secret_key] = secret_data.get(secret_key, "")

                logger.info(f"Fetched {len(all_secrets)} secrets from Dapr")
                return all_secrets

        except Exception as e:
            logger.error(f"Failed to fetch bulk secrets from Dapr: {str(e)}")
            return {}


# Global settings instance
settings = Settings()

# Dapr Secrets helper (enable with use_dapr=True in production)
dapr_secrets = DaprSecretsConfig(
    secret_store_name=os.getenv("DAPR_SECRET_STORE_NAME", "kubernetes-secrets"),
    use_dapr=os.getenv("USE_DAPR_SECRETS", "false").lower() == "true",
    dapr_http_port=int(os.getenv("DAPR_HTTP_PORT", "3500"))
)
