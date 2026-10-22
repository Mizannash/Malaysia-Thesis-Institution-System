"""
Plan Generation & Iterative Refinement Reasoning Agent (MTIS Stage 5).
Input: Full project state (Search results, Gap list, Title, Deep-Dive papers).
Output: Structured research execution plan with objectives, key milestones, resources, and timeline.
Enforces the mandatory D4 contract layer with schema verification, 
out-of-policy refusal, and 1-repair retry.
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Union

from app.schemas import StructuredPlan
from app.ai.contract import (
    execute_contract_with_retry,
    check_out_of_policy,
    check_user_quota,
    AIContractError,
)

logger = logging.getLogger(__name__)


def _load_prompt_template(filename: str) -> str:
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "prompts" / filename,
        Path(__file__).resolve().parent.parent.parent / "prompts" / filename,
        Path("prompts") / filename,
        Path("/app/prompts") / filename,
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read prompt from {p}: {e}")
    return "You are an expert research planner. Generate a structured thesis plan in strict JSON."


def generate_research_plan(
    project_state: Dict[str, Any],
    custom_instructions: Optional[str] = None,
    user: Any = None,
    user_email: str = "anonymous",
) -> StructuredPlan:
    """
    Generates a structured postgraduate thesis execution plan from full project context.
    - Input: Search results, Gap list, Title, Deep-Dive papers.
    - Pre-call policy & quota enforcement.
    - Validates objectives, milestones, resources, and timeline phases.
    - Retries ONCE on malformed reply; returns defined failure message if still invalid.
    """
    if user:
        check_user_quota(user, stage="plan")
        user_email = getattr(user, "email", user_email)

    title = project_state.get("chosen_title") or project_state.get("title") or "Malaysian Academic Research Thesis"
    check_out_of_policy(f"{title} {custom_instructions or ''}", user_email=user_email, stage="plan")

    gap_id = project_state.get("chosen_gap_id")
    if not gap_id and project_state.get("gaps"):
        gap_id = project_state["gaps"][0].get("gap_id")

    raw_prompt = _load_prompt_template("plan_prompt.md")
    context_str = json.dumps(project_state, indent=2, default=str)
    user_prompt = (
        raw_prompt
        .replace("{{PROJECT_CONTEXT_JSON}}", context_str)
        .replace("{{TITLE}}", title)
        .replace("{{GAP_ID}}", gap_id or "GAP-1")
    )
    if custom_instructions:
        user_prompt += f"\n\nAdditional Supervisor Instructions:\n{custom_instructions}"

    system_prompt = (
        "You are an academic postgraduate thesis planning consultant for Malaysian HEIs. "
        "Formulate a structured research execution plan adhering strictly to the provided input literature and gap. "
        "Return ONLY strict valid JSON conforming to the StructuredPlan schema."
    )

    def validate_plan_integrity(plan: StructuredPlan):
        if not plan.objectives or len(plan.objectives) < 2:
            raise ValueError(f"Plan must contain at least 2 research objectives (received {len(plan.objectives)}).")
        if not plan.key_milestones or len(plan.key_milestones) < 3:
            raise ValueError(f"Plan must define at least 3 key milestones (received {len(plan.key_milestones)}).")
        if not plan.timeline or len(plan.timeline) < 2:
            raise ValueError(f"Plan must contain at least 2 timeline phases (received {len(plan.timeline)}).")
        if not plan.methodology_summary or len(plan.methodology_summary.strip()) < 20:
            raise ValueError("Methodology summary is too short or missing.")

    generated_plan = execute_contract_with_retry(
        stage="plan",
        stage_display="Stage 5 (Objectives & Methodology Plan)",
        schema_cls=StructuredPlan,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        user_email=user_email,
        custom_validator=validate_plan_integrity,
    )

    # Assign unique plan_id
    generated_plan.plan_id = f"plan-{uuid.uuid4().hex[:8]}"

    return generated_plan


def refine_research_plan(
    existing_plan: Union[StructuredPlan, Dict[str, Any]],
    user_prompt: str,
    user: Any = None,
    user_email: str = "anonymous",
) -> StructuredPlan:
    """
    Applies iterative user/supervisor feedback to refine an existing research plan.
    - Pre-call policy and quota check.
    - Refines objectives, timeline, or methodology based on feedback.
    - Increments plan_version.
    """
    if user:
        check_user_quota(user, stage="refine")
        user_email = getattr(user, "email", user_email)

    check_out_of_policy(user_prompt, user_email=user_email, stage="refine")

    if isinstance(existing_plan, StructuredPlan):
        plan_dict = existing_plan.model_dump()
        current_version = existing_plan.version
    else:
        plan_dict = dict(existing_plan)
        current_version = plan_dict.get("version", 1)

    next_version = current_version + 1
    raw_prompt = _load_prompt_template("refine_prompt.md")
    user_prompt_formatted = (
        raw_prompt
        .replace("{{VERSION}}", str(current_version))
        .replace("{{EXISTING_PLAN_JSON}}", json.dumps(plan_dict, indent=2))
        .replace("{{USER_FEEDBACK}}", user_prompt)
        .replace("{{NEXT_VERSION}}", str(next_version))
    )

    system_prompt = (
        "You are an academic thesis planning consultant. "
        "Refine the provided thesis plan based on user feedback. "
        "Increment the version number and output ONLY valid JSON conforming to the StructuredPlan schema."
    )

    def validate_refined_plan(plan: StructuredPlan):
        if not plan.objectives or len(plan.objectives) < 2:
            raise ValueError("Refined plan must retain at least 2 research objectives.")
        if not plan.key_milestones or len(plan.key_milestones) < 3:
            raise ValueError("Refined plan must retain at least 3 milestones.")
        # Ensure version is updated
        if plan.version <= current_version:
            plan.version = next_version

    refined_plan = execute_contract_with_retry(
        stage="refine",
        stage_display="Stage 5 Plan Refinement",
        schema_cls=StructuredPlan,
        system_prompt=system_prompt,
        user_prompt=user_prompt_formatted,
        user_email=user_email,
        custom_validator=validate_refined_plan,
    )

    # Ensure plan_id is preserved from existing plan
    if plan_dict.get("plan_id"):
        refined_plan.plan_id = plan_dict["plan_id"]
    refined_plan.version = next_version

    return refined_plan
