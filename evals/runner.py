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
        
        # Only evaluate phase1 cases during Phase 1
        if case_type != "phase1":
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
                # Protected dashboard endpoint refusal/redirect check
                resp = client.get("/projects", headers={})
                duration = time.time() - start_time
                if resp.status_code == 401 and duration < 5.0:
                    passed = True
                    notes = f"Unauthenticated request correctly refused with HTTP 401 within {duration:.3f}s (< 5.0s threshold)"
                else:
                    notes = f"Status {resp.status_code}, duration {duration:.3f}s"

            elif case_id == "P1_CROSS_TENANT_REFUSAL":
                # Demo login as tenant-utm-001 student
                login_resp = client.post("/auth/demo-login", json={"email": "ahmad@utm.my"})
                assert login_resp.status_code == 200
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                # Attempt to access project belonging to tenant-demo-002 (seeded as prj-demo-201)
                resp = client.get("/projects/prj-demo-201", headers=headers)
                duration = time.time() - start_time

                if resp.status_code == 403:
                    body = resp.json()
                    detail = body.get("detail", "")
                    # Ensure no project data leaked
                    if "proj-demo-002" not in str(body) and "Blockchain" not in str(body):
                        passed = True
                        notes = f"Cross-tenant access refused with HTTP 403 in {duration:.3f}s. Detail: '{detail}'. Zero leaked data."
                    else:
                        notes = "HTTP 403 returned but sensitive project fields leaked in response."
                else:
                    notes = f"Expected HTTP 403, got HTTP {resp.status_code}: {resp.text}"

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
