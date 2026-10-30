"""
Acceptance Test Suite: Production Hardening (Render + Supabase deployment).

Acceptance Criteria:
1. A Supabase-signed ES256 token (verified via the project's JWKS) signs in and creates a student.
2. Tokens with the wrong audience, expired, or an unknown key id are rejected with 401.
3. In production (DEMO_MODE=false, APP_ENV=production) demo login is refused.
4. The global daily AI cap is atomic: limit 2 allows 2 calls then refuses; limit 0 means no cap.
5. When the global cap is reached, coach chat refuses with 429 before any HTTP call and refunds the chat slot.
6. ALLOWED_ORIGINS is parsed from a comma-separated list.
7. In production an unreachable DATABASE_URL fails loudly instead of falling back to SQLite.
"""
import sys
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt, jwk
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.config import settings, Settings
from app.database import SessionLocal, resolve_database_url
from app.models import AIDailyUsage
from app import auth as auth_module
from app.ai import usage_cap
from app.ai.provider import reset_mock_provider_handler
from app.ai.chat_limits import reset_chat_rate_limits

CLIENT = TestClient(app)
SUPABASE_URL = "https://testref.supabase.co"
KID = "test-key-1"

_private_key = ec.generate_private_key(ec.SECP256R1())
PRIVATE_PEM = _private_key.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
).decode()
PUBLIC_PEM = _private_key.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
).decode()
PUBLIC_JWK = {**jwk.construct(PUBLIC_PEM, "ES256").to_dict(), "kid": KID, "alg": "ES256", "use": "sig"}


@pytest.fixture
def supabase_jwks(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", SUPABASE_URL)
    monkeypatch.setattr(auth_module, "_fetch_supabase_jwks", lambda url: {"keys": [PUBLIC_JWK]})
    auth_module.clear_jwks_cache()
    yield
    auth_module.clear_jwks_cache()


def _supabase_token(sub: str, email: str, aud: str = "authenticated", exp_offset: int = 3600, kid: str = KID) -> str:
    now = int(time.time())
    claims = {
        "sub": sub,
        "email": email,
        "aud": aud,
        "iss": f"{SUPABASE_URL}/auth/v1",
        "iat": now,
        "exp": now + exp_offset,
        "role": "authenticated",
        "app_metadata": {"provider": "google"},
        "user_metadata": {"full_name": "Google Student"},
    }
    return jwt.encode(claims, PRIVATE_PEM, algorithm="ES256", headers={"kid": kid})


def test_supabase_es256_token_signs_in_and_creates_student(supabase_jwks):
    sub = str(uuid.uuid4())
    email = f"google_{sub[:8]}@gmail.com"
    res = CLIENT.get("/auth/me", headers={"Authorization": f"Bearer {_supabase_token(sub, email)}"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["id"] == sub
    assert body["email"] == email
    assert body["role"] == "student"
    # Private emails join Independent Researchers (university decided by email domain, server-side)
    assert body["tenant_id"] == "tenant-independent"


@pytest.mark.parametrize("kwargs", [
    {"aud": "anon"},
    {"exp_offset": -60},
    {"kid": "unknown-kid"},
])
def test_bad_supabase_tokens_rejected(supabase_jwks, kwargs):
    sub = str(uuid.uuid4())
    token = _supabase_token(sub, f"bad_{sub[:8]}@gmail.com", **kwargs)
    res = CLIENT.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_demo_login_refused_in_production(monkeypatch):
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "APP_ENV", "production")
    res = CLIENT.post("/auth/demo-login", json={
        "email": "attacker@example.com",
        "role": "admin",
        "tenant_id": "tenant-utm-001",
    })
    assert res.status_code == 403


def test_demo_login_refused_in_production_even_if_demo_mode_on(monkeypatch):
    # A misconfigured production (e.g. missing key making settings fall back to demo) must stay locked
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    monkeypatch.setattr(settings, "APP_ENV", "production")
    res = CLIENT.post("/auth/demo-login", json={
        "email": "attacker2@example.com",
        "role": "admin",
        "tenant_id": "tenant-utm-001",
    })
    assert res.status_code == 403


def test_global_ai_cap_is_enforced_per_day():
    test_day = date(2000, 1, 1) + timedelta(days=uuid.uuid4().int % 3000)
    with SessionLocal() as db:
        try:
            assert usage_cap.take_global_ai_slot(db, limit=2, day=test_day) is True
            assert usage_cap.take_global_ai_slot(db, limit=2, day=test_day) is True
            assert usage_cap.take_global_ai_slot(db, limit=2, day=test_day) is False
            assert usage_cap.take_global_ai_slot(db, limit=0, day=test_day) is True
        finally:
            db.query(AIDailyUsage).filter(AIDailyUsage.day == test_day).delete()
            db.commit()


def test_coach_refuses_when_global_cap_reached(monkeypatch):
    reset_mock_provider_handler()
    reset_chat_rate_limits()
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "sk-test-not-real")
    monkeypatch.setattr(settings, "CHAT_DAILY_LIMIT", 5)
    monkeypatch.setattr(usage_cap, "take_global_ai_slot", lambda db, limit, day=None: False)

    import httpx

    def no_network(*args, **kwargs):
        raise AssertionError("No HTTP call may be made when the global AI cap is reached")

    monkeypatch.setattr(httpx, "Client", no_network)

    login = CLIENT.post("/auth/demo-login", json={
        "email": f"cap_{uuid.uuid4().hex[:10]}@utm.my",
        "role": "student",
        "tenant_id": "tenant-utm-001",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    pid = CLIENT.post("/projects", json={"title": "Cap Test Project"}, headers=headers).json()["id"]

    res = CLIENT.post(f"/api/projects/{pid}/coach/chat", json={"message": "Need help"}, headers=headers)
    assert res.status_code == 429
    assert res.json()["error"] == "REFUSED_GLOBAL_QUOTA"

    hist = CLIENT.get(f"/api/projects/{pid}/coach/history", headers=headers).json()
    assert hist["chat_remaining"] == 5
    assert hist["history"] == []


def test_allowed_origins_parsed_from_comma_list():
    s = Settings(ALLOWED_ORIGINS=" https://mtis.netlify.app, http://localhost:3000 ,")
    assert s.allowed_origins_list == ["https://mtis.netlify.app", "http://localhost:3000"]
    assert Settings(ALLOWED_ORIGINS="*").allowed_origins_list == ["*"]


def test_production_database_never_falls_back_to_sqlite():
    unreachable = lambda url, timeout=0.5: False
    url = "postgresql://user:pw@db.example.com:5432/mtis"
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        resolve_database_url(url, production=True, check=unreachable)
    assert resolve_database_url(url, production=False, check=unreachable).startswith("sqlite")


def test_supabase_database_url_gets_sslmode():
    reachable = lambda url, timeout=0.5: True
    url = "postgresql://postgres.ref:pw@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    assert "sslmode=require" in resolve_database_url(url, production=True, check=reachable)
