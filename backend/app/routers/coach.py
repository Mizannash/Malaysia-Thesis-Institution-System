"""
Academic Coach Chat Router.
Enforces:
1. Signed-in user, tenant isolation and project ownership (same checks as the pipeline).
2. Off-policy filter before any model call.
3. Per-minute rate limit and a daily chat allowance separate from the generation quota.
4. Chat turns persisted to projects.state_json["coach_chat"].
"""
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config import settings
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import CoachChatRequest, CoachChatResponse, CoachHistoryResponse
from app.routers.pipeline import _get_isolated_project
from app.agents.coach_agent import coach_reply
from app.ai.provider import ChatProviderError
from app.ai.contract import AIContractError, AIPolicyRefusalError
from app.ai import chat_limits

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Academic Coach"])

MAX_SAVED_TURNS = 50


@router.get("/api/projects/{project_id}/coach/history", response_model=CoachHistoryResponse)
def get_coach_history(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_isolated_project(project_id, current_user, db)
    return CoachHistoryResponse(
        history=(project.state_json or {}).get("coach_chat", []),
        chat_remaining=chat_limits.remaining_today(
            db, current_user.tenant_id, current_user.id, settings.CHAT_DAILY_LIMIT
        ),
    )


@router.post("/api/projects/{project_id}/coach/chat", response_model=CoachChatResponse)
def send_coach_message(
    project_id: str,
    req: CoachChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_isolated_project(project_id, current_user, db)
    tenant_id, user_id = current_user.tenant_id, current_user.id
    history = list((project.state_json or {}).get("coach_chat", []))

    if not chat_limits.allow_per_minute(tenant_id, user_id, settings.CHAT_PER_MINUTE_LIMIT):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_RATE_LIMIT", "message": "Too many messages. Please wait a minute and try again."},
        )

    remaining = chat_limits.take_daily_slot(db, tenant_id, user_id, settings.CHAT_DAILY_LIMIT)
    if remaining is None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "REFUSED_CHAT_QUOTA", "message": "You have used today's coach messages. They reset at midnight (Malaysia time)."},
        )

    try:
        reply = coach_reply(project, current_user, req.message, history, lang=req.lang)
    except AIPolicyRefusalError as e:
        chat_limits.refund_daily_slot(db, tenant_id, user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REFUSED_POLICY", "message": e.user_message},
        )
    except (ChatProviderError, AIContractError):
        chat_limits.refund_daily_slot(db, tenant_id, user_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "COACH_UNAVAILABLE", "message": "The Academic Coach is unavailable right now. Please try again shortly."},
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    history.append({"role": "user", "content": req.message, "at": now_iso})
    history.append({"role": "assistant", "content": reply, "at": now_iso})
    new_state = dict(project.state_json or {})
    new_state["coach_chat"] = history[-MAX_SAVED_TURNS:]
    project.state_json = new_state
    flag_modified(project, "state_json")
    db.commit()

    return CoachChatResponse(reply=reply, chat_remaining=remaining, history=new_state["coach_chat"])
