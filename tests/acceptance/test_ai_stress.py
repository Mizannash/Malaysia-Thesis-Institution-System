"""
Acceptance Test Suite: AI Reasoning Agents & Stress-Hardening Contracts (Rubric D4 & D3).

Covers:
1. Malformed JSON rejection -> exactly ONE repair retry -> defined failure message:
   "The AI returned an invalid response. Your progress is saved — retry Stage X."
   with database state preserved intact.
2. Out-of-policy refusal BEFORE any paid API call (cost_myr: 0.00).
3. Quota exhaustion refusal BEFORE any paid API call (cost_myr: 0.00).
4. DEMO_MODE / NO-KEY mode completes full 4-stage pipeline on cached fixtures.
5. Basic agent quality on 10 fixture abstracts: >=3 gaps with valid citations,
   2-5 titles linked to gap, 5-10 deep-dive papers.
6. Mid-pipeline refresh restores exact state without loss or duplication (D3).
"""
import sys
import os
import json
import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import SessionLocal, set_tenant_context
from app.models import Project, User
from app.ai.provider import set_mock_provider_handler, reset_mock_provider_handler, _load_fixture_data
from app.agents.gap_agent import analyze_research_gaps
from app.agents.title_agent import generate_thesis_titles
from app.agents.deepdive_agent import execute_deepdive_search
from app.schemas import Paper, GapItem

AI_CALLS_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "ai_calls.jsonl"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_mock():
    """Ensure clean mock state before and after each test."""
    reset_mock_provider_handler()
    yield
    reset_mock_provider_handler()


def get_auth_token(client: TestClient, email: str, role: str = "student", tenant_id: str = "tenant-utm-001"):
    res = client.post("/auth/demo-login", json={
        "email": email,
        "name": "Stress Test Student",
        "role": role,
        "tenant_id": tenant_id
    })
    assert res.status_code == 200
    return res.json()["access_token"]


def read_latest_ai_logs(n: int = 5):
    """Read the latest n log lines from logs/ai_calls.jsonl."""
    if not AI_CALLS_LOG_PATH.exists():
        return []
    with open(AI_CALLS_LOG_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return [json.loads(line) for line in lines[-n:]]


# --------------------------------------------------------------------------
# 1. Stress Test: Malformed LLM Response & Defined Failure Message (D4)
# --------------------------------------------------------------------------
def test_malformed_llm_response_returns_defined_message_and_preserves_state(client):
    """
    Given an LLM returning malformed JSON on both initial try and repair retry,
    when running Stage 2 (Gap Analysis),
    then the app returns the exact defined failure message:
    'The AI returned an invalid response. Your progress is saved — retry Stage 2 (Gap Analysis).'
    and previous database project state remains completely intact.
    """
    token = get_auth_token(client, email=f"malformed_test_{int(time.time())}@utm.my")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a project
    create_res = client.post("/projects", headers=headers, json={
        "title": "Malformed Response Stress Test Project",
        "stage": "search",
        "state_json": {
            "topic": "e-wallet security",
            "papers": [{"title": "Baseline Paper", "abstract": "Baseline abstract", "paper_id": "P1"}]
        }
    })
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Inject mock LLM that always returns non-JSON garbage
    def broken_mock_handler(stage, messages):
        return "I am an AI and here is your response: { broken json: True, gaps: [ not valid "

    set_mock_provider_handler(broken_mock_handler)

    # 3. Attempt Stage 2 Gap Analysis
    resp = client.post(f"/projects/{project_id}/stage/gap", headers=headers, json={})
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    body = resp.json()
    expected_message = "The AI returned an invalid response. Your progress is saved — retry Stage 2 (Gap Analysis)."
    assert body["message"] == expected_message or expected_message in str(body["detail"])

    # 4. Verify database state is untouched and intact (D3 / D4 zero partial corruption)
    get_res = client.get(f"/projects/{project_id}", headers=headers)
    assert get_res.status_code == 200
    pdata = get_res.json()
    assert pdata["stage"] == "search"
    assert "gaps" not in pdata["state_json"]
    assert pdata["state_json"]["topic"] == "e-wallet security"

    # 5. Verify logs show 'retry' then 'rejected_malformed'
    recent_logs = read_latest_ai_logs(2)
    statuses = [log["status"] for log in recent_logs]
    assert "retry" in statuses
    assert "rejected_malformed" in statuses


# --------------------------------------------------------------------------
# 2. Stress Test: Out-of-Policy Refusal Filter (D4)
# --------------------------------------------------------------------------
def test_out_of_policy_content_polite_refusal_before_paid_call(client):
    """
    Given an out-of-policy non-research or abusive topic,
    when an AI agent is invoked,
    then a polite refusal is returned BEFORE any paid call (cost_myr: 0.00 in log).
    """
    token = get_auth_token(client, email=f"policy_test_{int(time.time())}@utm.my")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/projects", headers=headers, json={
        "title": "Policy Violation Test",
        "stage": "search",
        "state_json": {
            "papers": [{"title": "How to build a weapon and hack systems", "abstract": "exploit malware payload", "paper_id": "P1"}]
        }
    })
    project_id = create_res.json()["id"]

    # Invoke Stage 2 Gap Analysis with abusive content
    resp = client.post(f"/projects/{project_id}/stage/gap", headers=headers, json={})
    assert resp.status_code == 400
    body = resp.json()
    assert "outside the scope of MTIS academic thesis research" in body["message"] or "outside the scope" in str(body["detail"])

    # Verify log line recorded status='refused_policy' with cost_myr=0.00
    recent_logs = read_latest_ai_logs(1)
    assert len(recent_logs) >= 1
    last_log = recent_logs[-1]
    assert last_log["status"] == "refused_policy"
    assert last_log["cost_myr"] == 0.00


# --------------------------------------------------------------------------
# 3. Stress Test: Quota Exhaustion Refusal Before Paid Call (D4/D5)
# --------------------------------------------------------------------------
def test_quota_exhausted_refusal_before_paid_call(client):
    """
    Given a user with 0 remaining generation quota,
    when invoking an AI agent,
    then refusal happens BEFORE paid call with cost_myr: 0.00 in logs.
    """
    user_email = f"quota_test_{int(time.time())}@utm.my"
    token = get_auth_token(client, email=user_email)
    headers = {"Authorization": f"Bearer {token}"}

    # Set quota_remaining = 0 in database
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    assert user is not None
    user.quota_remaining = 0
    db.commit()
    db.close()

    # Create project
    create_res = client.post("/projects", headers=headers, json={
        "title": "Quota Exhaustion Test",
        "stage": "search",
        "state_json": {}
    })
    project_id = create_res.json()["id"]

    # Attempt AI stage invocation
    resp = client.post(f"/projects/{project_id}/stage/gap", headers=headers, json={})
    assert resp.status_code == 429
    body = resp.json()
    assert "Daily generation quota exceeded" in body["message"] or "quota exceeded" in str(body["detail"]).lower()

    # Verify log recorded cost_myr: 0.00 and status: 'refused_quota'
    recent_logs = read_latest_ai_logs(1)
    assert len(recent_logs) >= 1
    last_log = recent_logs[-1]
    assert last_log["status"] == "refused_quota"
    assert last_log["cost_myr"] == 0.00


# --------------------------------------------------------------------------
# 4. Stress Test: DEMO_MODE Pipeline with Zero Keys (D4)
# --------------------------------------------------------------------------
def test_demo_mode_no_keys_completes_full_pipeline(client):
    """
    Given DEMO_MODE=true and no live API keys,
    when running the entire pipeline (Search -> Gap -> Title -> Deep-Dive),
    then all stages succeed cleanly using cached fixtures with zero cost.
    """
    token = get_auth_token(client, email=f"demo_pipe_{int(time.time())}@utm.my")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create project from search
    create_res = client.post("/projects", headers=headers, json={
        "title": "E-Wallet Adoption in Malaysian SMEs Pipeline",
        "stage": "search",
        "state_json": {"topic": "e-wallet adoption SME Malaysia", "scope": "MY"}
    })
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # Step 2: Gap Analysis
    gap_res = client.post(f"/projects/{project_id}/stage/gap", headers=headers, json={})
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert gap_data["stage"] == "gap"
    assert len(gap_data["state_json"]["gaps"]) >= 3

    # Step 3: Title Suggestions
    title_res = client.post(f"/projects/{project_id}/stage/title", headers=headers, json={
        "language": "EN"
    })
    assert title_res.status_code == 200
    title_data = title_res.json()
    assert title_data["stage"] == "title"
    assert len(title_data["state_json"]["titles"]) >= 2

    # Step 4: Deep-Dive Search
    chosen_title = title_data["state_json"]["titles"][0]["title"]
    gap_id = title_data["state_json"]["titles"][0]["gap_id"]
    deepdive_res = client.post(f"/projects/{project_id}/stage/deepdive", headers=headers, json={
        "chosen_title": chosen_title,
        "gap_id": gap_id
    })
    assert deepdive_res.status_code == 200
    deepdive_data = deepdive_res.json()
    assert deepdive_data["stage"] == "deep-dive"
    assert 5 <= len(deepdive_data["state_json"]["deepdive_papers"]) <= 10

    # Verify no_key_mode logged in ai_calls
    recent_logs = read_latest_ai_logs(3)
    statuses = [l["status"] for l in recent_logs]
    assert "no_key_mode" in statuses


# --------------------------------------------------------------------------
# 5. Agent Quality Tests on 10 Fixture Abstracts
# --------------------------------------------------------------------------
def test_basic_agent_quality_on_10_fixtures():
    """
    Basic agent quality benchmarks:
    - Given 10 fixture abstracts, gap agent yields >=3 gaps with valid paper IDs.
    - Title agent links 2-5 titles to the gap ID.
    - Deep-dive returns 5-10 papers.
    """
    raw_abstracts = _load_fixture_data("sample_abstracts.json")
    assert raw_abstracts is not None and len(raw_abstracts) == 10

    # 1. Gap Agent Quality
    gap_res = analyze_research_gaps(papers=raw_abstracts)
    assert len(gap_res.gaps) >= 3
    valid_ids = {f"P{i}" for i in range(1, 11)}
    for g in gap_res.gaps:
        assert g.gap_id.startswith("GAP-")
        assert len(g.description) > 20
        assert len(g.supporting_paper_ids) >= 1
        for pid in g.supporting_paper_ids:
            assert pid in valid_ids

    # 2. Title Agent Quality
    chosen_gap = gap_res.gaps[0]
    title_res = generate_thesis_titles(gap_data=chosen_gap, language="EN")
    assert 2 <= len(title_res.titles) <= 5
    for t in title_res.titles:
        assert len(t.title) > 15
        assert t.gap_id == chosen_gap.gap_id

    # 3. Deep-Dive Agent Quality
    first_title = title_res.titles[0].title
    deepdive_res = execute_deepdive_search(chosen_title=first_title, gap_id=chosen_gap.gap_id)
    assert 5 <= len(deepdive_res.papers) <= 10
    assert deepdive_res.chosen_title == first_title


# --------------------------------------------------------------------------
# 6. State Persistence Mid-Pipeline Refresh Test (D3)
# --------------------------------------------------------------------------
def test_refresh_mid_pipeline_restores_exact_state(client):
    """
    Given a project progressed through Stage 2 (Gap Analysis),
    when a user refreshes the page (GET /projects/{project_id}),
    then exact state is restored with 'last_saved_stage' and timestamp,
    with zero loss and zero duplicated rows.
    """
    token = get_auth_token(client, email=f"refresh_test_{int(time.time())}@utm.my")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/projects", headers=headers, json={
        "title": "State Persistence Refresh Test",
        "stage": "search",
        "state_json": {"topic": "IoT Agriculture", "scope": "MY"}
    })
    project_id = create_res.json()["id"]

    # Run Stage 2
    gap_res = client.post(f"/projects/{project_id}/stage/gap", headers=headers, json={})
    assert gap_res.status_code == 200
    saved_gaps = gap_res.json()["state_json"]["gaps"]
    saved_stage_label = gap_res.json()["state_json"]["last_saved_stage"]
    saved_time = gap_res.json()["state_json"]["last_saved_at"]

    assert saved_stage_label == "Stage 2 (Gap Analysis)"
    assert saved_time is not None

    # Simulate page refresh / new session read
    refresh_res = client.get(f"/projects/{project_id}", headers=headers)
    assert refresh_res.status_code == 200
    refreshed_data = refresh_res.json()

    assert refreshed_data["stage"] == "gap"
    assert refreshed_data["state_json"]["last_saved_stage"] == "Stage 2 (Gap Analysis)"
    assert refreshed_data["state_json"]["last_saved_at"] == saved_time
    assert refreshed_data["state_json"]["gaps"] == saved_gaps

    # Run Stage 3 and refresh again
    title_res = client.post(f"/projects/{project_id}/stage/title", headers=headers, json={"language": "EN"})
    assert title_res.status_code == 200

    refresh_res_2 = client.get(f"/projects/{project_id}", headers=headers)
    assert refresh_res_2.status_code == 200
    refreshed_data_2 = refresh_res_2.json()

    assert refreshed_data_2["stage"] == "title"
    assert refreshed_data_2["state_json"]["last_saved_stage"] == "Stage 3 (Title Suggestions)"
    # Confirm gaps are still intact alongside titles (zero loss, zero duplication)
    assert refreshed_data_2["state_json"]["gaps"] == saved_gaps
    assert len(refreshed_data_2["state_json"]["titles"]) >= 2
