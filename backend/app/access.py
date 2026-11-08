"""
Who may use MTIS's AI features: the 10-day free trial, then view-only until subscribed.

access_status(user):
  staff       admins and supervisors (never locked)
  subscribed  plan pro / enterprise (set by Stripe in Step C, or by an admin)
  trial       within TRIAL_DAYS of trial_start
  expired     trial over, not subscribed: projects stay viewable, AI routes answer 402
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status

from app.auth import get_current_user, get_current_user_optional
from app.config import settings
from app.models import User

PAID_PLANS = ("pro", "enterprise")
TRIAL_ENDED_MESSAGE = (
    "Your 10-day free trial has ended. Subscribe to MTIS Pro to keep using AI features — "
    "your projects stay available to view and export."
)


def trial_ends_at(user: User) -> Optional[datetime]:
    start = user.trial_start or user.created_at
    if start is None:
        return None
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return start + timedelta(days=settings.TRIAL_DAYS)


def access_status(user: User, now: Optional[datetime] = None) -> str:
    if user.role in ("admin", "supervisor"):
        return "staff"
    if (user.plan or "").lower() in PAID_PLANS:
        return "subscribed"
    ends = trial_ends_at(user)
    now = now or datetime.now(timezone.utc)
    if ends is None or now < ends:
        return "trial"
    return "expired"


def require_ai_access(current_user: User = Depends(get_current_user)) -> User:
    """Route dependency for every AI feature. Not enforced in DEMO_MODE (local offline evaluation)."""
    if not settings.DEMO_MODE and access_status(current_user) == "expired":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"error": "TRIAL_ENDED", "message": TRIAL_ENDED_MESSAGE},
        )
    return current_user


def require_ai_access_if_signed_in(current_user: Optional[User] = Depends(get_current_user_optional)) -> Optional[User]:
    """For routes that also serve anonymous visitors (literature search, no paid model call)."""
    if current_user is not None:
        require_ai_access(current_user)
    return current_user
