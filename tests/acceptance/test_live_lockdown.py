"""
Acceptance Test Suite: Live-site lockdown of demo-only controls.

Acceptance Criteria:
1. In production a student cannot refill their AI quota (403); outside production refill still works.
2. A student cannot switch the server's DEMO_MODE (403); in production even an admin cannot.
3. A student cannot read, save or delete the tenant's API key (403).
4. A supervisor can still save a tenant key outside production.
"""
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.config import settings

CLIENT = TestClient(app)


def _headers(role: str, tenant: str = "tenant-utm-001") -> dict:
    email = f"lock_{role}_{uuid.uuid4().hex[:8]}@utm.my"
    res = CLIENT.post("/auth/demo-login", json={"email": email, "name": "Lock Test", "role": role, "tenant_id": tenant})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_student_cannot_refill_quota_in_production(monkeypatch):
    headers = _headers("student")
    monkeypatch.setattr(settings, "APP_ENV", "production")
    res = CLIENT.post("/auth/refill-quota", headers=headers)
    assert res.status_code == 403


def test_refill_still_works_outside_production():
    headers = _headers("student")
    res = CLIENT.post("/auth/refill-quota", headers=headers)
    assert res.status_code == 200
    assert res.json()["quota_remaining"] > 0


def test_student_cannot_toggle_demo_mode():
    headers = _headers("student")
    before = settings.DEMO_MODE
    res = CLIENT.post("/api/settings/mode", json={"demo_mode": not before}, headers=headers)
    assert res.status_code == 403
    assert settings.DEMO_MODE == before


def test_admin_cannot_toggle_demo_mode_in_production(monkeypatch):
    headers = _headers("admin")
    monkeypatch.setattr(settings, "APP_ENV", "production")
    before = settings.DEMO_MODE
    res = CLIENT.post("/api/settings/mode", json={"demo_mode": not before}, headers=headers)
    assert res.status_code == 403
    assert settings.DEMO_MODE == before


def test_student_cannot_manage_tenant_key():
    headers = _headers("student", tenant="tenant-independent")
    assert CLIENT.get("/api/settings/keys", headers=headers).status_code == 403
    res = CLIENT.post("/api/settings/keys", json={"provider": "deepseek", "api_key": "sk-attacker-key-123456"}, headers=headers)
    assert res.status_code == 403
    assert CLIENT.delete("/api/settings/keys", headers=headers).status_code == 403


def test_supervisor_can_save_tenant_key_outside_production():
    headers = _headers("supervisor")
    res = CLIENT.post("/api/settings/keys", json={"provider": "deepseek", "api_key": "sk-supervisor-key-abcdef"}, headers=headers)
    assert res.status_code == 200
    CLIENT.delete("/api/settings/keys", headers=headers)
