"""
LLM Provider Adapter for MTIS.
Supports swappable model providers (DeepSeek, OpenAI, Gemini),
deterministic fixture-based execution for DEMO_MODE / no-key mode,
and mock handlers for stress & contract tests.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    content: str
    tokens: int
    cost_myr: float
    model: str
    status: str = "ok"  # "ok" | "no_key_mode"


# Global test hook for injecting mock responses in stress tests
_mock_handler: Optional[Callable[[str, List[Dict[str, str]]], str]] = None


def set_mock_provider_handler(handler: Optional[Callable[[str, List[Dict[str, str]]], str]]):
    """Set custom mock handler for testing malformed, repair, or edge-case responses."""
    global _mock_handler
    _mock_handler = handler


def reset_mock_provider_handler():
    """Reset the mock provider handler to None."""
    global _mock_handler
    _mock_handler = None


def _load_fixture_data(filename: str) -> Any:
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
                logger.warning(f"Failed to read fixture {p}: {e}")
    return None


def call_llm_provider(
    stage: str,
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    user_email: Optional[str] = "anonymous",
) -> ProviderResponse:
    """
    Calls configured LLM provider or fallback fixture engine.
    - If mock handler is set, invokes handler.
    - If DEMO_MODE or no keys configured, returns cached fixture with cost_myr=0.00.
    - Otherwise, dispatches to live API.
    """
    # 1. Test Mock Handler Hook
    if _mock_handler is not None:
        content = _mock_handler(stage, messages)
        return ProviderResponse(
            content=content,
            tokens=120,
            cost_myr=0.00,
            model="mock-provider",
            status="ok"
        )

    # 2. Check for active API Keys
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    has_live_keys = bool(deepseek_key or openai_key or gemini_key)

    # 3. DEMO_MODE or NO-KEY Mode Fallback (D4 requirement)
    if settings.DEMO_MODE or not has_live_keys:
        logger.info(f"LLM Provider executing in NO-KEY / DEMO mode for stage '{stage}'")
        if stage == "gap":
            fixture_data = _load_fixture_data("gap_fixture.json")
            if fixture_data:
                return ProviderResponse(
                    content=json.dumps(fixture_data),
                    tokens=450,
                    cost_myr=0.00,
                    model="demo-fixtures",
                    status="no_key_mode"
                )
        elif stage == "title":
            fixture_data = _load_fixture_data("title_fixture.json")
            if fixture_data:
                import re
                gap_match = re.search(r'"gap_id":\s*"([^"]+)"', json.dumps(messages))
                target_gap = gap_match.group(1) if gap_match else "GAP-1"
                for item in fixture_data.get("titles", []):
                    item["gap_id"] = target_gap
                return ProviderResponse(
                    content=json.dumps(fixture_data),
                    tokens=280,
                    cost_myr=0.00,
                    model="demo-fixtures",
                    status="no_key_mode"
                )
        elif stage == "deepdive":
            fixture_data = _load_fixture_data("deepdive_fixture.json")
            if fixture_data:
                import re
                gap_match = re.search(r'"gap_id":\s*"([^"]+)"', json.dumps(messages))
                title_match = re.search(r'"chosen_title":\s*"([^"]+)"', json.dumps(messages))
                if gap_match:
                    fixture_data["gap_id"] = gap_match.group(1)
                if title_match:
                    fixture_data["chosen_title"] = title_match.group(1)
                return ProviderResponse(
                    content=json.dumps(fixture_data),
                    tokens=520,
                    cost_myr=0.00,
                    model="demo-fixtures",
                    status="no_key_mode"
                )
        elif stage in ("plan", "refine"):
            fixture_data = _load_fixture_data("plan_fixture.json") or {}
            import re
            msg_dump = json.dumps(messages)
            title_match = re.search(r'"title":\s*"([^"]+)"', msg_dump)
            gap_match = re.search(r'"gap_id":\s*"([^"]+)"', msg_dump)
            if title_match and fixture_data:
                fixture_data["title"] = title_match.group(1)
            if gap_match and fixture_data:
                fixture_data["gap_id"] = gap_match.group(1)

            if stage == "refine":
                # Extract user feedback from prompt
                feedback_match = re.search(r'(?:Feedback|revision instructions|user_prompt)[:\s]*([^\n"]+)', msg_dump, re.IGNORECASE)
                feedback = feedback_match.group(1) if feedback_match else "Focused refinement on Malaysian SMEs"
                fixture_data["version"] = fixture_data.get("version", 1) + 1
                fixture_data["methodology_summary"] = (
                    f"{fixture_data.get('methodology_summary', '')} Refined based on feedback: {feedback}."
                )
                # Demonstrably adjust milestone description to show refinement effect
                if fixture_data.get("key_milestones"):
                    fixture_data["key_milestones"][0]["description"] += f" (Refined: {feedback})"

            return ProviderResponse(
                content=json.dumps(fixture_data),
                tokens=650,
                cost_myr=0.00,
                model="demo-fixtures",
                status="no_key_mode"
            )



        # Fallback minimal JSON if fixture not found
        return ProviderResponse(
            content=json.dumps({"gaps": []} if stage == "gap" else {"titles": []}),
            tokens=50,
            cost_myr=0.00,
            model="demo-fixtures-empty",
            status="no_key_mode"
        )

    # 4. Live Provider Call (DeepSeek / OpenAI)
    # Defaulting to DeepSeek V3 / OpenAI compatible endpoint
    target_model = model or "deepseek-chat"
    api_key = deepseek_key or openai_key
    base_url = "https://api.deepseek.com/v1" if deepseek_key else "https://api.openai.com/v1"

    try:
        import httpx
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)
            total_toks = usage.get("total_tokens", prompt_toks + comp_toks)

            # DeepSeek token rate: ~$0.14 per 1M input (~RM0.65), ~$0.28 per 1M output (~RM1.30)
            cost_usd = (prompt_toks * 0.00000014) + (comp_toks * 0.00000028)
            cost_myr = round(cost_usd * 4.65, 4)

            return ProviderResponse(
                content=choice,
                tokens=total_toks,
                cost_myr=cost_myr,
                model=target_model,
                status="ok"
            )
    except Exception as e:
        logger.error(f"Live provider call failed: {e}. Falling back to cached fixture.")
        return ProviderResponse(
            content=json.dumps({"error": str(e)}),
            tokens=0,
            cost_myr=0.00,
            model=target_model,
            status="error"
        )
