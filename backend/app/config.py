"""Configuration settings for MTIS Backend."""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


import secrets

class Settings(BaseSettings):
    APP_NAME: str = "Malaysian Thesis Institution System (MTIS)"
    APP_ENV: str = "development"
    DEMO_MODE: bool = True
    APP_SECRET: str = os.getenv("APP_SECRET", secrets.token_urlsafe(32))

    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis"

    # Supabase Settings (Optional in DEMO_MODE)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None

    # OpenAlex Settings (Polite Pool)
    OPENALEX_EMAIL: Optional[str] = None

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# If credentials are not supplied, ensure DEMO_MODE is active
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    settings.DEMO_MODE = True
