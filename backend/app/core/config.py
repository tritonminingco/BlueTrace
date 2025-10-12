"""Configuration management using Pydantic Settings."""
import json
from typing import Any, Dict, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RateLimitConfig(BaseSettings):
    """Rate limit configuration per plan."""

    requests: int
    window: int  # seconds


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    # Database
    POSTGRES_DSN: str = Field(
        default="postgresql://bluetrace:bluetrace@localhost:5432/bluetrace"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # API
    API_BASE_URL: str = Field(default="http://localhost:8080")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"]
    )
    LOG_LEVEL: str = Field(default="INFO")

    # Stripe
    STRIPE_SECRET_KEY: str = Field(default="")
    STRIPE_WEBHOOK_SECRET: str = Field(default="")
    STRIPE_PRODUCT_FREE: str = Field(default="")
    STRIPE_PRODUCT_PRO: str = Field(default="")
    STRIPE_PRODUCT_ENTERPRISE: str = Field(default="")

    # Rate Limits
    RATE_LIMITS_JSON: str = Field(
        default='{"free": {"requests": 30, "window": 60}, "pro": {"requests": 300, "window": 60}, "enterprise": {"requests": 10000, "window": 60}}'
    )

    # Admin
    ADMIN_SEED_EMAIL: str = Field(default="admin@bluetrace.dev")

    # Security
    SECRET_KEY: str = Field(default="change-this-secret-key")
    API_KEY_SALT: str = Field(default="change-this-salt")

    # Telemetry
    OTEL_SERVICE_NAME: str = Field(default="bluetrace-api")
    OTEL_EXPORTER_TYPE: str = Field(default="console")

    # Workers
    DRAMATIQ_BROKER: str = Field(default="redis")
    DRAMATIQ_THREADS: int = Field(default=8)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    def get_rate_limits(self) -> Dict[str, RateLimitConfig]:
        """Parse and return rate limit configurations."""
        limits_dict = json.loads(self.RATE_LIMITS_JSON)
        return {
            plan: RateLimitConfig(**config) for plan, config in limits_dict.items()
        }


settings = Settings()

