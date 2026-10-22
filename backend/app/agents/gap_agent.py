"""
Gap Analysis Reasoning Agent (MTIS Stage 2).
Input: Structured list of papers/abstracts.
Output: JSON array of research gaps, each citing supporting paper IDs.
Enforces the mandatory D4 contract layer with schema verification, 
out-of-policy refusal, and 1-repair retry.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Union

from app.schemas import GapAnalysisResponse, Paper, GapItem
from app.ai.contract import (
    execute_contract_with_retry,
    check_out_of_policy,
    check_user_quota,
    AIContractError,
)

logger = logging.getLogger(__name__)


def _load_prompt_template() -> str:
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "gap_prompt.md",
        Path(__file__).resolve().parent.parent.parent / "prompts" / "gap_prompt.md",
        Path("prompts/gap_prompt.md"),
        Path("/app/prompts/gap_prompt.md"),
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read prompt from {p}: {e}")
    return "You are an academic thesis advisor. Identify research gaps from the provided papers in strict JSON."


def analyze_research_gaps(
    papers: List[Union[Paper, Dict[str, Any]]],
    user: Any = None,
    user_email: str = "anonymous",
) -> GapAnalysisResponse:
    """
    Analyzes paper abstracts and generates synthesized research gaps with supporting citations.
    - Filters out-of-policy text BEFORE paid calls.
    - Checks quota BEFORE paid calls.
    - Validates citations link to actual input paper IDs.
    - Retries ONCE on malformed reply; returns defined failure message if still invalid.
    """
    # 1. Pre-call checks
    if user:
        check_user_quota(user, stage="gap")
        user_email = getattr(user, "email", user_email)

    # Convert papers to indexed structure
    formatted_papers = []
    valid_ids = set()

    for idx, p in enumerate(papers, start=1):
        if isinstance(p, Paper):
            p_dict = p.model_dump()
        else:
            p_dict = dict(p)

        paper_id = p_dict.get("paper_id") or f"P{idx}"
        valid_ids.add(paper_id)

        # Policy safety check on title/abstract text
        title_text = p_dict.get("title", "")
        abstract_text = p_dict.get("abstract", "")
        check_out_of_policy(f"{title_text} {abstract_text}", user_email=user_email, stage="gap")

        formatted_papers.append({
            "paper_id": paper_id,
            "title": title_text,
            "authors": p_dict.get("authors", []),
            "year": p_dict.get("year"),
            "abstract": abstract_text,
            "source": p_dict.get("source", "openalex"),
        })

    # Prepare prompt
    raw_prompt = _load_prompt_template()
    papers_json_str = json.dumps(formatted_papers, indent=2)
    user_prompt = raw_prompt.replace("{{PAPERS_JSON}}", papers_json_str)
    system_prompt = (
        "You are an academic research advisor specializing in Malaysian HEIs. "
        "Analyze the provided abstracts and output genuine research gaps citing valid Paper IDs. "
        "Return ONLY strict valid JSON conforming to the schema."
    )

    # 2. Custom Validator for D4 citation integrity
    def validate_gaps_integrity(resp: GapAnalysisResponse):
        if not resp.gaps or len(resp.gaps) < 1:
            raise ValueError("Gap analysis must yield at least one research gap.")
        for gap in resp.gaps:
            if not gap.description or len(gap.description.strip()) < 10:
                raise ValueError(f"Gap description for {gap.gap_id} is too short or empty.")
            if not gap.supporting_paper_ids or len(gap.supporting_paper_ids) < 1:
                raise ValueError(f"Gap {gap.gap_id} must cite at least one supporting paper ID.")
            # Check citation validity against provided papers
            for pid in gap.supporting_paper_ids:
                if pid not in valid_ids:
                    raise ValueError(f"Gap {gap.gap_id} cited paper ID '{pid}', which does not exist in the input papers list.")

    # 3. Execute through contract layer
    return execute_contract_with_retry(
        stage="gap",
        stage_display="Stage 2 (Gap Analysis)",
        schema_cls=GapAnalysisResponse,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        user_email=user_email,
        custom_validator=validate_gaps_integrity,
    )
