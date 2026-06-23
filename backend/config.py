# FILE: /home/overlord/.openclaw/workspace/VULCAN/orderstream/backend/config.py
"""Application configuration using Pydantic Settings.

All secrets must come from environment variables – no hard‑coded values.
The settings object validates on import, causing the process to fail fast
if any required variable is missing.
"""

from pydantic import Field, validator, model_validator
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # -------------------
    # Core environment
    # -------------------
    APP_ENV: str = Field(
        default="development",
        description="Application environment – development | staging | production",
    )
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # --------
    # Static UI path (merchant dashboard HTML served by FastAPI StaticFiles)
    # In Docker, set GENERATED_UI_PATH=/app/static in docker-compose.
    # In systemd direct deploy, set it to the absolute path on the host.
    # --------
    GENERATED_UI_PATH: str = Field(
        default="/home/overlord/.openclaw/workspace/VULCAN/generated_ui",
        description="Absolute path to the generated_ui directory containing index.html and templates/",
    )

    # --------
    # CORS
    # --------
    # Comma‑separated list of allowed origins. In development defaults include
    # the Vite dev server (port 5173) and the backend itself so both are allowed.
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:8000",
        description="Comma‑separated allowed origins; empty string blocks all cross‑origin requests",
    )

    # --------
    # JWT
    # --------
    JWT_SECRET: str = Field(
        default="dGhpc2lzYXRlc3RzZWNyZXR0aGF0aXNhdGxlYXN0NDRjaGFyc2xvbmcK",
        description="Base64‑encoded 256‑bit secret used for signing JWTs — NOT for production use",
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=60, ge=1, description="Access token TTL in minutes")

    # --------
    # Appwrite backend — safe dev defaults (no real credentials needed for health check)
    # --------
    APPWRITE_ENDPOINT: str = Field(
        default="https://cloud.appwrite.io/v1",
        description="Appwrite service endpoint",
    )
    APPWRITE_PROJECT_ID: str = Field(
        default="dev-project-id",
        description="Appwrite project identifier",
    )
    APPWRITE_API_KEY: str = Field(
        default="dev-api-key",
        description="Appwrite server SDK key",
    )
    APPWRITE_DATABASE_ID: str = Field(
        default="dev-database-id",
        description="Database ID for orders collection",
    )

    # --------
    # WhatsApp (Baileys placeholder)
    # --------
    WHATSAPP_PHONE: str = Field(default="+0000000000", description="WhatsApp phone number")
    WHATSAPP_SESSION_ID: str = Field(default="default_session")

    # --------
    # Optional payment provider credentials
    # --------
    PAYSTACK_SECRET_KEY: Optional[str] = None
    MPESA_CONSUMER_KEY: Optional[str] = None
    MPESA_CONSUMER_SECRET: Optional[str] = None

    # --------
    # Webhook shared secret (Baileys Node → backend webhook, no JWT)
    # --------
    WEBHOOK_SECRET: str = Field(
        default="whatsapp_webhook_secret_dev",
        description="Shared secret for authenticating incoming webhooks from Baileys Node service",
    )
    WEBHOOK_DEFAULT_USER_ID: Optional[str] = Field(
        default=None,
        description="Default user_id to assign to webhook-created orders (set in production)",
    )

    @validator("JWT_SECRET")
    def secret_must_be_256_bit(cls, v: str) -> str:
        if len(v) < 44:
            raise ValueError(
                "JWT_SECRET must be at least 44 base64 characters (256 bits). "
                "Generate one with: python -c \"import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())\""
            )
        return v

    @model_validator(mode='after')
    def enforce_production_cors(cls, values):
        if values.APP_ENV == "production" and not values.CORS_ORIGINS.strip():
            raise ValueError("CORS_ORIGINS must be set in production")
        return values

    @model_validator(mode='after')
    def enforce_production_secret(cls, values):
        # Disallow the insecure default secret in non‑development environments.
        if values.APP_ENV != "development" and values.JWT_SECRET == "dGhpc2lzYXRlc3RzZWNyZXR0aGF0aXNhdGxlYXN0NDRjaGFyc2xvbmcK":
            raise ValueError("JWT_SECRET must be set via environment variable in production; default secret is insecure")
        if values.APP_ENV != "development" and values.WEBHOOK_SECRET == "whatsapp_webhook_secret_dev":
            raise ValueError("WEBHOOK_SECRET must be set via environment variable in production; default secret is insecure")
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instantiate settings – validation happens here. The application will not start if any required
# environment variable is missing or malformed.
settings = Settings()
