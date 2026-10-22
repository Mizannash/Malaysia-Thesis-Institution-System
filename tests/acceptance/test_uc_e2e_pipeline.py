"""
End-to-End High-Level Acceptance & Integration Test: Full Guided Research Pipeline.
Validates the complete researcher journey:
Search -> Gap Analysis -> Title Suggestions -> Deep-Dive Search -> Plan Generation -> Plan Refinement.
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

CLIENT = TestClient(app)


def get_auth_token(client: TestClient, email: str, role: str = "student", tenant_id: str = "tenant-utm-001"):
    res = client.post("/auth/demo-login", json={
        "email": email,
        "name": "E2E Student Researcher",
        "role": role,
        "tenant_id": tenant_id
    })
    assert res.status_code == 200
    return res.json()["access_token"]


def test_full_e2e_pipeline_journey():
    """
    High-level integration test running the complete 5-stage MTIS pipeline
    from initial search to refined versioned thesis plan using fixtures.
    """
    user_email = f"e2e_researcher_{int(time.time()*1000)}@utm.my"
    token = get_auth_token(CLIENT, user_email, role="supervisor", tenant_id="tenant-utm-001")
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------
    # Step 0: Initialize Research Project
    # -------------------------------------------------------------
    create_res = CLIENT.post(
        "/projects",
        json={
            "title": "FinTech Adoption and Trust Dynamics in Malaysian SMEs",
            "stage": "search",
            "state_json": {}
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    project_data = create_res.json()
    project_id = project_data["id"]
    assert project_data["tenant_id"] == "tenant-utm-001"

    # -------------------------------------------------------------
    # Step 1: Topic Search (Data Acquisition)
    # -------------------------------------------------------------
    search_res = CLIENT.post(
        "/api/search",
        json={"query": "e-wallet adoption SME Malaysia", "scope": "MY", "limit": 10},
        headers=headers,
    )
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 10
    papers = search_data["papers"]
    assert len(papers) >= 10
    assert "openalex" in search_data["sources"]

    # -------------------------------------------------------------
    # Step 2: Gap Analysis (Stage 2 Reasoning Agent)
    # -------------------------------------------------------------
    gap_res = CLIENT.post(
        f"/projects/{project_id}/stage/gap",
        json={"project_id": project_id, "papers": papers},
        headers=headers,
    )
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert gap_data["stage"] == "gap"
    gaps = gap_data["state_json"]["gaps"]
    assert len(gaps) >= 1, "Must produce candidate research gaps"
    chosen_gap = gaps[0]
    assert "gap_id" in chosen_gap
    assert "description" in chosen_gap
    assert "Stage 2" in gap_data["state_json"].get("last_saved_stage", "")

    # -------------------------------------------------------------
    # Step 3: Title Suggestions (Stage 3 Reasoning Agent)
    # -------------------------------------------------------------
    title_res = CLIENT.post(
        f"/projects/{project_id}/stage/title",
        json={
            "project_id": project_id,
            "gap_id": chosen_gap["gap_id"],
            "language": "EN"
        },
        headers=headers,
    )
    assert title_res.status_code == 200
    title_data = title_res.json()
    assert title_data["stage"] == "title"
    titles = title_data["state_json"]["titles"]
    assert len(titles) >= 2, "Must produce at least 2 thesis titles"
    chosen_title = titles[0]["title"]
    assert len(chosen_title) > 10

    # -------------------------------------------------------------
    # Step 4: Deep-Dive Search (Stage 4 Literature Refinement)
    # -------------------------------------------------------------
    deepdive_res = CLIENT.post(
        f"/projects/{project_id}/stage/deepdive",
        json={
            "project_id": project_id,
            "chosen_title": chosen_title,
            "gap_id": chosen_gap["gap_id"],
        },
        headers=headers,
    )
    assert deepdive_res.status_code == 200
    deepdive_data = deepdive_res.json()
    assert deepdive_data["stage"] == "deep-dive"
    assert len(deepdive_data["state_json"]["deepdive_papers"]) >= 3

    # -------------------------------------------------------------
    # Step 5: Plan Generation (Stage 5 Objectives & Methodology Plan)
    # -------------------------------------------------------------
    plan_res = CLIENT.post(
        f"/projects/{project_id}/stage/plan",
        json={"project_id": project_id, "custom_instructions": "Focus on doctoral timeline constraints"},
        headers=headers,
    )
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert plan_data["stage"] == "plan"
    assert plan_data["plan_id"] is not None
    assert plan_data["plan_version"] == 1
    assert plan_data["current_plan_json"] is not None

    plan_v1 = plan_data["current_plan_json"]
    # Verify complete StructuredPlan schema
    assert len(plan_v1["objectives"]) >= 2, "Must contain at least 2 research objectives"
    assert len(plan_v1["key_milestones"]) >= 3, "Must contain at least 3 milestones"
    assert len(plan_v1["timeline"]) >= 2, "Must contain at least 2 timeline phases"
    assert len(plan_v1["necessary_resources"]) >= 1, "Must detail necessary resources"
    assert len(plan_v1["methodology_summary"]) > 20

    # -------------------------------------------------------------
    # Step 6: Iterative Plan Refinement (Requirement 2 & D3)
    # -------------------------------------------------------------
    refine_prompt = "Supervisor requested to focus exclusively on semi-rural Johor SMEs and shorten data collection to 2 months."
    refine_res = CLIENT.post(
        "/api/plan/refine",
        json={
            "plan_id": plan_data["plan_id"],
            "project_id": project_id,
            "user_prompt": refine_prompt,
        },
        headers=headers,
    )
    assert refine_res.status_code == 200
    refine_data = refine_res.json()
    assert refine_data["plan_version"] == 2
    plan_v2 = refine_data["plan"]
    assert plan_v2["version"] == 2

    # -------------------------------------------------------------
    # Step 7: Database State & Relational Integrity Audit
    # -------------------------------------------------------------
    db = SessionLocal()
    try:
        set_tenant_context(db, "tenant-utm-001")
        db_proj = db.query(Project).filter(Project.id == project_id).first()
        assert db_proj is not None
        assert db_proj.plan_version == 2
        assert db_proj.plan_id == plan_data["plan_id"]
        assert db_proj.last_refined_at is not None
        assert db_proj.stage == "plan"
        assert db_proj.current_plan_json["version"] == 2

        # State JSON integrity
        st = db_proj.state_json
        assert "gaps" in st
        assert "titles" in st
        assert "deepdive_papers" in st
        assert "plan" in st
        assert st["plan"]["version"] == 2
    finally:
        db.close()
