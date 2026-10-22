"""
Deep-Dive Search Reasoning Agent (MTIS Stage 4).
Input: Chosen thesis title and linked gap_id.
Output: Refined set of 5 to 10 targeted academic papers (re-runs Phase 2 search).
Enforces the mandatory D4 contract layer with schema verification, 
out-of-policy refusal, and 1-repair retry.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.schemas import DeepDiveResponse, Paper
from app.ai.contract import (
    execute_contract_with_retry,
    check_out_of_policy,
    check_user_quota,
    AIContractError,
)
from app.agents.openalex_client import search as openalex_search
from app.agents.utm_scraper import search_utm_repository
from app.config import settings

logger = logging.getLogger(__name__)


def _load_prompt_template() -> str:
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "deepdive_prompt.md",
        Path(__file__).resolve().parent.parent.parent / "prompts" / "deepdive_prompt.md",
        Path("prompts/deepdive_prompt.md"),
        Path("/app/prompts/deepdive_prompt.md"),
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read prompt from {p}: {e}")
    return "You are an academic literature retrieval specialist. Refine literature search for the title."


def execute_deepdive_search(
    chosen_title: str,
    gap_id: str,
    scope: str = "MY",
    user: Any = None,
    user_email: str = "anonymous",
) -> DeepDiveResponse:
    """
    Executes deep-dive literature refinement for the chosen thesis title.
    - Pre-call policy and quota verification.
    - Runs through D4 contract layer.
    - Yields between 5 and 10 targeted papers.
    - Retries ONCE on malformed reply; returns defined failure message if still invalid.
    """
    # 1. Pre-call checks
    if user:
        check_user_quota(user, stage="deepdive")
        user_email = getattr(user, "email", user_email)

    check_out_of_policy(chosen_title, user_email=user_email, stage="deepdive")

    raw_prompt = _load_prompt_template()
    title_gap_json = json.dumps({"chosen_title": chosen_title, "gap_id": gap_id}, indent=2)
    user_prompt = raw_prompt.replace("{{TITLE_AND_GAP_JSON}}", title_gap_json)
    system_prompt = (
        "You are an academic literature retrieval agent. "
        "Return between 5 and 10 targeted research papers for the chosen thesis title. "
        "Return ONLY strict valid JSON conforming to the DeepDiveResponse schema."
    )

    # 2. Custom Validator for D4 paper count constraints (5-10 papers)
    def validate_deepdive_integrity(resp: DeepDiveResponse):
        if not resp.papers or len(resp.papers) < 5 or len(resp.papers) > 10:
            raise ValueError(f"Deep-dive search must return between 5 and 10 papers (received {len(resp.papers) if resp.papers else 0}).")
        if not resp.chosen_title or resp.chosen_title != chosen_title:
            raise ValueError(f"Chosen title mismatch: received '{resp.chosen_title}', expected '{chosen_title}'.")
        if not resp.gap_id or resp.gap_id != gap_id:
            raise ValueError(f"Gap ID mismatch: received '{resp.gap_id}', expected '{gap_id}'.")

    # 3. Execute through contract layer
    return execute_contract_with_retry(
        stage="deepdive",
        stage_display="Stage 4 (Deep-Dive Search)",
        schema_cls=DeepDiveResponse,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        user_email=user_email,
        custom_validator=validate_deepdive_integrity,
    )
