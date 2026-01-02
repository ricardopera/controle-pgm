"""Environment configuration for Controle PGM backend."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Brazil timezone offset (UTC-3)
BRAZIL_TZ_OFFSET = timedelta(hours=-3)
BRAZIL_TZ = timezone(BRAZIL_TZ_OFFSET, "BRT")


def get_brazil_now() -> datetime:
    """Get current datetime in Brazil timezone (America/Sao_Paulo / UTC-3).

    Note: Brazil doesn't observe DST since 2019, so UTC-3 is always correct.

    Returns:
        datetime: Current datetime with Brazil timezone info.
    """
    return datetime.now(BRAZIL_TZ)


def get_current_year() -> int:
    """Get current year in Brazil timezone.

    Returns:
        int: Current year number.
    """
    return get_brazil_now().year


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Azure Tables
    azure_tables_connection_string: str = "UseDevelopmentStorage=true"

    # Azure Redis Cache (for production rate limiting)
    redis_connection_string: str = ""

    # JWT Authentication
    jwt_secret: str = "change-this-in-production-min-32-characters-long"
    jwt_expiration_hours: int = 8
    jwt_algorithm: str = "HS256"

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Timezone (Brazil)
    timezone: str = "America/Sao_Paulo"

    # Password Policy
    password_min_length: int = 8
    bcrypt_cost_factor: int = 12

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 1

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def use_redis_rate_limit(self) -> bool:
        """Check if Redis should be used for rate limiting."""
        return bool(self.redis_connection_string)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function for direct access
settings = get_settings()
