"""
Router for System Owner / Administrator Management.
Enables user management, subscription plan upgrades, quota resets, and system stats.
All routes strictly enforced with require_admin.
"""
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Tenant, Project
from app.auth import require_admin
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


class AdminUserItem(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    role: str
    plan: str
    quota_remaining: int
    quota_reset_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserPlanRequest(BaseModel):
    plan: str = Field(..., description="Target subscription plan: free, pro, or enterprise")
    quota_remaining: Optional[int] = Field(None, description="Optional custom quota override")
    reset_quota: bool = Field(False, description="Whether to reset quota to the plan standard")


class CreateUserRequest(BaseModel):
    email: str = Field(..., min_length=3)
    name: str = Field(..., min_length=2)
    role: str = Field("student", description="Role: student or admin")
    plan: str = Field("free", description="Initial plan: free or pro")
    tenant_id: str = Field("tenant-demo-002", description="Target institution tenant ID")


class AdminStatsResponse(BaseModel):
    total_users: int
    students_count: int
    admins_count: int
    plans_breakdown: dict
    total_projects: int
    demo_mode: bool
    service_status: str


@router.get("/users", response_model=List[AdminUserItem])
def list_all_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all registered platform users across all tenants (Admin only)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.patch("/users/{user_id}/plan", response_model=AdminUserItem)
def update_user_plan_and_quota(
    user_id: str,
    req: UpdateUserPlanRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a user's subscription tier and adjust their quota balance (Admin only)."""
    valid_plans = {"free": 3, "pro": 99, "enterprise": 999}
    if req.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{req.plan}'. Must be one of: {list(valid_plans.keys())}",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    user.plan = req.plan
    if req.quota_remaining is not None:
        user.quota_remaining = max(0, req.quota_remaining)
    elif req.reset_quota or user.plan != req.plan:
        user.quota_remaining = valid_plans[req.plan]
        user.quota_reset_at = datetime.now(timezone.utc) + timedelta(days=1)

    db.commit()
    db.refresh(user)
    return user


@router.post("/users", response_model=AdminUserItem, status_code=status.HTTP_201_CREATED)
def onboard_user(
    req: CreateUserRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Onboard a new researcher or administrator to the platform (Admin only)."""
    existing = db.query(User).filter(User.email == req.email.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{req.email}' already exists.",
        )

    tenant = db.query(Tenant).filter(Tenant.id == req.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant '{req.tenant_id}' not found")

    plan_defaults = {"free": 3, "pro": 99, "enterprise": 999}
    initial_quota = plan_defaults.get(req.plan, 3)

    user_id = f"usr-{req.email.split('@')[0]}"
    new_user = User(
        id=user_id,
        tenant_id=req.tenant_id,
        name=req.name.strip(),
        email=req.email.strip().lower(),
        role="admin" if req.role == "admin" else "student",
        plan=req.plan if req.plan in plan_defaults else "free",
        quota_remaining=initial_quota,
        quota_reset_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/stats", response_model=AdminStatsResponse)
def get_system_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve platform usage metrics, user breakdowns, and system configuration (Admin only)."""
    users = db.query(User).all()
    total_projects = db.query(Project).count()

    students = sum(1 for u in users if u.role == "student")
    admins = sum(1 for u in users if u.role == "admin")
    
    plans: dict = {}
    for u in users:
        plans[u.plan] = plans.get(u.plan, 0) + 1

    return AdminStatsResponse(
        total_users=len(users),
        students_count=students,
        admins_count=admins,
        plans_breakdown=plans,
        total_projects=total_projects,
        demo_mode=getattr(settings, "DEMO_MODE", True),
        service_status="healthy",
    )
