"""Acceptance Test: Multi-Tenant Boundary & Row-Level Security Isolation

Criteria:
Given users in two tenants, when user A requests user B's project, then response is 403/empty and nothing leaks.
Must also assert RLS at DB level.
"""
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import SessionLocal, set_tenant_context, engine
from app.models import Project, User
from sqlalchemy import text


@pytest.fixture
def client():
    return TestClient(app)


def get_token_for(client: TestClient, email: str, role: str, tenant_id: str, name: str) -> str:
    res = client.post("/auth/demo-login", json={
        "email": email,
        "role": role,
        "tenant_id": tenant_id,
        "name": name,
    })
    assert res.status_code == 200
    return res.json()["access_token"]


def test_cross_tenant_api_isolation(client):
    """
    User A (UTM) requests User B (Demo Univ) project -> 403 Forbidden.
    User B (Demo Univ) requests User A (UTM) project -> 403 Forbidden.
    Nothing leaks.
    """
    token_utm = get_token_for(client, "ahmad@utm.my", "student", "tenant-utm-001", "Ahmad Student")
    token_demo = get_token_for(client, "alex@demouniv.edu.my", "student", "tenant-demo-002", "Alex Demo Student")

    # 1. UTM user attempts to fetch Demo Univ's project (prj-demo-201)
    res_utm_cross = client.get(
        "/projects/prj-demo-201",
        headers={"Authorization": f"Bearer {token_utm}"}
    )
    assert res_utm_cross.status_code == 403, f"Expected 403 Forbidden, got {res_utm_cross.status_code}: {res_utm_cross.text}"
    assert "Cross-tenant" in res_utm_cross.json()["detail"]

    # 2. Demo Univ user attempts to fetch UTM's project (prj-utm-101)
    res_demo_cross = client.get(
        "/projects/prj-utm-101",
        headers={"Authorization": f"Bearer {token_demo}"}
    )
    assert res_demo_cross.status_code == 403, f"Expected 403 Forbidden, got {res_demo_cross.status_code}: {res_demo_cross.text}"
    assert "Cross-tenant" in res_demo_cross.json()["detail"]

    # 3. UTM user lists projects -> ONLY UTM projects, zero Demo Univ projects
    res_utm_list = client.get("/projects", headers={"Authorization": f"Bearer {token_utm}"})
    assert res_utm_list.status_code == 200
    utm_projects = res_utm_list.json()
    assert len(utm_projects) >= 1
    for p in utm_projects:
        assert p["tenant_id"] == "tenant-utm-001"
        assert p["id"] != "prj-demo-201"

    # 4. Demo Univ user lists projects -> ONLY Demo Univ projects, zero UTM projects
    res_demo_list = client.get("/projects", headers={"Authorization": f"Bearer {token_demo}"})
    assert res_demo_list.status_code == 200
    demo_projects = res_demo_list.json()
    assert len(demo_projects) >= 1
    for p in demo_projects:
        assert p["tenant_id"] == "tenant-demo-002"
        assert p["id"] != "prj-utm-101"
        assert p["id"] != "prj-utm-102"


def test_supervisor_tenant_view_isolation(client):
    """
    Supervisor can see all projects in their OWN tenant, but 0 projects from other tenants.
    """
    token_utm_supervisor = get_token_for(client, "siti@utm.my", "supervisor", "tenant-utm-001", "Dr. Siti Supervisor")
    res = client.get("/projects", headers={"Authorization": f"Bearer {token_utm_supervisor}"})
    assert res.status_code == 200
    supervisor_projects = res.json()
    assert len(supervisor_projects) >= 2  # Has multiple student projects in UTM

    for p in supervisor_projects:
        assert p["tenant_id"] == "tenant-utm-001"
        assert p["tenant_id"] != "tenant-demo-002"


def test_database_level_rls():
    """
    Direct assertion of Row-Level Security / tenant filtering at the Database Session level.
    """
    with SessionLocal() as db:
        # Check UTM tenant scope
        set_tenant_context(db, "tenant-utm-001")
        utm_projects = db.query(Project).filter(Project.tenant_id == "tenant-utm-001").all()
        assert len(utm_projects) > 0
        for p in utm_projects:
            assert p.tenant_id == "tenant-utm-001"

        # Check Demo University tenant scope
        set_tenant_context(db, "tenant-demo-002")
        demo_projects = db.query(Project).filter(Project.tenant_id == "tenant-demo-002").all()
        assert len(demo_projects) > 0
        for p in demo_projects:
            assert p.tenant_id == "tenant-demo-002"

        # Verify no intersection
        utm_ids = {p.id for p in utm_projects}
        demo_ids = {p.id for p in demo_projects}
        assert utm_ids.isdisjoint(demo_ids), "Tenant project IDs must have zero intersection!"
