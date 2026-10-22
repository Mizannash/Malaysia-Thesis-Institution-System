"""Acceptance Tests: System Owner / Administrator Management (Admin Router)

Verifies:
- Role privilege enforcement: Only 'admin' role can access /api/admin routes (students rejected with 403).
- System KPIs and platform overview metrics (/api/admin/stats).
- User directory listing across tenants (/api/admin/users).
- Subscription tier management & quota balance updates (/api/admin/users/{user_id}/plan).
- Academic researcher onboarding (/api/admin/users) with conflict detection.
- Quota auto-reset mechanism when quota_reset_at passes.
"""
import time
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.database import SessionLocal
from app.models import User, Tenant


@pytest.fixture
def client():
    return TestClient(app)


def get_token_for(client: TestClient, email: str, role: str, tenant_id: str = "tenant-demo-002", name: str = "Test User") -> str:
    res = client.post("/auth/demo-login", json={
        "email": email,
        "name": name,
        "role": role,
        "tenant_id": tenant_id
    })
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def test_admin_route_privilege_enforcement(client):
    """Students and unauthenticated requests are strictly refused access to admin routes."""
    # 1. Unauthenticated request -> 401
    r_unauth = client.get("/api/admin/users")
    assert r_unauth.status_code == 401

    # 2. Student token -> 403 Forbidden
    student_token = get_token_for(client, "student@demo.test", "student")
    r_forbidden = client.get("/api/admin/users", headers={"Authorization": f"Bearer {student_token}"})
    assert r_forbidden.status_code == 403
    assert "administrator privilege required" in r_forbidden.json()["detail"]

    # 3. Admin token -> 200 OK
    admin_token = get_token_for(client, "admin@demo.test", "admin")
    r_ok = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r_ok.status_code == 200
    assert isinstance(r_ok.json(), list)


def test_admin_system_stats(client):
    """Admin retrieves platform aggregate metrics and system configuration."""
    admin_token = get_token_for(client, "admin@demo.test", "admin")
    res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    stats = res.json()

    assert "total_users" in stats
    assert stats["total_users"] > 0
    assert "students_count" in stats
    assert "admins_count" in stats
    assert stats["admins_count"] >= 1
    assert "plans_breakdown" in stats
    assert isinstance(stats["plans_breakdown"], dict)
    assert "total_projects" in stats
    assert stats["service_status"] == "healthy"


def test_admin_user_directory_and_plan_update(client):
    """Admin can query user directory and update subscription plans and quota balances."""
    admin_token = get_token_for(client, "admin@demo.test", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Fetch user list
    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 200
    users = res.json()
    assert len(users) > 0

    target_user = next((u for u in users if u["email"] == "student@demo.test"), users[0])
    target_id = target_user["id"]

    # 2. Upgrade to Pro plan
    r_pro = client.patch(f"/api/admin/users/{target_id}/plan", json={"plan": "pro", "reset_quota": True}, headers=headers)
    assert r_pro.status_code == 200
    updated_user = r_pro.json()
    assert updated_user["plan"] == "pro"
    assert updated_user["quota_remaining"] == 99

    # 3. Custom Quota Override
    r_override = client.patch(f"/api/admin/users/{target_id}/plan", json={"plan": "pro", "quota_remaining": 150}, headers=headers)
    assert r_override.status_code == 200
    assert r_override.json()["quota_remaining"] == 150

    # 4. Downgrade to Free plan
    r_free = client.patch(f"/api/admin/users/{target_id}/plan", json={"plan": "free", "reset_quota": True}, headers=headers)
    assert r_free.status_code == 200
    assert r_free.json()["plan"] == "free"
    assert r_free.json()["quota_remaining"] == 3

    # 5. Invalid plan rejection -> 400
    r_invalid = client.patch(f"/api/admin/users/{target_id}/plan", json={"plan": "ultra_vip"}, headers=headers)
    assert r_invalid.status_code == 400
    assert "Invalid plan" in r_invalid.json()["detail"]

    # 6. Non-existent user -> 404
    r_404 = client.patch("/api/admin/users/usr-does-not-exist-9999/plan", json={"plan": "pro"}, headers=headers)
    assert r_404.status_code == 404


def test_admin_onboard_user_and_conflict_handling(client):
    """Admin can onboard a new academic user, with duplicate email conflict prevention."""
    admin_token = get_token_for(client, "admin@demo.test", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    unique_email = f"researcher_{int(time.time())}@utm.my"
    payload = {
        "email": unique_email,
        "name": "Dr. Nurul Izzah",
        "role": "student",
        "plan": "pro",
        "tenant_id": "tenant-utm-001"
    }

    # 1. Successful onboard
    res = client.post("/api/admin/users", json=payload, headers=headers)
    assert res.status_code == 201
    created = res.json()
    assert created["email"] == unique_email
    assert created["name"] == "Dr. Nurul Izzah"
    assert created["role"] == "student"
    assert created["plan"] == "pro"
    assert created["quota_remaining"] == 99
    assert created["tenant_id"] == "tenant-utm-001"

    # 2. Duplicate email rejection -> 409 Conflict
    res_dup = client.post("/api/admin/users", json=payload, headers=headers)
    assert res_dup.status_code == 409
    assert "already exists" in res_dup.json()["detail"]

    # 3. Non-existent tenant rejection -> 404
    invalid_tenant_payload = {**payload, "email": f"diff_{int(time.time())}@utm.my", "tenant_id": "non-existent-tenant-999"}
    res_tenant_404 = client.post("/api/admin/users", json=invalid_tenant_payload, headers=headers)
    assert res_tenant_404.status_code == 404
    assert "not found" in res_tenant_404.json()["detail"]


def test_user_quota_auto_reset_on_expiration(client):
    """User quota automatically replenishes if current time is past quota_reset_at."""
    unique_email = f"quota_test_{int(time.time())}@demo.test"
    token = get_token_for(client, unique_email, "student")
    headers = {"Authorization": f"Bearer {token}"}

    # Artificially exhaust quota and set reset time in the past
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        user.quota_remaining = 0
        user.quota_reset_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.commit()

    # Calling /auth/me triggers get_current_user auto-reset
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200
    user_data = res.json()

    assert user_data["quota_remaining"] == 3
    assert user_data["quota_reset_at"] is not None
    # Verify quota_reset_at was pushed to the future
    reset_dt = datetime.fromisoformat(user_data["quota_reset_at"].replace("Z", "+00:00"))
    assert reset_dt > datetime.now(timezone.utc)
