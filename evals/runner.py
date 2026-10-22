"""
Evaluation Runner for Malaysian Thesis Institution System (MTIS).
Executes eval cases from evals/cases.json and records results.
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app

def run_evals():
    cases_file = Path(__file__).resolve().parent / "cases.json"
    with open(cases_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = TestClient(app)
    results = []
    
    print(f"Loaded {len(data['cases'])} cases from {cases_file.name}")
    print(f"Gate criteria: {data.get('gate', 'Every case passes')}\n")

    for case in data["cases"]:
        case_id = case["id"]
        case_type = case.get("type", "unknown")
        
        # Evaluate active phase cases (phase1 and phase2)
        if case_type not in ("phase1", "phase2"):
            continue

        start_time = time.time()
        passed = False
        notes = ""

        try:
            if case_id == "P1_HEALTH":
                resp = client.get("/health")
                duration = time.time() - start_time
                if resp.status_code == 200:
                    body = resp.json()
                    if body.get("status") == "ok" and body.get("service") == "mtis-backend":
                        passed = True
                        notes = f"HTTP 200 returned in {duration:.3f}s: {body}"
                    else:
                        notes = f"Unexpected payload: {body}"
                else:
                    notes = f"HTTP {resp.status_code}"

            elif case_id == "P1_AUTH_REDIRECT":
                resp = client.get("/projects", headers={})
                duration = time.time() - start_time
                if resp.status_code == 401 and duration < 5.0:
                    passed = True
                    notes = f"Unauthenticated request correctly refused with HTTP 401 within {duration:.3f}s (< 5.0s threshold)"
                else:
                    notes = f"Status {resp.status_code}, duration {duration:.3f}s"

            elif case_id == "P1_CROSS_TENANT_REFUSAL":
                login_resp = client.post("/auth/demo-login", json={"email": "ahmad@utm.my"})
                assert login_resp.status_code == 200
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                resp = client.get("/projects/prj-demo-201", headers=headers)
                duration = time.time() - start_time

                if resp.status_code == 403:
                    body = resp.json()
                    detail = body.get("detail", "")
                    if "proj-demo-002" not in str(body) and "Blockchain" not in str(body):
                        passed = True
                        notes = f"Cross-tenant access refused with HTTP 403 in {duration:.3f}s. Detail: '{detail}'. Zero leaked data."
                    else:
                        notes = "HTTP 403 returned but sensitive project fields leaked in response."
                else:
                    notes = f"Expected HTTP 403, got HTTP {resp.status_code}: {resp.text}"

            elif case_id == "P2_SEARCH_MY_SCOPE":
                resp = client.post("/api/search", json={"query": "e-wallet adoption SME Malaysia", "scope": "MY"})
                duration = time.time() - start_time
                if resp.status_code == 200 and duration < 30.0:
                    body = resp.json()
                    if body.get("total", 0) >= 10 and len(body.get("papers", [])) >= 10:
                        passed = True
                        notes = f"HTTP 200 returned in {duration:.3f}s with {body['total']} papers and source tags: {body.get('sources')}"
                    else:
                        notes = f"Expected >= 10 papers, got {body.get('total')}"
                else:
                    notes = f"Status {resp.status_code}, duration {duration:.3f}s"

            elif case_id == "P2_SEARCH_VALIDATION_ERROR":
                resp = client.post("/api/search", json={"query": "asdfghjkl12345", "scope": "MY"})
                duration = time.time() - start_time
                if resp.status_code == 422:
                    body = resp.json()
                    if "error" in body and "message" in body:
                        passed = True
                        notes = f"HTTP 422 error contract returned in {duration:.3f}s: error='{body.get('error')}'"
                    else:
                        notes = f"HTTP 422 returned but missing standardized error contract: {body}"
                else:
                    notes = f"Expected HTTP 422, got {resp.status_code}"

            elif case_id == "P2_SEARCH_DEDUPLICATION":
                resp = client.post("/api/search", json={"query": "Determinants of E-Wallet Adoption", "scope": "MY"})
                duration = time.time() - start_time
                if resp.status_code == 200:
                    body = resp.json()
                    dois = [p["doi"].lower().strip() for p in body.get("papers", []) if p.get("doi")]
                    if len(dois) == len(set(dois)):
                        passed = True
                        notes = f"Deduplication confirmed in {duration:.3f}s across {len(dois)} papers with DOIs"
                    else:
                        notes = f"Duplicate DOIs found: {dois}"
                else:
                    notes = f"Status {resp.status_code}"

        except Exception as e:
            duration = time.time() - start_time
            notes = f"Exception during execution: {str(e)}"

        results.append({
            "id": case_id,
            "type": case_type,
            "severity": case.get("severity", "normal"),
            "input": case.get("input", ""),
            "expect": case.get("expect", ""),
            "passed": passed,
            "duration": duration,
            "notes": notes
        })

    return results

if __name__ == "__main__":
    results = run_evals()
    all_passed = all(r["passed"] for r in results)
    
    print("=" * 60)
    print("PHASE 1 EVALUATION RESULTS")
    print("=" * 60)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']} ({r['duration']:.3f}s): {r['notes']}")
    print("=" * 60)
    print(f"GATE VERDICT: {'PASS' if all_passed else 'FAIL'}")
    
    sys.exit(0 if all_passed else 1)
