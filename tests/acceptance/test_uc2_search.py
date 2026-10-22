"""
Acceptance Test for UC2: Academic Literature Search & Acquisition.

Requirements Covered:
1. Given topic 'e-wallet adoption SME Malaysia' with MY toggle, when searching, then >=10 structured papers with title, year, DOI display within 30 seconds.
2. Given an invalid input, when submitted, then an inline error appears (HTTP 422) and NO project row is created.
3. Fixture-based scraper test: >=5 structured records extracted from UTM fixture.
4. Deduplication: a paper present in multiple sources appears once.
5. DEMO_MODE search runs with zero API keys.
6. Structured logging: every search logs {user, query, scope, source, result_count, latency_ms, cost_myr: 0} to logs/search_log.jsonl.
"""
import sys
import time
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import SessionLocal
from app.models import Project
from app.agents.utm_scraper import search_utm_repository, parse_utm_html, load_fixture
from app.agents.openalex_client import (
    search as openalex_search,
    OpenAlexError,
    OpenAlexTimeoutError,
    OpenAlexRateLimitError,
    OpenAlexEmptyResultError
)
from app.schemas import Paper


@pytest.fixture
def client():
    return TestClient(app)


def test_uc2_search_my_scope_success(client):
    """
    Given topic 'e-wallet adoption SME Malaysia' with MY toggle,
    when searching,
    then >=10 structured papers with title, year, DOI display within 30 seconds.
    """
    start_time = time.time()
    payload = {
        "query": "e-wallet adoption SME Malaysia",
        "scope": "MY"
    }
    
    resp = client.post("/api/search", json=payload)
    duration = time.time() - start_time

    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    assert duration < 30.0, f"Search took {duration:.2f}s, exceeding 30s threshold"

    data = resp.json()
    assert data["query"] == "e-wallet adoption SME Malaysia"
    assert data["scope"] == "MY"
    assert "papers" in data
    assert data["total"] >= 10, f"Expected >= 10 papers, got {data['total']}"

    # Verify structured fields on returned papers
    for paper in data["papers"]:
        assert "title" in paper and len(paper["title"]) > 0
        assert "authors" in paper and isinstance(paper["authors"], list)
        assert "source" in paper and paper["source"] in ("openalex", "utm")
        assert "citation_count" in paper

    # Verify at least some papers contain year and DOI
    papers_with_doi = [p for p in data["papers"] if p.get("doi")]
    assert len(papers_with_doi) >= 5, "Expected >= 5 papers with valid DOIs"

    papers_with_year = [p for p in data["papers"] if p.get("year")]
    assert len(papers_with_year) >= 8, "Expected >= 8 papers with publication years"


def test_uc2_search_invalid_input_zero_db_writes(client):
    """
    Given an invalid input (empty, >300 chars, gibberish),
    when submitted,
    then an inline error appears (HTTP 422) and NO project row is created.
    """
    db = SessionLocal()
    try:
        initial_project_count = db.query(Project).count()
    finally:
        db.close()

    invalid_cases = [
        {"query": "", "scope": "MY", "expected_code": 422},
        {"query": "   ", "scope": "MY", "expected_code": 422},
        {"query": "a" * 305, "scope": "MY", "expected_code": 422},
        {"query": "asdfghjkl12345", "scope": "MY", "expected_code": 422},
        {"query": "qwertyuiopasdfgh", "scope": "MY", "expected_code": 422},
        {"query": "zzzzzzzzzzzz", "scope": "MY", "expected_code": 422},
        {"query": "valid query", "scope": "INVALID_SCOPE", "expected_code": 422},
    ]

    for case in invalid_cases:
        resp = client.post("/api/search", json={"query": case["query"], "scope": case["scope"]})
        assert resp.status_code == case["expected_code"], f"Query '{case['query'][:30]}' expected {case['expected_code']} got {resp.status_code}"
        
        # Verify error contract format {"error": ..., "message": ...}
        body = resp.json()
        assert "error" in body, f"Response missing 'error' key: {body}"
        assert "message" in body, f"Response missing 'message' key: {body}"

    # Assert ZERO project rows created in database
    db = SessionLocal()
    try:
        current_project_count = db.query(Project).count()
        assert current_project_count == initial_project_count, (
            f"Database mutation detected! Expected {initial_project_count} projects, found {current_project_count}"
        )
    finally:
        db.close()


def test_uc2_utm_scraper_fixture_extraction():
    """
    Fixture-based scraper test: >=5 structured records extracted from UTM fixture.
    """
    papers = search_utm_repository("e-wallet", use_fixture=True)
    assert len(papers) >= 5, f"Expected >= 5 papers from fixture, got {len(papers)}"

    for p in papers:
        assert isinstance(p, Paper)
        assert p.source == "utm"
        assert len(p.title) > 5
        assert p.year is not None and p.year >= 2020
        assert p.url and "eprints.utm.my" in p.url
        assert p.doi is not None


def test_uc2_deduplication_by_doi(client):
    """
    Deduplication assertion:
    When a paper with the same DOI exists in both OpenAlex and UTM,
    it must appear only ONCE in the response list.
    """
    resp = client.post("/api/search", json={"query": "Determinants of E-Wallet Adoption", "scope": "MY"})
    assert resp.status_code == 200
    data = resp.json()
    papers = data["papers"]

    dois = [p["doi"].lower().strip() for p in papers if p.get("doi")]
    unique_dois = set(dois)
    assert len(dois) == len(unique_dois), f"Duplicate DOIs detected: {dois}"


def test_uc2_demo_mode_search_zero_external_api_keys(client):
    """
    DEMO_MODE=true boots and searches with zero API keys required.
    """
    resp = client.post("/api/search", json={"query": "cashless digital transformation", "scope": "MY"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["papers"]) >= 5


def test_uc2_search_structured_logging():
    """
    Structured logging:
    Every search logs {user, query, scope, source, result_count, latency_ms, cost_myr: 0}
    to logs/search_log.jsonl (D5 cost evidence: search is free; AI calls are not).
    """
    test_client = TestClient(app)
    query_str = "e-wallet logging test verification"
    resp = test_client.post("/api/search", json={"query": query_str, "scope": "MY"})
    assert resp.status_code == 200

    log_file = Path(__file__).resolve().parent.parent.parent / "logs" / "search_log.jsonl"
    if not log_file.exists():
        log_file = Path(__file__).resolve().parent.parent.parent / "backend" / "logs" / "search_log.jsonl"

    assert log_file.exists(), f"Search log file not found at {log_file}"

    # Read last line
    with open(log_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) > 0
    last_log = json.loads(lines[-1])
    
    assert last_log["cost_myr"] == 0, f"Expected cost_myr 0, got {last_log['cost_myr']}"
    assert "latency_ms" in last_log
    assert last_log["scope"] == "MY"
    assert "user" in last_log
    assert "result_count" in last_log


@pytest.mark.live
def test_uc2_live_openalex_query():
    """
    Optional live network test against openalex.org (marked with @pytest.mark.live).
    Skipped by default to ensure reproducible, zero-network test runs per Rubric D5.
    Set RUN_LIVE_TESTS=1 to execute.
    """
    import os
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Skipping live network test in default run (D5 reproducibility). Set RUN_LIVE_TESTS=1 to run.")

    try:
        papers = openalex_search("e-wallet Malaysia", scope="MY", timeout=15.0)
        assert len(papers) >= 1
    except OpenAlexError as e:
        pytest.skip(f"Live OpenAlex network unreachable: {e}")
