"""
Acceptance Test Suite: MTIS for all Malaysian institutions.

Acceptance Criteria:
1. A known institution domain, or any of its subdomains, places a new user in that institution, and /auth/me
   returns the institution name.
2. Non-.edu.my institutions (usm.my, utm.my) are recognised too; UTM keeps its existing tenant id.
3. An unknown .edu.my domain creates one institution automatically; its subdomains join the same one.
4. Look-alike domains and private emails go to Independent Researchers.
5. Seeding the institution list is idempotent.
6. Only an admin can list and rename institutions.
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
SUPABASE_URL = "https://insttest.supabase.co"
KID = "inst-test-key"

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
    # No env override: the institution list in the database decides
    monkeypatch.setattr(settings, "TENANT_EMAIL_DOMAINS", "")
    monkeypatch.setattr(auth_module, "_fetch_supabase_jwks", lambda url: {"keys": [PUBLIC_JWK]})
    auth_module.clear_jwks_cache()
    init_db()
    yield
    auth_module.clear_jwks_cache()


def _me(email: str) -> dict:
    now = int(time.time())
    claims = {
        "sub": str(uuid.uuid4()),
        "email": email,
        "aud": "authenticated",
        "iss": f"{SUPABASE_URL}/auth/v1",
        "iat": now,
        "exp": now + 3600,
        "role": "authenticated",
        "app_metadata": {"provider": "email"},
        "user_metadata": {},
    }
    token = jwt.encode(claims, PRIVATE_PEM, algorithm="ES256", headers={"kid": KID})
    res = CLIENT.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    return res.json()


def _unique(domain: str) -> str:
    return f"s_{uuid.uuid4().hex[:8]}@{domain}"


def _demo_headers(role: str) -> dict:
    res = CLIENT.post("/auth/demo-login", json={
        "email": f"inst_{role}_{uuid.uuid4().hex[:8]}@utm.my", "name": "Inst Test", "role": role, "tenant_id": "tenant-utm-001",
    })
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_known_institution_and_subdomain_join_it_with_name():
    me = _me(_unique("um.edu.my"))
    assert me["tenant_id"] == "inst-um"
    assert "Universiti Malaya" in me["tenant_name"]
    assert _me(_unique("siswa.um.edu.my"))["tenant_id"] == "inst-um"


def test_non_edu_my_institutions_are_recognised():
    assert _me(_unique("usm.my"))["tenant_id"] == "inst-usm"
    assert _me(_unique("graduate.utm.my"))["tenant_id"] == "tenant-utm-001"


def test_unknown_edu_my_domain_creates_one_institution():
    label = "kolej" + uuid.uuid4().hex[:6]
    first = _me(_unique(f"{label}.edu.my"))
    assert first["tenant_id"] not in ("tenant-independent", "tenant-utm-001")
    second = _me(_unique(f"student.{label}.edu.my"))
    assert second["tenant_id"] == first["tenant_id"]
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.id == first["tenant_id"]).one()
        assert tenant.kind == "auto"
        assert tenant.email_domain == f"{label}.edu.my"


def test_lookalikes_and_private_emails_are_independent():
    for domain in ("um.edu.my.attacker.com", "notedu.my", "gmail.com", "edu.my"):
        assert _me(_unique(domain))["tenant_id"] == "tenant-independent", domain


def test_seeding_is_idempotent():
    init_db()
    init_db()
    with SessionLocal() as db:
        assert db.query(Tenant).filter(Tenant.email_domain == "um.edu.my").count() == 1
        assert db.query(Tenant).filter(Tenant.id == "inst-um").count() == 1


def test_only_admin_can_list_and_rename_institutions():
    _me(_unique("um.edu.my"))
    student = _demo_headers("student")
    assert CLIENT.get("/api/admin/institutions", headers=student).status_code == 403

    admin = _demo_headers("admin")
    res = CLIENT.get("/api/admin/institutions", headers=admin)
    assert res.status_code == 200
    um = next(i for i in res.json() if i["id"] == "inst-um")
    assert um["student_count"] >= 1
    assert um["email_domain"] == "um.edu.my"

    assert CLIENT.patch("/api/admin/institutions/inst-um", json={"name": "X"}, headers=student).status_code == 403
    renamed = CLIENT.patch("/api/admin/institutions/inst-um", json={"name": "Universiti Malaya (UM)", "short_name": "UM"}, headers=admin)
    assert renamed.status_code == 200
    assert renamed.json()["short_name"] == "UM"
