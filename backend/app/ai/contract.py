"""
MANDATORY AI CONTRACT LAYER (Rubric D4).
Enforces:
1. Pydantic schema validation for all agent outputs.
2. Malformed/truncated reply rejection with exactly ONE repair retry.
3. Defined user-facing failure message if still invalid:
   "The AI returned an invalid response. Your progress is saved — retry Stage X."
4. Out-of-policy refusal filter executed BEFORE any paid call (cost_myr: 0.00).
5. Rate limit / quota filter executed BEFORE any paid call (cost_myr: 0.00).
6. Structured JSONL logging to logs/ai_calls.jsonl.
"""
import os
import re
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Type, TypeVar, Optional, List, Dict, Any, Tuple, Callable
from pydantic import BaseModel, ValidationError


from app.schemas import (
    GapAnalysisResponse,
    TitleSuggestionsResponse,
    DeepDiveResponse,
    GapItem,
    TitleItem,
    Paper,
)
from app.ai.provider import call_llm_provider, ProviderResponse

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Paths for JSONL logging
REPO_LOGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
BACKEND_LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
AI_LOG_FILES = [
    REPO_LOGS_DIR / "ai_calls.jsonl",
    BACKEND_LOGS_DIR / "ai_calls.jsonl",
]


def _ensure_log_dirs():
    REPO_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    BACKEND_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_ai_call(
    user: str,
    stage: str,
    model: str,
    tokens: int,
    cost_myr: float,
    status: str,
):
    """
    Append-only log entry per AI call to logs/ai_calls.jsonl per Rubric D4/D5.
    Statuses include: ok, retry, rejected_malformed, refused_policy, refused_quota, no_key_mode.
    """
    _ensure_log_dirs()
    event = {
        "user": user or "anonymous",
        "stage": stage,
        "model": model,
        "tokens": tokens,
        "cost_myr": round(float(cost_myr), 4),
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    line = json.dumps(event) + "\n"
    for log_path in AI_LOG_FILES:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            logger.error(f"Failed writing to {log_path}: {e}")


# Custom Exceptions with Defined User Messages
class AIContractError(Exception):
    def __init__(self, stage_display: str, message: str, detail: Optional[Any] = None):
        super().__init__(message)
        self.stage_display = stage_display
        self.user_message = message
        self.detail = detail


class AIPolicyRefusalError(Exception):
    def __init__(self, message: str = "Refusal: Your request is outside the scope of MTIS academic thesis research. Please provide an academic thesis topic."):
        super().__init__(message)
        self.user_message = message


class AIQuotaExceededError(Exception):
    def __init__(self, message: str = "Daily generation quota exceeded. Please upgrade your plan or wait for the quota reset."):
        super().__init__(message)
        self.user_message = message


# Policy and Safety Filter
FORBIDDEN_TOPIC_PATTERNS = [
    r"\b(bomb|weapon|explosive|ammunition)\b",
    r"\b(hack|exploit|malware|ddos|trojan|ransomware|keylogger)\b",
    r"\b(recipe|cookie|chocolate chip|bake a cake)\b",
    r"\b(poem|love song|creative story|fairy tale)\b",
    r"\b(bypass safety|ignore previous instructions|jailbreak|DAN mode)\b",
    r"\b(lottery|casino|gambling|porn|nsfw)\b",
]


def check_out_of_policy(text: str, user_email: str, stage: str):
    """
    Filters non-research or abusive content BEFORE any paid API call.
    Logs cost_myr=0.00 and status='refused_policy'.
    """
    lower = text.lower()
    for pattern in FORBIDDEN_TOPIC_PATTERNS:
        if re.search(pattern, lower):
            log_ai_call(
                user=user_email,
                stage=stage,
                model="policy-filter",
                tokens=0,
                cost_myr=0.00,
                status="refused_policy",
            )
            raise AIPolicyRefusalError()


def check_user_quota(user: Any, stage: str):
    """
    Enforces per-user daily quota BEFORE any paid API call.
    At limit, logs cost_myr=0.00 and status='refused_quota'.
    """
    if user is not None and hasattr(user, "quota_remaining"):
        if user.quota_remaining <= 0:
            log_ai_call(
                user=getattr(user, "email", "anonymous"),
                stage=stage,
                model="quota-gate",
                tokens=0,
                cost_myr=0.00,
                status="refused_quota",
            )
            raise AIQuotaExceededError()


def _extract_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """Extracts JSON substring, stripping markdown fences if present."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def execute_contract_with_retry(
    stage: str,
    stage_display: str,
    schema_cls: Type[T],
    system_prompt: str,
    user_prompt: str,
    user_email: str = "anonymous",
    custom_validator: Optional[Callable[[T], None]] = None,
) -> T:
    """
    Executes an LLM call through the strict D4 contract:
    1. Initial LLM Call.
    2. Validate against Pydantic schema + custom validator.
    3. If invalid/malformed:
       - Log status 'retry'.
       - Send repair prompt to LLM.
       - If repair succeeds: log 'ok' and return.
       - If repair STILL fails:
         - Log status 'rejected_malformed'.
         - Raise AIContractError with defined user message:
           'The AI returned an invalid response. Your progress is saved — retry Stage X.'
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Attempt 1
    resp1 = call_llm_provider(stage=stage, messages=messages, user_email=user_email)

    try:
        data1 = _extract_and_parse_json(resp1.content)
        validated1 = schema_cls.model_validate(data1)
        if custom_validator:
            custom_validator(validated1)

        # Success on first attempt
        final_status = resp1.status if resp1.status == "no_key_mode" else "ok"
        log_ai_call(
            user=user_email,
            stage=stage,
            model=resp1.model,
            tokens=resp1.tokens,
            cost_myr=resp1.cost_myr,
            status=final_status,
        )
        return validated1

    except Exception as first_err:
        logger.warning(f"Contract failure on Attempt 1 for stage '{stage}': {first_err}")
        # Log retry event
        log_ai_call(
            user=user_email,
            stage=stage,
            model=resp1.model,
            tokens=resp1.tokens,
            cost_myr=resp1.cost_myr,
            status="retry",
        )

        # Attempt 2: Repair prompt
        repair_messages = list(messages)
        repair_messages.append({"role": "assistant", "content": resp1.content})
        repair_messages.append({
            "role": "user",
            "content": (
                f"Your previous response was rejected due to schema error: {first_err}.\n"
                "Please repair your output and return strictly valid JSON matching the required schema. "
                "Do not include any conversational filler, only raw JSON."
            )
        })

        resp2 = call_llm_provider(stage=stage, messages=repair_messages, user_email=user_email)

        try:
            data2 = _extract_and_parse_json(resp2.content)
            validated2 = schema_cls.model_validate(data2)
            if custom_validator:
                custom_validator(validated2)

            # Success on repair
            final_status2 = resp2.status if resp2.status == "no_key_mode" else "ok"
            log_ai_call(
                user=user_email,
                stage=stage,
                model=resp2.model,
                tokens=resp2.tokens,
                cost_myr=resp2.cost_myr,
                status=final_status2,
            )
            return validated2

        except Exception as second_err:
            logger.error(f"Contract failure on Repair Attempt 2 for stage '{stage}': {second_err}")
            # Log final rejection
            log_ai_call(
                user=user_email,
                stage=stage,
                model=resp2.model,
                tokens=resp2.tokens,
                cost_myr=resp2.cost_myr,
                status="rejected_malformed",
            )
            # Defined user-facing failure message per Rubric D4
            raise AIContractError(
                stage_display=stage_display,
                message=f"The AI returned an invalid response. Your progress is saved — retry {stage_display}.",
                detail={"first_error": str(first_err), "second_error": str(second_err)}
            )
