"""
Acceptance Test Suite: Stripe subscriptions (MTIS Pro).

Acceptance Criteria:
1. Checkout returns the Stripe URL with the right price, user reference, mode and return URLs;
   503 when payments are not configured; 401 when signed out.
2. A webhook with a missing or wrong signature is refused (400) and changes nothing.
3. checkout.session.completed makes an expired student Pro: AI routes stop answering 402.
4. customer.subscription.deleted returns them to free: the expired trial is locked again.
5. Replaying the same event gives the same result.
6. The billing portal needs a Stripe customer (400 otherwise).
"""
import hashlib
import hmac
import json
import sys
import time
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
from app import billing

CLIENT = TestClient(app)
FAKE_SECRET = "whsec_test_not_a_real_secret"
FAKE_PRICE = "price_test_mtis_pro"


@pytest.fixture
def stripe_calls(monkeypatch):
    """Configure fake Stripe settings and capture outgoing API calls (no network)."""
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "APP_ENV", "development")
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_not_a_real_key")
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", FAKE_SECRET)
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID", FAKE_PRICE)
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://mtis.example")
    calls = []

    def fake_post(path, data):
        calls.append((path, dict(data)))
        if path == "/v1/checkout/sessions":
            return {"id": "cs_test_1", "url": "https://checkout.stripe.com/c/pay/cs_test_1"}
        if path == "/v1/billing_portal/sessions":
            return {"url": "https://billing.stripe.com/p/session/test"}
        raise AssertionError(f"unexpected Stripe call {path}")

    monkeypatch.setattr(billing, "_stripe_post", fake_post)
    return calls


def _login() -> tuple[dict, str]:
    email = f"pay_{uuid.uuid4().hex[:8]}@gmail.com"
    res = CLIENT.post("/auth/demo-login", json={"email": email, "name": "Pay Test", "role": "student", "tenant_id": "tenant-independent"})
    assert res.status_code == 200, res.text
    body = res.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


def _expire_trial(user_id: str) -> None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.trial_start = datetime.now(timezone.utc) - timedelta(days=30)
        db.commit()


def _signed(event: dict, secret: str = FAKE_SECRET) -> tuple[bytes, dict]:
    payload = json.dumps(event).encode()
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return payload, {"Stripe-Signature": f"t={ts},v1={sig}", "Content-Type": "application/json"}


def _completed(user_id: str, customer: str, subscription: str) -> dict:
    return {"id": f"evt_{uuid.uuid4().hex[:10]}", "type": "checkout.session.completed", "data": {"object": {
        "object": "checkout.session", "client_reference_id": user_id, "customer": customer,
        "subscription": subscription, "mode": "subscription", "payment_status": "paid",
    }}}


def _subscription_event(kind: str, customer: str, subscription: str, sub_status: str) -> dict:
    return {"id": f"evt_{uuid.uuid4().hex[:10]}", "type": f"customer.subscription.{kind}", "data": {"object": {
        "object": "subscription", "id": subscription, "customer": customer, "status": sub_status,
    }}}


def _ai_status(headers: dict) -> int:
    # Empty query: passes the access check, then validation answers without any network call
    return CLIENT.post("/api/search", json={"query": "", "scope": "MY"}, headers=headers).status_code


def test_checkout_creates_subscription_session(stripe_calls):
    headers, user_id = _login()
    res = CLIENT.post("/api/billing/checkout", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["url"].startswith("https://checkout.stripe.com/")
    path, data = stripe_calls[-1]
    assert path == "/v1/checkout/sessions"
    assert data["mode"] == "subscription"
    assert data["line_items[0][price]"] == FAKE_PRICE
    assert data["client_reference_id"] == user_id
    assert data["success_url"].startswith("https://mtis.example/dashboard")


def test_checkout_unavailable_without_config_or_login(stripe_calls, monkeypatch):
    assert CLIENT.post("/api/billing/checkout").status_code == 401
    headers, _ = _login()
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", None)
    assert CLIENT.post("/api/billing/checkout", headers=headers).status_code == 503


def test_webhook_rejects_bad_signature(stripe_calls):
    headers, user_id = _login()
    _expire_trial(user_id)
    event = _completed(user_id, "cus_bad", "sub_bad")
    payload, hdrs = _signed(event, secret="whsec_wrong")
    assert CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs).status_code == 400
    assert CLIENT.post("/api/billing/webhook", content=payload, headers={"Content-Type": "application/json"}).status_code == 400
    assert CLIENT.get("/auth/me", headers=headers).json()["plan"] == "free"


def test_payment_unlocks_and_cancellation_locks_again(stripe_calls):
    headers, user_id = _login()
    _expire_trial(user_id)
    assert _ai_status(headers) == 402

    customer, sub = f"cus_{uuid.uuid4().hex[:8]}", f"sub_{uuid.uuid4().hex[:8]}"
    payload, hdrs = _signed(_completed(user_id, customer, sub))
    assert CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs).status_code == 200
    # Stripe may deliver the same event again
    assert CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs).status_code == 200

    me = CLIENT.get("/auth/me", headers=headers).json()
    assert me["plan"] == "pro"
    assert me["access_status"] == "subscribed"
    assert _ai_status(headers) != 402

    payload, hdrs = _signed(_subscription_event("deleted", customer, sub, "canceled"))
    assert CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs).status_code == 200
    me = CLIENT.get("/auth/me", headers=headers).json()
    assert me["plan"] == "free"
    assert me["access_status"] == "expired"
    assert _ai_status(headers) == 402


def test_unknown_event_is_acknowledged(stripe_calls):
    payload, hdrs = _signed({"id": "evt_x", "type": "invoice.created", "data": {"object": {}}})
    assert CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs).status_code == 200


def test_portal_needs_a_stripe_customer(stripe_calls):
    headers, user_id = _login()
    assert CLIENT.post("/api/billing/portal", headers=headers).status_code == 400

    payload, hdrs = _signed(_completed(user_id, f"cus_{uuid.uuid4().hex[:8]}", f"sub_{uuid.uuid4().hex[:8]}"))
    CLIENT.post("/api/billing/webhook", content=payload, headers=hdrs)
    res = CLIENT.post("/api/billing/portal", headers=headers)
    assert res.status_code == 200
    assert res.json()["url"].startswith("https://billing.stripe.com/")
