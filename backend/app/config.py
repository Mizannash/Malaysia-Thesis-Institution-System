"""Configuration settings for MTIS Backend.
All API keys and provider configurations are loaded strictly from the environment.
No hardcoded API keys exist in code.
"""
import os
import secrets
from enum import Enum
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class LLMProviderEnum(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"


class Settings(BaseSettings):
    APP_NAME: str = "Malaysian Thesis Institution System (MTIS)"
    APP_ENV: str = "development"
    DEMO_MODE: bool = True
    APP_SECRET: str = os.getenv("APP_SECRET", secrets.token_urlsafe(32))

    # ── LLM Settings (loaded strictly from environment) ──
    LLM_PROVIDER: Literal["openai", "deepseek"] = "deepseek"
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    # ── Academic Coach Chat Limits (separate from generation quota) ──
    CHAT_DAILY_LIMIT: int = 30
    CHAT_PER_MINUTE_LIMIT: int = 10

    # ── Production Safety ──
    # Total paid AI calls per Malaysia day across all users (0 = no cap)
    AI_DAILY_GLOBAL_LIMIT: int = 300
    # Comma-separated browser origins allowed by CORS (e.g. https://your-site.netlify.app)
    ALLOWED_ORIGINS: str = "*"

    # ── Account → University Mapping ──
    # Comma-separated "domain:tenant_id" pairs; other emails join INDEPENDENT_TENANT_ID
    TENANT_EMAIL_DOMAINS: str = ""  # optional override; the institution list lives in the database

    # ── Data Source Settings ──
    # Polite-pool email for live OpenAlex queries (free, NOT a secret)
    OPENALEX_EMAIL: Optional[str] = None
    # Optional SerpApi key for Google Scholar (default None / disabled)
    SERPAPI_KEY: Optional[str] = None

    # ── Database Settings ──
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis"

    # ── Supabase Settings (Optional in DEMO_MODE) ──
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None

    # ── Redis Settings ──
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return (self.APP_ENV or "").lower() == "production"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in (self.ALLOWED_ORIGINS or "").split(",") if o.strip()]

    @property
    def tenant_email_domains(self) -> dict[str, str]:
        pairs = {}
        for item in (self.TENANT_EMAIL_DOMAINS or "").split(","):
            domain, _, tenant_id = item.strip().partition(":")
            if domain.strip() and tenant_id.strip():
                pairs[domain.strip().lower()] = tenant_id.strip()
        return pairs

    @model_validator(mode="after")
    def validate_configuration(self) -> "Settings":
        # 1. Resolve default model based on provider if not explicitly provided
        if not self.LLM_MODEL:
            if self.LLM_PROVIDER == "openai":
                self.LLM_MODEL = "gpt-4o-mini"
            else:
                self.LLM_MODEL = "deepseek-chat"

        # 2. Key validation when DEMO_MODE is False
        if not self.DEMO_MODE:
            has_deepseek = bool(self.DEEPSEEK_API_KEY and self.DEEPSEEK_API_KEY.strip())
            has_openai = bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())
            if not has_deepseek and not has_openai:
                raise ValueError(
                    "Startup configuration error: DEMO_MODE is false, but both DEEPSEEK_API_KEY and OPENAI_API_KEY are missing. "
                    "Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY in your environment (.env)."
                )

        return self


def validate_startup_config(s: Settings) -> None:
    """
    Validate startup requirements for LLM keys when DEMO_MODE is False.
    Raises RuntimeError naming the missing environment variables if invalid.
    """
    if not s.DEMO_MODE:
        has_deepseek = bool(s.DEEPSEEK_API_KEY and s.DEEPSEEK_API_KEY.strip())
        has_openai = bool(s.OPENAI_API_KEY and s.OPENAI_API_KEY.strip())
        if not has_deepseek and not has_openai:
            raise RuntimeError(
                "Startup configuration error: DEMO_MODE is false, but both DEEPSEEK_API_KEY and OPENAI_API_KEY are missing. "
                "Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY in your environment (.env)."
            )


try:
    settings = Settings()
except Exception:
    # Production must never silently fall back to demo mode (it would re-enable demo login)
    if os.getenv("APP_ENV", "").lower() == "production":
        raise
    # If loading with missing keys under DEMO_MODE=False, instantiate a fallback
    # so module import succeeds; validation failure will be explicitly caught at startup.
    settings = Settings(DEMO_MODE=True)
