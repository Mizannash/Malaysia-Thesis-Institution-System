"""
Pipeline Router for Reasoning Agents (Stage 2 Gap -> Stage 3 Title -> Stage 4 Deep-Dive).
Enforces:
1. Immediate database state persistence into projects.state_json (Rubric D3).
2. 'Last saved: stage X, <timestamp>' metadata tracking.
3. Multi-tenant isolation and per-user daily quota decrement.
4. Clean failure handling via AI contract exceptions (zero partial corruption).
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified


from app.database import get_db, set_tenant_context
from app.models import Project, User
from app.auth import get_current_user
from app.schemas import (
    ProjectResponse,
    GapAnalysisRequest,
    GapAnalysisResponse,
    TitleSuggestionsRequest,
    TitleSuggestionsResponse,
    DeepDiveRequest,
    DeepDiveResponse,
    GapItem,
    TitleItem,
    Paper,
)
from app.agents.gap_agent import analyze_research_gaps
from app.agents.title_agent import generate_thesis_titles
from app.agents.deepdive_agent import execute_deepdive_search
from app.ai.contract import (
    AIContractError,
    AIPolicyRefusalError,
    AIQuotaExceededError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pipeline & AI Agents"])


def _get_isolated_project(project_id: str, current_user: User, db: Session) -> Project:
    """Retrieves project asserting multi-tenant isolation."""
    set_tenant_context(db, current_user.tenant_id)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Cross-tenant data access is strictly prohibited.",
        )
    if current_user.role == "student" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You may only view or update your own projects.",
        )
    return project


# ---------------------------------------------------------
# STAGE 2: GAP ANALYSIS
# ---------------------------------------------------------
@router.post("/projects/{project_id}/stage/gap", response_model=ProjectResponse)
@router.post("/api/projects/{project_id}/stage/gap", response_model=ProjectResponse)
def run_stage_gap(
    project_id: str,
    req: Optional[GapAnalysisRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes Stage 2 Gap Analysis on project literature.
    Writes result immediately to projects.state_json and updates last_saved metadata.
    """
    project = _get_isolated_project(project_id, current_user, db)

    # 1. Resolve papers to analyze
    papers_to_analyze = []
    if req and req.papers:
        papers_to_analyze = req.papers
    elif "papers" in project.state_json and project.state_json["papers"]:
        papers_to_analyze = [Paper(**p) for p in project.state_json["papers"]]
    else:
        # Load sample papers from fixtures if none present
        from app.ai.provider import _load_fixture_data
        sample_data = _load_fixture_data("sample_abstracts.json") or []
        papers_to_analyze = [Paper(**p) for p in sample_data]
        project.state_json["papers"] = [p.model_dump() for p in papers_to_analyze]

    # 2. Execute Gap Agent through contract layer
    try:
        gap_resp = analyze_research_gaps(
            papers=papers_to_analyze,
            user=current_user,
            user_email=current_user.email,
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )

    # 3. State Persistence (D3): Write immediately to DB
    now_iso = datetime.now(timezone.utc).isoformat()
    new_state = dict(project.state_json or {})
    new_state["gaps"] = [g.model_dump() for g in gap_resp.gaps]
    new_state["last_saved_stage"] = "Stage 2 (Gap Analysis)"
    new_state["last_saved_at"] = now_iso
    project.state_json = new_state
    project.stage = "gap"
    flag_modified(project, "state_json")

    # Decrement quota
    current_user.quota_remaining = max(0, current_user.quota_remaining - 1)

    db.commit()
    db.refresh(project)
    return project



# ---------------------------------------------------------
# STAGE 3: TITLE SUGGESTIONS
# ---------------------------------------------------------
@router.post("/projects/{project_id}/stage/title", response_model=ProjectResponse)
@router.post("/api/projects/{project_id}/stage/title", response_model=ProjectResponse)
def run_stage_title(
    project_id: str,
    req: TitleSuggestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes Stage 3 Title Suggestions for a specific research gap.
    Writes result immediately to projects.state_json.
    """
    project = _get_isolated_project(project_id, current_user, db)

    # 1. Resolve gap data
    target_gap: Optional[Dict[str, Any]] = None
    if req.gap:
        target_gap = req.gap.model_dump()
    elif req.gap_id:
        existing_gaps = project.state_json.get("gaps", [])
        for g in existing_gaps:
            if g.get("gap_id") == req.gap_id:
                target_gap = g
                break
    
    if not target_gap:
        existing_gaps = project.state_json.get("gaps", [])
        if existing_gaps:
            target_gap = existing_gaps[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "NO_GAP_FOUND", "message": "No research gap found. Please complete Stage 2 first."}
            )

    # 2. Execute Title Agent through contract layer
    try:
        title_resp = generate_thesis_titles(
            gap_data=target_gap,
            language=req.language or "EN",
            user=current_user,
            user_email=current_user.email,
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )

    # 3. State Persistence (D3): Write immediately to DB
    now_iso = datetime.now(timezone.utc).isoformat()
    new_state = dict(project.state_json or {})
    new_state["titles"] = [t.model_dump() for t in title_resp.titles]
    new_state["chosen_gap_id"] = target_gap.get("gap_id")
    new_state["last_saved_stage"] = "Stage 3 (Title Suggestions)"
    new_state["last_saved_at"] = now_iso
    project.state_json = new_state
    project.stage = "title"
    flag_modified(project, "state_json")

    current_user.quota_remaining = max(0, current_user.quota_remaining - 1)

    db.commit()
    db.refresh(project)
    return project


# ---------------------------------------------------------
# STAGE 4: DEEP-DIVE SEARCH
# ---------------------------------------------------------
@router.post("/projects/{project_id}/stage/deepdive", response_model=ProjectResponse)
@router.post("/api/projects/{project_id}/stage/deepdive", response_model=ProjectResponse)
def run_stage_deepdive(
    project_id: str,
    req: DeepDiveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes Stage 4 Deep-Dive Search for the chosen thesis title.
    Writes result immediately to projects.state_json.
    """
    project = _get_isolated_project(project_id, current_user, db)

    # 1. Execute Deep-Dive Agent through contract layer
    try:
        deepdive_resp = execute_deepdive_search(
            chosen_title=req.chosen_title,
            gap_id=req.gap_id,
            user=current_user,
            user_email=current_user.email,
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )

    # 2. State Persistence (D3): Write immediately to DB
    now_iso = datetime.now(timezone.utc).isoformat()
    new_state = dict(project.state_json or {})
    new_state["deepdive_papers"] = [p.model_dump() for p in deepdive_resp.papers]
    new_state["chosen_title"] = req.chosen_title
    new_state["last_saved_stage"] = "Stage 4 (Deep-Dive Search)"
    new_state["last_saved_at"] = now_iso
    project.state_json = new_state
    project.stage = "deep-dive"
    flag_modified(project, "state_json")

    current_user.quota_remaining = max(0, current_user.quota_remaining - 1)

    db.commit()
    db.refresh(project)
    return project



# ---------------------------------------------------------
# DIRECT AGENT ENDPOINTS (For standalone verification)
# ---------------------------------------------------------
@router.post("/api/agents/gap", response_model=GapAnalysisResponse)
def direct_gap_agent(
    req: GapAnalysisRequest,
    current_user: Optional[User] = Depends(get_current_user),
):
    """Direct invocation of Gap Analysis Agent with contract enforcement."""
    papers = req.papers or []
    if not papers:
        from app.ai.provider import _load_fixture_data
        sample_data = _load_fixture_data("sample_abstracts.json") or []
        papers = [Paper(**p) for p in sample_data]

    try:
        return analyze_research_gaps(
            papers=papers,
            user=current_user,
            user_email=current_user.email if current_user else "anonymous",
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )


@router.post("/api/agents/title", response_model=TitleSuggestionsResponse)
def direct_title_agent(
    req: TitleSuggestionsRequest,
    current_user: Optional[User] = Depends(get_current_user),
):
    """Direct invocation of Title Suggestions Agent with contract enforcement."""
    gap_data = req.gap or {"gap_id": req.gap_id or "GAP-1", "description": "Sample gap"}
    try:
        return generate_thesis_titles(
            gap_data=gap_data,
            language=req.language or "EN",
            user=current_user,
            user_email=current_user.email if current_user else "anonymous",
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )


@router.post("/api/agents/deepdive", response_model=DeepDiveResponse)
def direct_deepdive_agent(
    req: DeepDiveRequest,
    current_user: Optional[User] = Depends(get_current_user),
):
    """Direct invocation of Deep-Dive Agent with contract enforcement."""
    try:
        return execute_deepdive_search(
            chosen_title=req.chosen_title,
            gap_id=req.gap_id,
            user=current_user,
            user_email=current_user.email if current_user else "anonymous",
        )
    except AIPolicyRefusalError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message}
        )
    except AIQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_QUOTA", "message": e.user_message}
        )
    except AIContractError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "AI_CONTRACT_ERROR", "message": e.user_message, "detail": e.detail}
        )
