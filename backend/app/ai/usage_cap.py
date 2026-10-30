"""
Platform-wide daily cap on paid AI calls (protects the DeepSeek budget).
Checked only right before a live provider HTTP call; demo mode and test mocks never count.
"""
from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.chat_limits import malaysia_today

GLOBAL_CAP_MESSAGE = "MTIS has reached today's AI limit. Please try again tomorrow."


def take_global_ai_slot(db: Session, limit: int, day: Optional[date] = None) -> bool:
    """Atomically uses one call from today's platform-wide allowance. limit <= 0 means no cap."""
    if limit <= 0:
        return True
    day = day or malaysia_today()
    try:
        db.execute(text("INSERT INTO ai_daily_usage (day, calls) VALUES (:day, 0)"), {"day": day})
        db.commit()
    except IntegrityError:
        db.rollback()
    result = db.execute(
        text("UPDATE ai_daily_usage SET calls = calls + 1 WHERE day = :day AND calls < :limit"),
        {"day": day, "limit": limit},
    )
    db.commit()
    return result.rowcount == 1


def check_global_ai_cap():
    """Raises AIQuotaExceededError when today's platform-wide AI allowance is used up."""
    from app.config import settings
    from app.database import SessionLocal
    from app.ai.contract import AIQuotaExceededError

    with SessionLocal() as db:
        if not take_global_ai_slot(db, settings.AI_DAILY_GLOBAL_LIMIT):
            raise AIQuotaExceededError(GLOBAL_CAP_MESSAGE)
