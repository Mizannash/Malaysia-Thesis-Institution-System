"""
Title Suggestions Reasoning Agent (MTIS Stage 3).
Input: Research gap data (dict or GapItem), language preference ('EN' | 'BM').
Output: 2 to 5 defended thesis titles (tajuk kajian) linked to the gap ID.
Enforces the mandatory D4 contract layer with schema verification, 
out-of-policy refusal, and 1-repair retry.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional

from app.schemas import TitleSuggestionsResponse, GapItem, TitleItem
from app.ai.contract import (
    execute_contract_with_retry,
    check_out_of_policy,
    check_user_quota,
    AIContractError,
)

logger = logging.getLogger(__name__)


def _load_prompt_template() -> str:
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "title_prompt.md",
        Path(__file__).resolve().parent.parent.parent / "prompts" / "title_prompt.md",
        Path("prompts/title_prompt.md"),
        Path("/app/prompts/title_prompt.md"),
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read prompt from {p}: {e}")
    return "You are an academic thesis title advisor. Generate 2 to 5 thesis titles linking to the gap in strict JSON."


def generate_thesis_titles(
    gap_data: Union[GapItem, Dict[str, Any]],
    language: str = "EN",
    user: Any = None,
    user_email: str = "anonymous",
) -> TitleSuggestionsResponse:
    """
    Generates 2 to 5 defensible thesis titles based on the specified gap.
    - Filters out-of-policy text BEFORE paid calls.
    - Checks quota BEFORE paid calls.
    - Validates 2 <= count <= 5 and links each title to gap_id.
    - Retries ONCE on malformed reply; returns defined failure message if still invalid.
    """
    # 1. Pre-call checks
    if user:
        check_user_quota(user, stage="title")
        user_email = getattr(user, "email", user_email)

    if isinstance(gap_data, GapItem):
        gap_dict = gap_data.model_dump()
    else:
        gap_dict = dict(gap_data)

    gap_id = gap_dict.get("gap_id", "GAP-1")
    description = gap_dict.get("description", "")

    # Safety check on gap description
    check_out_of_policy(description, user_email=user_email, stage="title")

    lang_code = language.upper() if language else "EN"
    if lang_code not in ("EN", "BM"):
        lang_code = "EN"

    raw_prompt = _load_prompt_template()
    user_prompt = (
        raw_prompt
        .replace("{{GAP_JSON}}", json.dumps(gap_dict, indent=2))
        .replace("{{LANGUAGE}}", lang_code)
    )
    system_prompt = (
        f"You are an academic title advisor for Malaysian universities. "
        f"Generate between 2 and 5 specific thesis titles in {lang_code} linking back to {gap_id}. "
        "Return ONLY strict valid JSON conforming to the schema."
    )

    # 2. Custom Validator for D4 title constraints
    def validate_titles_integrity(resp: TitleSuggestionsResponse):
        if not resp.titles or len(resp.titles) < 2 or len(resp.titles) > 5:
            raise ValueError(f"Title suggestions must contain between 2 and 5 titles (received {len(resp.titles)}).")
        for item in resp.titles:
            if not item.title or len(item.title.strip()) < 10:
                raise ValueError("Thesis title is too short or empty.")
            if not item.gap_id or item.gap_id != gap_id:
                raise ValueError(f"Title '{item.title}' has invalid gap_id '{item.gap_id}'. Expected '{gap_id}'.")
            if item.language not in ("EN", "BM"):
                raise ValueError(f"Invalid language '{item.language}'. Must be EN or BM.")

    # 3. Execute through contract layer
    return execute_contract_with_retry(
        stage="title",
        stage_display="Stage 3 (Title Suggestions)",
        schema_cls=TitleSuggestionsResponse,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        user_email=user_email,
        custom_validator=validate_titles_integrity,
    )
