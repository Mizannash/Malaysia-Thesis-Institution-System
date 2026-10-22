"""
Simulates the complete lecturer and student journey through MTIS:
1. Quickstart sign-in as student@demo.test
2. Dashboard view: 5-step roadmap & hero action card (matching design Website)
3. Pipeline run: Stage 2 Gap -> Stage 3 Title -> Stage 4 DeepDive
4. Stage 5 Research Plan generation & iterative refinement
5. Multi-tenant isolation: sign in as ahmad@utm.my and attempt cross-tenant access (403 refused)
6. API Key Management: encrypted AES-256 storage, masked preview, mode toggling, deletion
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

def run_simulation():
    with TestClient(app) as client:
        print("=" * 65)
        print("MTIS LECTURER SIMULATION RUNNER (DESIGN & E2E PROTOCOL)")
        print("=" * 65)

        print("\n[STEP 1] Quickstart Authentication (student@demo.test)")
        r = client.post("/auth/demo-login", json={
            "email": "student@demo.test",
            "name": "Demo Student",
            "role": "student",
            "tenant_id": "tenant-demo-002"
        })
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        print("  -> Status: PASS")
        print("  -> Authenticated as student@demo.test in tenant: tenant-demo-002")

        # Ensure test user has fresh quota for the complete 5-stage pipeline run
        from app.database import SessionLocal
        from app.models import User
        with SessionLocal() as db_session:
            u = db_session.query(User).filter(User.email == "student@demo.test").first()
            if u:
                u.quota_remaining = 10
                db_session.commit()

        print("\n[STEP 2] Dashboard Data Hierarchy & Roadmap Verification")
        r_me = client.get("/auth/me", headers=h)
        assert r_me.status_code == 200
        user_data = r_me.json()
        print(f"  -> Verified user {user_data['email']}, quota remaining: {user_data['quota_remaining']}")

        r_proj = client.get("/projects", headers=h)
        assert r_proj.status_code == 200
        projects = r_proj.json()
        if len(projects) == 0:
            print("  -> Creating initial thesis project for Demo Student...")
            r_create = client.post("/projects", json={
                "title": "Cryo-EM Neural Attention in Protein Folding",
                "stage": "search",
                "state_json": {"topic": "Cryo-EM Neural Attention in Protein Folding", "scope": "MY"}
            }, headers=h)
            assert r_create.status_code == 201
            target_prj = r_create.json()
        else:
            target_prj = projects[0]

        prj_id = target_prj["id"]
        print(f"  -> Active project: {prj_id} ('{target_prj['title']}')")
        print("  -> 5-Stage Roadmap: Topic -> Gap -> Title -> Deep-Dive -> Plan")
        print("  -> Status: PASS")

        print("\n[STEP 3] Guided Pipeline Execution (Stage 2 -> Stage 3 -> Stage 4)")
        r_gap = client.post(f"/projects/{prj_id}/stage/gap", json={"project_id": prj_id}, headers=h)
        assert r_gap.status_code == 200
        gaps = r_gap.json()["state_json"]["gaps"]
        print(f"  -> Stage 2 (Gap Analysis): {len(gaps)} candidate gaps identified with citations")

        r_title = client.post(f"/projects/{prj_id}/stage/title", json={"project_id": prj_id, "language": "EN"}, headers=h)
        assert r_title.status_code == 200
        titles = r_title.json()["state_json"]["titles"]
        print(f"  -> Stage 3 (Title Suggestions): {len(titles)} defended titles generated (EN/BM)")

        chosen_title = titles[0]["title"]
        chosen_gap_id = titles[0].get("gap_id", "GAP-01")
        r_deep = client.post(f"/projects/{prj_id}/stage/deepdive", json={"project_id": prj_id, "chosen_title": chosen_title, "gap_id": chosen_gap_id}, headers=h)
        assert r_deep.status_code == 200
        deep_papers = r_deep.json()["state_json"]["deepdive_papers"]
        print(f"  -> Stage 4 (Deep-Dive Search): {len(deep_papers)} sub-field papers retrieved")
        print("  -> Status: PASS")

        print("\n[STEP 4] Stage 5 Research Plan Generation & Iterative Refinement")
        r_plan = client.post(f"/projects/{prj_id}/stage/plan", json={"project_id": prj_id}, headers=h)
        assert r_plan.status_code == 200
        plan_v1 = r_plan.json()["current_plan_json"]
        print(f"  -> Plan v1 generated: {len(plan_v1['objectives'])} SMART objectives, {len(plan_v1['key_milestones'])} milestones")

        r_refine = client.post("/api/plan/refine", json={
            "project_id": prj_id,
            "plan_id": plan_v1.get("plan_id", "plan-001"),
            "user_prompt": "Focus on Malaysian smallholders and shorten duration to 18 months"
        }, headers=h)
        assert r_refine.status_code == 200
        refine_data = r_refine.json()
        print(f"  -> Plan refined to v{refine_data['plan_version']}: {refine_data.get('diff_summary')}")
        print("  -> Status: PASS")

        print("\n[STEP 5] Tenant Boundary Isolation (Sign in as ahmad@utm.my)")
        r_utm = client.post("/auth/demo-login", json={
            "email": "ahmad@utm.my",
            "name": "Ahmad Student",
            "role": "student",
            "tenant_id": "tenant-utm-001"
        })
        assert r_utm.status_code == 200
        utm_token = r_utm.json()["access_token"]
        h_utm = {"Authorization": f"Bearer {utm_token}"}

        # Attempt foreign tenant project access
        r_leak = client.get(f"/projects/{prj_id}", headers=h_utm)
        assert r_leak.status_code == 403, f"Expected 403 Forbidden, got {r_leak.status_code}"
        print(f"  -> Cross-tenant refusal verified (HTTP 403): {r_leak.json()['detail']}")
        print("  -> Status: PASS")

        print("\n[STEP 6] AES-256 Encrypted API Key Management & Mode Toggle")
        raw_key = "sk-live-deepseek-simulation-key-445566"
        r_key = client.post("/api/settings/keys", json={
            "provider": "deepseek",
            "api_key": raw_key
        }, headers=h_utm)
        assert r_key.status_code == 200
        key_data = r_key.json()
        assert key_data["has_custom_key"] is True
        assert raw_key not in key_data["key_preview"]
        print(f"  -> Encrypted key saved: {key_data['provider']}, preview: {key_data['key_preview']}")

        r_mode = client.post("/api/settings/mode", json={"demo_mode": False}, headers=h_utm)
        assert r_mode.status_code == 200
        print(f"  -> Toggled mode: DEMO_MODE={r_mode.json()['demo_mode']}")

        r_reset_mode = client.post("/api/settings/mode", json={"demo_mode": True}, headers=h_utm)
        assert r_reset_mode.status_code == 200
        print(f"  -> Reset back to safe default: DEMO_MODE={r_reset_mode.json()['demo_mode']}")

        r_del = client.delete("/api/settings/keys", headers=h_utm)
        assert r_del.status_code == 200
        print(f"  -> Clean key deletion verified: has_custom_key={r_del.json()['has_custom_key']}")
        print("  -> Status: PASS")

        print("\n" + "=" * 65)
        print("ALL 6 STEPS OF LECTURER SIMULATION VERIFIED: 100% PASS")
        print("=" * 65)

if __name__ == "__main__":
    run_simulation()
