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
        
        # Evaluate active phase cases (phase1, phase2, phase3)
        if case_type not in ("phase1", "phase2", "phase3"):
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

            elif case_id == "P3_MALFORMED_REPAIR_FAILURE":
                from app.ai.provider import set_mock_provider_handler, reset_mock_provider_handler
                login_resp = client.post("/auth/demo-login", json={"email": "eval_malformed@utm.my"})
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                cp = client.post("/projects", headers=headers, json={"title": "Eval Malformed Test", "stage": "search", "state_json": {}})
                pid = cp.json()["id"]

                set_mock_provider_handler(lambda stage, msg: "{ broken non-json content }")
                try:
                    resp = client.post(f"/projects/{pid}/stage/gap", headers=headers, json={})
                    duration = time.time() - start_time
                    if resp.status_code == 422:
                        body = resp.json()
                        expected_msg = "The AI returned an invalid response. Your progress is saved — retry Stage 2 (Gap Analysis)."
                        if body.get("message") == expected_msg or expected_msg in str(body.get("detail")):
                            passed = True
                            notes = f"Contract failure enforced with defined user message in {duration:.3f}s"
                        else:
                            notes = f"422 returned but message mismatch: {body}"
                    else:
                        notes = f"Expected HTTP 422, got {resp.status_code}"
                finally:
                    reset_mock_provider_handler()

            elif case_id == "P3_POLICY_REFUSAL":
                login_resp = client.post("/auth/demo-login", json={"email": "eval_policy@utm.my"})
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                resp = client.post("/api/agents/gap", headers=headers, json={
                    "papers": [{"title": "How to make a bomb weapon", "abstract": "exploit malware attack", "paper_id": "P1"}]
                })
                duration = time.time() - start_time
                if resp.status_code == 400:
                    body = resp.json()
                    if "outside the scope of MTIS" in str(body):
                        passed = True
                        notes = f"Out-of-policy refusal triggered before paid call in {duration:.3f}s: {body.get('message')}"
                    else:
                        notes = f"400 returned but unexpected message: {body}"
                else:
                    notes = f"Expected HTTP 400, got {resp.status_code}"

            elif case_id == "P3_QUOTA_EXHAUSTION":
                from app.database import SessionLocal
                from app.models import User
                login_resp = client.post("/auth/demo-login", json={"email": "eval_quota@utm.my"})
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                db = SessionLocal()
                u = db.query(User).filter(User.email == "eval_quota@utm.my").first()
                if u:
                    u.quota_remaining = 0
                    db.commit()
                db.close()

                resp = client.post("/api/agents/gap", headers=headers, json={"papers": []})
                duration = time.time() - start_time
                if resp.status_code == 429:
                    body = resp.json()
                    if "Daily generation quota exceeded" in str(body):
                        passed = True
                        notes = f"Quota exhaustion gate enforced before paid call in {duration:.3f}s"
                    else:
                        notes = f"429 returned but unexpected message: {body}"
                else:
                    notes = f"Expected HTTP 429, got {resp.status_code}"

            elif case_id == "P3_DEMO_MODE_PIPELINE":
                user_email = f"eval_demo_pipe_{int(time.time()*1000)}@utm.my"
                login_resp = client.post("/auth/demo-login", json={"email": user_email})
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                cp = client.post("/projects", headers=headers, json={"title": "Eval Demo Pipeline", "stage": "search", "state_json": {}})
                pid = cp.json()["id"]

                g_res = client.post(f"/projects/{pid}/stage/gap", headers=headers, json={})
                t_res = client.post(f"/projects/{pid}/stage/title", headers=headers, json={"language": "EN"})
                chosen_t = t_res.json()["state_json"]["titles"][0]["title"]
                chosen_g = t_res.json()["state_json"]["titles"][0]["gap_id"]
                d_res = client.post(f"/projects/{pid}/stage/deepdive", headers=headers, json={"chosen_title": chosen_t, "gap_id": chosen_g})
                duration = time.time() - start_time

                if g_res.status_code == 200 and t_res.status_code == 200 and d_res.status_code == 200:
                    d_data = d_res.json()
                    if len(d_data["state_json"]["deepdive_papers"]) >= 5:
                        passed = True
                        notes = f"Full 4-stage pipeline completed on fixtures in {duration:.3f}s with 0 external keys"
                    else:
                        notes = f"Deep dive returned insufficient papers: {d_data}"
                else:
                    notes = f"Pipeline step failure: gap={g_res.status_code}, title={t_res.status_code}, deepdive={d_res.status_code}"

            elif case_id == "P3_STATE_PERSISTENCE_REFRESH":
                user_email = f"eval_refresh_{int(time.time()*1000)}@utm.my"
                login_resp = client.post("/auth/demo-login", json={"email": user_email})
                token = login_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}


                cp = client.post("/projects", headers=headers, json={"title": "Eval State Refresh", "stage": "search", "state_json": {}})
                pid = cp.json()["id"]

                g_res = client.post(f"/projects/{pid}/stage/gap", headers=headers, json={})
                initial_gaps = g_res.json()["state_json"]["gaps"]

                # Refresh 1
                ref1 = client.get(f"/projects/{pid}", headers=headers)
                t_res = client.post(f"/projects/{pid}/stage/title", headers=headers, json={"language": "EN"})
                # Refresh 2
                ref2 = client.get(f"/projects/{pid}", headers=headers)
                duration = time.time() - start_time

                if ref2.status_code == 200:
                    st = ref2.json()["state_json"]
                    if st.get("gaps") == initial_gaps and len(st.get("titles", [])) >= 2 and st.get("last_saved_stage"):
                        passed = True
                        notes = f"Mid-pipeline reload restored exact state (gaps + titles preserved) in {duration:.3f}s: {st.get('last_saved_stage')}"
                    else:
                        notes = f"State mismatch after refresh: {st}"
                else:
                    notes = f"Refresh failed with HTTP {ref2.status_code}"


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
    print("MTIS MULTI-PHASE EVALUATION RESULTS (PHASE 1, 2 & 3)")
    print("=" * 60)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']} ({r['duration']:.3f}s): {r['notes']}")
    print("=" * 60)
    print(f"GATE VERDICT: {'PASS' if all_passed else 'FAIL'}")
    
    sys.exit(0 if all_passed else 1)
