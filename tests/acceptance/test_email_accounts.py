"""
Acceptance Test Suite: MTIS email + password accounts (Supabase Auth).

Acceptance Criteria:
1. A university email domain (or its subdomain) places a new user in that university's tenant.
2. A private email (e.g. Gmail) places a new user in the Independent Researchers tenant.
3. A user cannot pick their own university through user_metadata (user-writable).
4. An admin-set app_metadata.tenant_id takes priority.
5. The sign-up name (user_metadata.full_name) becomes the user's name.
6. The Independent Researchers tenant always exists after start-up.
"""
import sys
import time
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt, jwk
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.config import settings
from app.database import SessionLocal, init_db
from app.models import Tenant
from app import auth as auth_module

CLIENT = TestClient(app)
SUPABASE_URL = "https://emailtest.supabase.co"
KID = "email-test-key"

_private_key = ec.generate_private_key(ec.SECP256R1())
PRIVATE_PEM = _private_key.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
).decode()
PUBLIC_PEM = _private_key.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
).decode()
PUBLIC_JWK = {**jwk.construct(PUBLIC_PEM, "ES256").to_dict(), "kid": KID, "alg": "ES256", "use": "sig"}


@pytest.fixture(autouse=True)
def supabase_jwks(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", SUPABASE_URL)
    monkeypatch.setattr(settings, "TENANT_EMAIL_DOMAINS", "utm.my:tenant-utm-001")
    monkeypatch.setattr(auth_module, "_fetch_supabase_jwks", lambda url: {"keys": [PUBLIC_JWK]})
    auth_module.clear_jwks_cache()
    yield
    auth_module.clear_jwks_cache()


def _me(email: str, user_metadata: dict = None, app_metadata: dict = None) -> dict:
    now = int(time.time())
    claims = {
        "sub": str(uuid.uuid4()),
        "email": email,
        "aud": "authenticated",
        "iss": f"{SUPABASE_URL}/auth/v1",
        "iat": now,
        "exp": now + 3600,
        "role": "authenticated",
        "app_metadata": {"provider": "email", **(app_metadata or {})},
        "user_metadata": user_metadata or {},
    }
    token = jwt.encode(claims, PRIVATE_PEM, algorithm="ES256", headers={"kid": KID})
    res = CLIENT.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    return res.json()


def _unique(local: str, domain: str) -> str:
    return f"{local}_{uuid.uuid4().hex[:8]}@{domain}"


def test_university_domain_and_subdomain_join_university_tenant():
    assert _me(_unique("siti", "utm.my"))["tenant_id"] == "tenant-utm-001"
    assert _me(_unique("ali", "graduate.utm.my"))["tenant_id"] == "tenant-utm-001"


def test_private_email_joins_independent_tenant():
    me = _me(_unique("aminah", "gmail.com"))
    assert me["tenant_id"] == "tenant-independent"
    assert me["role"] == "student"


def test_lookalike_domain_does_not_join_university():
    assert _me(_unique("fake", "notutm.my"))["tenant_id"] == "tenant-independent"


def test_user_cannot_pick_university_through_user_metadata():
    me = _me(_unique("sneaky", "gmail.com"), user_metadata={"tenant_id": "tenant-utm-001"})
    assert me["tenant_id"] == "tenant-independent"


def test_admin_set_app_metadata_tenant_takes_priority():
    me = _me(_unique("moved", "gmail.com"), app_metadata={"tenant_id": "tenant-demo-002"})
    assert me["tenant_id"] == "tenant-demo-002"


def test_signup_full_name_becomes_user_name():
    me = _me(_unique("nurul", "gmail.com"), user_metadata={"full_name": "Nurul Huda"})
    assert me["name"] == "Nurul Huda"
    fallback = _me("hafiz_" + uuid.uuid4().hex[:6] + "@yahoo.com")
    assert fallback["name"].lower().startswith("hafiz")


def test_independent_tenant_exists_after_startup():
    init_db()
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.id == "tenant-independent").first()
        assert tenant is not None
        assert tenant.name == "Independent Researchers"
