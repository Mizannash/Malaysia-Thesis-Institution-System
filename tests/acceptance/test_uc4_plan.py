"""
Acceptance Test Suite: Use Case 4 - Plan Generation & Iterative Refinement (Rubric D1, D3, D5).

Acceptance Criteria:
1. "Given a completed project state, when the Plan Agent runs, then a structured plan JSON is generated within 30 seconds."
2. "Given a plan and a refinement prompt, when the refinement agent change (verified by diffing the two plan JSONs in DB)."
3. Multi-tenant isolation and policy enforcement during refinement.
"""
import sys
import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import SessionLocal, set_tenant_context
from app.models import Project, User
from app.schemas import StructuredPlan

CLIENT = TestClient(app)


def get_token(client: TestClient, email: str, role: str = "student", tenant_id: str = "tenant-utm-001"):
    res = client.post("/auth/demo-login", json={
        "email": email,
        "name": "Plan Test User",
        "role": role,
        "tenant_id": tenant_id
    })
    assert res.status_code == 200
    return res.json()["access_token"]


def test_plan_generation_within_30_seconds():
    """
    Criterion 1:
    Given a completed project state (Search results, Gap list, Title, Deep-Dive papers),
    when the Plan Agent runs, then a structured plan JSON is generated within 30 seconds.
    """
    user_email = f"plan_student_{int(time.time())}@utm.my"
    token = get_token(CLIENT, user_email, role="student", tenant_id="tenant-utm-001")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a project with complete upstream state (Stages 1-4)
    create_res = CLIENT.post(
        "/projects",
        json={
            "title": "Autonomous LLM Multi-Agent Coordination for Malaysian Higher Education",
            "stage": "deep-dive",
            "state_json": {
                "papers": [
                    {
                        "title": "Institutional Open Access Frameworks in Malaysia",
                        "authors": ["Ahmad, Z.", "Razak, N."],
                        "year": 2024,
                        "doi": "10.1000/182",
                        "abstract": "Studies open access compliance across Malaysian research universities.",
                        "source": "openalex",
                        "citation_count": 14
                    }
                ],
                "gaps": [
                    {
                        "gap_id": "GAP-1",
                        "description": "Lack of real-time AI supervisor feedback loops for postgraduate research students in Malaysian universities."
                    }
                ],
                "chosen_gap_id": "GAP-1",
                "chosen_title": "Autonomous LLM Multi-Agent Coordination for Malaysian Higher Education",
                "deepdive_papers": [
                    {
                        "title": "LLM Verification and Quality Assurances in Higher Ed",
                        "authors": ["Lee, C.", "Tan, W."],
                        "year": 2025,
                        "doi": "10.1000/183",
                        "abstract": "Evaluates deterministic multi-agent orchestration for institutional compliance.",
                        "source": "openalex",
                        "citation_count": 22
                    }
                ],
            }
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Measure execution time for Plan Agent
    start_time = time.time()
    plan_res = CLIENT.post(
        f"/projects/{project_id}/stage/plan",
        json={"project_id": project_id, "custom_instructions": "Focus on doctoral timeline constraints"},
        headers=headers,
    )
    elapsed = time.time() - start_time

    assert elapsed < 30.0, f"Plan generation exceeded 30 seconds: took {elapsed:.2f}s"
    assert plan_res.status_code == 200, plan_res.text

    data = plan_res.json()
    assert data["stage"] == "plan"
    assert data["plan_id"] is not None
    assert data["plan_version"] == 1
    assert data["current_plan_json"] is not None

    plan = data["current_plan_json"]
    # Schema checks: objectives, milestones, resources, timeline
    assert len(plan["objectives"]) >= 2, "Plan must contain at least 2 research objectives."
    assert len(plan["key_milestones"]) >= 3, "Plan must contain at least 3 milestones."
    assert len(plan["timeline"]) >= 2, "Plan must contain at least 2 timeline phases."
    assert len(plan["necessary_resources"]) >= 1, "Plan must list necessary resources."
    assert plan.get("methodology_summary") is not None and len(plan["methodology_summary"]) > 20

    # Verify directly in DB
    db = SessionLocal()
    try:
        set_tenant_context(db, "tenant-utm-001")
        db_proj = db.query(Project).filter(Project.id == project_id).first()
        assert db_proj is not None
        assert db_proj.plan_id == data["plan_id"]
        assert db_proj.plan_version == 1
        assert db_proj.current_plan_json["plan_id"] == data["plan_id"]
        assert db_proj.state_json["last_saved_stage"] == "Stage 5 (Objectives & Methodology Plan)"
    finally:
        db.close()


def test_iterative_refinement_changes_plan_and_increments_version():
    """
    Criterion 2:
    Given a plan and a refinement prompt, when the refinement agent runs,
    the plan demonstrably changes (verified by diffing the two plan JSONs in DB)
    and increments plan_version.
    """
    user_email = f"refine_student_{int(time.time())}@utm.my"
    token = get_token(CLIENT, user_email, role="student", tenant_id="tenant-utm-001")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create project and generate initial plan
    create_res = CLIENT.post(
        "/projects",
        json={
            "title": "FinTech Adoption in Malaysian Islamic Banking",
            "stage": "deep-dive",
            "state_json": {
                "chosen_title": "FinTech Adoption in Malaysian Islamic Banking",
                "chosen_gap_id": "GAP-MY-01",
                "gaps": [{"gap_id": "GAP-MY-01", "description": "Insufficient Shariah-compliant smart contracts evaluation."}],
                "papers": [{"title": "Islamic Banking Tech", "authors": ["Hashim, M."], "year": 2024, "source": "openalex"}],
            }
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    plan_res = CLIENT.post(f"/projects/{project_id}/stage/plan", headers=headers)
    assert plan_res.status_code == 200
    plan_v1 = plan_res.json()["current_plan_json"]
    plan_id = plan_res.json()["plan_id"]
    assert plan_v1 is not None
    assert plan_res.json()["plan_version"] == 1

    # 2. Send refinement prompt via POST /api/plan/refine
    refinement_prompt = "Too ambitious: please focus specifically on Malaysian SMEs and reduce timeline to 18 months."
    refine_res = CLIENT.post(
        "/api/plan/refine",
        json={
            "plan_id": plan_id,
            "project_id": project_id,
            "user_prompt": refinement_prompt,
        },
        headers=headers,
    )
    assert refine_res.status_code == 200, refine_res.text
    refine_data = refine_res.json()

    assert refine_data["plan_version"] == 2
    plan_v2 = refine_data["plan"]
    assert plan_v2["version"] == 2

    # 3. Verify in DB and diff the two versions
    db = SessionLocal()
    try:
        set_tenant_context(db, "tenant-utm-001")
        db_proj = db.query(Project).filter(Project.id == project_id).first()
        assert db_proj is not None
        assert db_proj.plan_version == 2
        assert db_proj.last_refined_at is not None

        db_plan_v2 = db_proj.current_plan_json
        assert db_plan_v2["version"] == 2

        # Demonstrable difference check (diffing the two plan JSONs)
        # Objectives or timeline tasks or methodology must reflect the refinement
        v1_objectives = [o["text"] for o in plan_v1["objectives"]]
        v2_objectives = [o["text"] for o in db_plan_v2["objectives"]]
        v1_methodology = plan_v1.get("methodology_summary", "")
        v2_methodology = db_plan_v2.get("methodology_summary", "")

        is_different = (
            v1_objectives != v2_objectives
            or v1_methodology != v2_methodology
            or plan_v1.get("timeline") != db_plan_v2.get("timeline")
        )
        assert is_different, "Plan JSON v2 must demonstrably differ from v1 after refinement."
    finally:
        db.close()


def test_cross_tenant_refinement_refusal():
    """Security requirement (D2/D3): Cross-tenant refinement attempts must be refused with 403."""
    # Tenant 1 user creates project
    t1_email = f"t1_user_{int(time.time())}@utm.my"
    t1_token = get_token(CLIENT, t1_email, tenant_id="tenant-utm-001")
    t1_headers = {"Authorization": f"Bearer {t1_token}"}

    create_res = CLIENT.post(
        "/projects",
        json={"title": "Tenant 1 Confidential Research", "stage": "search", "state_json": {}},
        headers=t1_headers,
    )
    project_id = create_res.json()["id"]

    plan_res = CLIENT.post(f"/projects/{project_id}/stage/plan", headers=t1_headers)
    plan_id = plan_res.json()["plan_id"]

    # Tenant 2 user attempts to refine Tenant 1's plan
    t2_email = f"t2_user_{int(time.time())}@demouniv.edu.my"
    t2_token = get_token(CLIENT, t2_email, tenant_id="tenant-demo-002")
    t2_headers = {"Authorization": f"Bearer {t2_token}"}

    refine_res = CLIENT.post(
        "/api/plan/refine",
        json={
            "plan_id": plan_id,
            "user_prompt": "Unauthorized malicious modification of tenant 1 plan",
        },
        headers=t2_headers,
    )
    assert refine_res.status_code == 403
    assert "Cross-tenant" in refine_res.json().get("message", "") or refine_res.status_code == 403
