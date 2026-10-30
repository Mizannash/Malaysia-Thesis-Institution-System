"""
Academic Coach chat limits.
1. Per-minute window per person, keyed by tenant and user (in-process; move to Redis when hosted).
2. Daily allowance per person, taken and refunded with single atomic UPDATE statements.
Both are separate from the generation quota (users.quota_remaining).
"""
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone, date
from typing import Deque, Dict, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

MALAYSIA_TZ = timezone(timedelta(hours=8))

_window: Dict[str, Deque[float]] = {}
_window_lock = threading.Lock()


def malaysia_today() -> date:
    return datetime.now(MALAYSIA_TZ).date()


def reset_chat_rate_limits():
    """Clear the per-minute windows (test hook)."""
    with _window_lock:
        _window.clear()


def allow_per_minute(tenant_id: str, user_id: str, limit: int, now: Optional[float] = None) -> bool:
    """Sliding 60-second window. Records the attempt only when it is allowed."""
    now = now if now is not None else time.monotonic()
    key = f"{tenant_id}:{user_id}"
    with _window_lock:
        hits = _window.setdefault(key, deque())
        while hits and now - hits[0] >= 60:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


def take_daily_slot(db: Session, tenant_id: str, user_id: str, limit: int) -> Optional[int]:
    """
    Atomically uses one chat from today's allowance.
    Returns the number left after this message, or None when the allowance is used up.
    """
    today = malaysia_today()
    result = db.execute(
        text(
            "UPDATE users SET "
            "chat_count = CASE WHEN chat_count_date = :today THEN chat_count + 1 ELSE 1 END, "
            "chat_count_date = :today "
            "WHERE id = :uid AND tenant_id = :tid "
            "AND (chat_count_date IS NULL OR chat_count_date <> :today OR chat_count < :limit)"
        ),
        {"today": today, "uid": user_id, "tid": tenant_id, "limit": limit},
    )
    db.commit()
    if result.rowcount != 1:
        return None
    used = db.execute(
        text("SELECT chat_count FROM users WHERE id = :uid AND tenant_id = :tid"),
        {"uid": user_id, "tid": tenant_id},
    ).scalar() or 0
    return max(0, limit - used)


def refund_daily_slot(db: Session, tenant_id: str, user_id: str):
    """Gives back a slot taken for a message the model never answered."""
    db.execute(
        text(
            "UPDATE users SET chat_count = chat_count - 1 "
            "WHERE id = :uid AND tenant_id = :tid AND chat_count_date = :today AND chat_count > 0"
        ),
        {"today": malaysia_today(), "uid": user_id, "tid": tenant_id},
    )
    db.commit()


def remaining_today(db: Session, tenant_id: str, user_id: str, limit: int) -> int:
    row = db.execute(
        text("SELECT chat_count, chat_count_date FROM users WHERE id = :uid AND tenant_id = :tid"),
        {"uid": user_id, "tid": tenant_id},
    ).first()
    if not row or row[1] is None or str(row[1]) != str(malaysia_today()):
        return limit
    return max(0, limit - (row[0] or 0))
