"""
LLM Provider Adapter for MTIS.
Centralized provider interface supporting OpenAI and DeepSeek with automatic
provider fallback, DEMO_MODE fixtures, startup key verification, and JSONL logging.
"""
import os
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings, Settings
from app.ai.contract import log_ai_call

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


@dataclass
class ProviderConfig:
    provider: str  # "openai" | "deepseek" | "demo"
    model: str
    api_key: Optional[str] = None
    fallback_from: Optional[str] = None


def resolve_provider_config(
    current_settings: Optional[Settings] = None,
    tenant_id: Optional[str] = None,
) -> ProviderConfig:
    """
    Resolves the active LLM provider based on LLM_PROVIDER and available API keys.
    If tenant_id is provided, checks for a securely encrypted key in the database.
    If the chosen provider's key is missing, falls back to the other provider.
    If BOTH keys are missing and DEMO_MODE is false, raises RuntimeError.
    """
    s = current_settings or settings
    requested_provider = getattr(s, "LLM_PROVIDER", "deepseek") or "deepseek"
    requested_provider = str(requested_provider).lower()

    deepseek_key = getattr(s, "DEEPSEEK_API_KEY", None) or os.getenv("DEEPSEEK_API_KEY") or None
    openai_key = getattr(s, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY") or None

    # Check for tenant-specific AES-256 encrypted API key
    if tenant_id:
        try:
            from app.database import SessionLocal
            from app.models import Tenant
            from app.security import decrypt_api_key
            with SessionLocal() as db:
                t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
                if t and t.encrypted_api_key:
                    decrypted = decrypt_api_key(t.encrypted_api_key)
                    if decrypted:
                        t_prov = (t.llm_provider or "deepseek").lower()
                        if t_prov == "openai":
                            openai_key = decrypted
                            requested_provider = "openai"
                        else:
                            deepseek_key = decrypted
                            requested_provider = "deepseek"
        except Exception as exc:
            logger.warning(f"Could not load tenant-specific API key: {exc}")

    if deepseek_key:
        deepseek_key = deepseek_key.strip() or None
    if openai_key:
        openai_key = openai_key.strip() or None

    demo_mode = getattr(s, "DEMO_MODE", True)

    if requested_provider == "deepseek":
        if deepseek_key:
            return ProviderConfig(
                provider="deepseek",
                model=getattr(s, "LLM_MODEL", None) or "deepseek-chat",
                api_key=deepseek_key,
                fallback_from=None,
            )
        elif openai_key:
            logger.warning(
                "LLM_PROVIDER is configured as 'deepseek', but DEEPSEEK_API_KEY is missing. "
                "Falling back to OpenAI provider."
            )
            return ProviderConfig(
                provider="openai",
                model="gpt-4o-mini",
                api_key=openai_key,
                fallback_from="deepseek",
            )
        else:
            if demo_mode:
                return ProviderConfig(
                    provider="demo",
                    model="demo-fixtures",
                    api_key=None,
                    fallback_from=None,
                )
            raise RuntimeError(
                "Startup configuration error: DEMO_MODE is false, but both DEEPSEEK_API_KEY and OPENAI_API_KEY are missing. "
                "Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY in your environment (.env)."
            )

    elif requested_provider == "openai":
        if openai_key:
            return ProviderConfig(
                provider="openai",
                model=getattr(s, "LLM_MODEL", None) or "gpt-4o-mini",
                api_key=openai_key,
                fallback_from=None,
            )
        elif deepseek_key:
            logger.warning(
                "LLM_PROVIDER is configured as 'openai', but OPENAI_API_KEY is missing. "
                "Falling back to DeepSeek provider."
            )
            return ProviderConfig(
                provider="deepseek",
                model="deepseek-chat",
                api_key=deepseek_key,
                fallback_from="openai",
            )
        else:
            if demo_mode:
                return ProviderConfig(
                    provider="demo",
                    model="demo-fixtures",
                    api_key=None,
                    fallback_from=None,
                )
            raise RuntimeError(
                "Startup configuration error: DEMO_MODE is false, but both DEEPSEEK_API_KEY and OPENAI_API_KEY are missing. "
                "Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY in your environment (.env)."
            )

    else:
        # Fallback to deepseek logic if unrecognized
        if deepseek_key:
            return ProviderConfig(provider="deepseek", model="deepseek-chat", api_key=deepseek_key)
        elif openai_key:
            return ProviderConfig(provider="openai", model="gpt-4o-mini", api_key=openai_key, fallback_from=requested_provider)
        elif demo_mode:
            return ProviderConfig(provider="demo", model="demo-fixtures", api_key=None)
        raise RuntimeError(
            f"Unsupported LLM_PROVIDER '{requested_provider}' and missing credentials."
        )


def _load_fixture_for_schema(schema_name: str) -> Optional[Dict[str, Any]]:
    """Loads appropriate fixture file based on schema name."""
    s_lower = schema_name.lower()
    filename = None
    if "gap" in s_lower:
        filename = "gap_fixture.json"
    elif "title" in s_lower:
        filename = "title_fixture.json"
    elif "deepdive" in s_lower:
        filename = "deepdive_fixture.json"
    elif "plan" in s_lower:
        filename = "plan_fixture.json"

    if not filename:
        return None

    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "tests" / "fixtures" / filename,
        Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / filename,
        Path("tests/fixtures") / filename,
        Path("/app/tests/fixtures") / filename,
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading fixture {p}: {e}")
    return None


def complete(
    prompt: str,
    schema: Type[T],
    stage: str = "adapter",
    user: str = "anonymous",
    current_settings: Optional[Settings] = None,
    **kwargs,
) -> T:
    """
    Single unified adapter interface:
    complete(prompt: str, schema: type[BaseModel]) -> BaseModel

    Routes to OpenAI or DeepSeek based on LLM_PROVIDER with automatic fallback.
    Logs every invocation to logs/ai_calls.jsonl.
    """
    # 1. Resolve Provider and Key Configuration
    cfg = resolve_provider_config(current_settings)

    # 2. Check for global mock handler (test hook from provider.py)
    try:
        from app.ai.provider import _mock_handler
    except ImportError:
        _mock_handler = None

    if _mock_handler is not None:
        raw_content = _mock_handler(stage, [{"role": "user", "content": prompt}])
        log_ai_call(
            user=user,
            stage=stage,
            model="mock-provider",
            tokens=120,
            cost_myr=0.00,
            status="ok",
        )
        return schema.model_validate_json(raw_content)

    # 3. DEMO_MODE / No-Key Mode Fixture Execution
    if cfg.provider == "demo":
        fixture_data = _load_fixture_for_schema(schema.__name__)
        tokens = 250
        cost_myr = 0.00
        status = "no_key_mode"

        log_ai_call(
            user=user,
            stage=stage,
            model=cfg.model,
            tokens=tokens,
            cost_myr=cost_myr,
            status=status,
        )

        if fixture_data is not None:
            return schema.model_validate(fixture_data)
        
        # If no fixture file matched, attempt default instantiation
        try:
            return schema.model_validate({})
        except ValidationError:
            # Return minimal empty schema if possible
            return schema.model_validate_json("{}")

    # 4. Live Provider Execution (DeepSeek or OpenAI)
    base_url = "https://api.deepseek.com/v1" if cfg.provider == "deepseek" else "https://api.openai.com/v1"
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg.model,
        "messages": [
            {
                "role": "system",
                "content": "You are MTIS academic research assistant. Return valid JSON only, conforming strictly to the requested schema.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    call_status = "ok"
    if cfg.fallback_from:
        call_status = f"fallback_{cfg.provider}"

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            choice_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)
            total_toks = usage.get("total_tokens", prompt_toks + comp_toks)

            # Cost estimation in MYR (~4.65 MYR / USD)
            if cfg.provider == "deepseek":
                cost_usd = (prompt_toks * 0.00000014) + (comp_toks * 0.00000028)
            else:
                cost_usd = (prompt_toks * 0.00000015) + (comp_toks * 0.00000060)
            cost_myr = round(cost_usd * 4.65, 4)

            log_ai_call(
                user=user,
                stage=stage,
                model=cfg.model,
                tokens=total_toks,
                cost_myr=cost_myr,
                status=call_status,
            )

            return schema.model_validate_json(choice_content)

    except Exception as exc:
        logger.error(f"Live LLM call to {cfg.provider} ({cfg.model}) failed: {exc}")
        log_ai_call(
            user=user,
            stage=stage,
            model=cfg.model,
            tokens=0,
            cost_myr=0.00,
            status=f"error_{cfg.provider}",
        )
        raise exc


class LLMAdapter:
    """Class wrapper for complete() interface."""
    @staticmethod
    def complete(prompt: str, schema: Type[T], **kwargs) -> T:
        return complete(prompt=prompt, schema=schema, **kwargs)
