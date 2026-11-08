"""
Acceptance Test Suite: 10-day free trial, then view-only until subscribed.

Acceptance Criteria:
1. A new student is on a trial; /auth/me shows access_status "trial" and trial_ends_at ~10 days ahead.
2. After the trial, AI routes (search, coach chat) return 402 TRIAL_ENDED; projects stay viewable.
3. A subscribed (pro) student has AI access again.
4. Admins and supervisors are never locked.
5. In DEMO_MODE (local offline evaluation) the trial is not enforced.
"""
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.config import settings
from app.database import SessionLocal
from app.models import User

CLIENT = TestClient(app)


@pytest.fixture(autouse=True)
def live_rules(monkeypatch):
    # Live-server rules, while demo-login stays available for test setup (development)
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "APP_ENV", "development")
    monkeypatch.setattr(settings, "TRIAL_DAYS", 10)


def _login(role: str = "student") -> tuple[dict, str]:
    email = f"trial_{role}_{uuid.uuid4().hex[:8]}@gmail.com"
    res = CLIENT.post("/auth/demo-login", json={"email": email, "name": "Trial Test", "role": role, "tenant_id": "tenant-independent"})
    assert res.status_code == 200, res.text
    body = res.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


def _age_account(user_id: str, days: int) -> None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.trial_start = datetime.now(timezone.utc) - timedelta(days=days)
        db.commit()


def _project(headers: dict) -> str:
    res = CLIENT.post("/projects", json={"title": "Trial project"}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_new_student_is_on_trial():
    headers, _ = _login()
    me = CLIENT.get("/auth/me", headers=headers).json()
    assert me["access_status"] == "trial"
    ends = datetime.fromisoformat(me["trial_ends_at"].replace("Z", "+00:00"))
    if ends.tzinfo is None:
        ends = ends.replace(tzinfo=timezone.utc)
    left = ends - datetime.now(timezone.utc)
    assert timedelta(days=9, hours=23) < left <= timedelta(days=10)


def test_expired_student_is_view_only():
    headers, user_id = _login()
    project_id = _project(headers)
    _age_account(user_id, 11)

    assert CLIENT.get("/auth/me", headers=headers).json()["access_status"] == "expired"

    search = CLIENT.post("/api/search", json={"query": "halal supply chain", "scope": "MY"}, headers=headers)
    assert search.status_code == 402
    assert "TRIAL_ENDED" in search.text

    chat = CLIENT.post(f"/api/projects/{project_id}/coach/chat", json={"message": "Help me", "lang": "en"}, headers=headers)
    assert chat.status_code == 402

    assert CLIENT.get("/projects", headers=headers).status_code == 200
    assert CLIENT.get(f"/projects/{project_id}", headers=headers).status_code == 200


def test_subscribed_student_has_access_again():
    headers, user_id = _login()
    _age_account(user_id, 30)
    admin_headers, _ = _login("admin")
    res = CLIENT.patch(f"/api/admin/users/{user_id}/plan", json={"plan": "pro"}, headers=admin_headers)
    assert res.status_code == 200, res.text

    assert CLIENT.get("/auth/me", headers=headers).json()["access_status"] == "subscribed"
    # Empty query: the access check passes, then input validation answers (no network call)
    res = CLIENT.post("/api/search", json={"query": "", "scope": "MY"}, headers=headers)
    assert res.status_code != 402


@pytest.mark.parametrize("role", ["admin", "supervisor"])
def test_staff_are_never_locked(role):
    headers, user_id = _login(role)
    _age_account(user_id, 100)
    assert CLIENT.get("/auth/me", headers=headers).json()["access_status"] == "staff"
    res = CLIENT.post("/api/search", json={"query": "", "scope": "MY"}, headers=headers)
    assert res.status_code != 402


def test_trial_not_enforced_in_demo_mode(monkeypatch):
    headers, user_id = _login()
    _age_account(user_id, 11)
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    res = CLIENT.post("/api/search", json={"query": "", "scope": "MY"}, headers=headers)
    assert res.status_code != 402
