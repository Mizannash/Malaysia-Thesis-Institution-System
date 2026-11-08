"""
MTIS Pro subscriptions through Stripe (Checkout, Customer Portal, webhooks).

Stripe is called over its REST API with httpx; webhooks are verified with the
Stripe-Signature HMAC-SHA256 scheme. Keys come only from the environment
(STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_ID) and are never logged.
"""
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.access import access_status
from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import User

logger = logging.getLogger("mtis.billing")
router = APIRouter(prefix="/api/billing", tags=["Billing"])

STRIPE_API = "https://api.stripe.com"
SIGNATURE_TOLERANCE_SECONDS = 300
ACTIVE_STATUSES = {"active", "trialing", "past_due"}  # past_due: Stripe is still retrying the card
ENDED_STATUSES = {"canceled", "unpaid", "incomplete_expired"}


def _stripe_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """POST form data to the Stripe API. Raises HTTPException(502) on failure without leaking details."""
    try:
        res = httpx.post(f"{STRIPE_API}{path}", data=data, auth=(settings.STRIPE_SECRET_KEY or "", ""), timeout=20)
    except httpx.HTTPError:
        logger.warning("billing stripe_call path=%s outcome=network_error", path)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payment provider is unreachable. Please try again.")
    if res.status_code >= 400:
        logger.warning("billing stripe_call path=%s outcome=http_%s", path, res.status_code)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payment provider error. Please try again.")
    return res.json()


def _require_configured() -> None:
    if not (settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payments are not set up yet.")


def _frontend(path: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


@router.post("/checkout")
def create_checkout(current_user: User = Depends(get_current_user)):
    """Start a Stripe Checkout for the MTIS Pro monthly subscription."""
    _require_configured()
    if access_status(current_user) == "subscribed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already have MTIS Pro.")
    data = {
        "mode": "subscription",
        "line_items[0][price]": settings.STRIPE_PRICE_ID,
        "line_items[0][quantity]": "1",
        "client_reference_id": current_user.id,
        "metadata[user_id]": current_user.id,
        "subscription_data[metadata][user_id]": current_user.id,
        "success_url": _frontend("/dashboard?billing=success"),
        "cancel_url": _frontend("/pricing?billing=cancel"),
        "allow_promotion_codes": "true",
    }
    if current_user.stripe_customer_id:
        data["customer"] = current_user.stripe_customer_id
    else:
        data["customer_email"] = current_user.email
    session = _stripe_post("/v1/checkout/sessions", data)
    logger.info("billing checkout user=%s outcome=created", current_user.id)
    return {"url": session["url"]}


@router.post("/portal")
def open_portal(current_user: User = Depends(get_current_user)):
    """Stripe Customer Portal: cancel, change card, download invoices."""
    _require_configured()
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No subscription to manage yet.")
    session = _stripe_post("/v1/billing_portal/sessions", {
        "customer": current_user.stripe_customer_id,
        "return_url": _frontend("/dashboard"),
    })
    return {"url": session["url"]}


def verify_signature(payload: bytes, header: Optional[str], secret: str, now: Optional[float] = None) -> bool:
    """Stripe-Signature check: t=<timestamp>,v1=<hex hmac of '<t>.<payload>'>, within the tolerance."""
    if not header or not secret:
        return False
    parts: Dict[str, list] = {}
    for item in header.split(","):
        key, _, value = item.strip().partition("=")
        parts.setdefault(key, []).append(value)
    try:
        timestamp = int(parts.get("t", [""])[0])
    except ValueError:
        return False
    if abs((now or time.time()) - timestamp) > SIGNATURE_TOLERANCE_SECONDS:
        return False
    expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, sig) for sig in parts.get("v1", []))


def _apply_subscription(user: User, sub_status: str) -> None:
    user.subscription_status = sub_status
    if sub_status in ACTIVE_STATUSES:
        user.plan = "pro"
    elif sub_status in ENDED_STATUSES:
        user.plan = "free"


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Stripe events. Each is applied idempotently: a redelivered event gives the same result."""
    payload = await request.body()
    if not verify_signature(payload, request.headers.get("Stripe-Signature"), settings.STRIPE_WEBHOOK_SECRET or ""):
        logger.warning("billing webhook outcome=bad_signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    try:
        event = json.loads(payload)
        event_type = event.get("type", "")
        obj = (event.get("data") or {}).get("object") or {}
    except (ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    user: Optional[User] = None
    if event_type == "checkout.session.completed":
        user_id = obj.get("client_reference_id") or (obj.get("metadata") or {}).get("user_id")
        user = db.query(User).filter(User.id == user_id).first() if user_id else None
        if user is not None:
            user.stripe_customer_id = obj.get("customer") or user.stripe_customer_id
            user.stripe_subscription_id = obj.get("subscription") or user.stripe_subscription_id
            _apply_subscription(user, "active")
    elif event_type in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
        sub_id, customer_id = obj.get("id"), obj.get("customer")
        if sub_id:
            user = db.query(User).filter(User.stripe_subscription_id == sub_id).first()
        if user is None and customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user is not None:
            user.stripe_subscription_id = sub_id or user.stripe_subscription_id
            sub_status = "canceled" if event_type.endswith(".deleted") else (obj.get("status") or "")
            _apply_subscription(user, sub_status)
    else:
        return {"received": True}

    if user is None:
        logger.warning("billing webhook type=%s outcome=user_not_found", event_type)
        return {"received": True}
    db.commit()
    logger.info("billing webhook type=%s user=%s plan=%s outcome=applied", event_type, user.id, user.plan)
    return {"received": True}
