"""Authentication routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, Tenant
from app.schemas import (
    UserResponse,
    TenantResponse,
    DemoLoginRequest,
    AuthTokenResponse,
)
from app.auth import get_current_user, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserResponse)
def get_authenticated_user(current_user: User = Depends(get_current_user)):
    """Retrieve profile and tenant details of the currently signed-in user."""
    return current_user


@router.get("/tenants", response_model=List[TenantResponse])
def list_tenants(db: Session = Depends(get_db)):
    """List available institutions/tenants for onboarding and testing."""
    return db.query(Tenant).all()


@router.post("/demo-login", response_model=AuthTokenResponse)
def demo_login(req: DemoLoginRequest, db: Session = Depends(get_db)):
    """Quick login for DEMO_MODE, automated testing, and marker evaluation."""
    if not settings.DEMO_MODE and not settings.APP_ENV == "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo login is disabled in production environments.",
        )

    # Find existing user or seed on the fly
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        tenant = db.query(Tenant).filter(Tenant.id == req.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail=f"Tenant {req.tenant_id} not found")

        base_id = f"usr-{req.email.split('@')[0]}"
        user_id = base_id
        suffix = 1
        while db.query(User).filter(User.id == user_id).first():
            user_id = f"{base_id}-{suffix}"
            suffix += 1
        user = User(
            id=user_id,
            tenant_id=req.tenant_id,
            name=req.name or req.email.split("@")[0].title(),
            email=req.email,
            role=req.role or "student",
            plan="free" if req.role == "student" else "pro",
            quota_remaining=3 if req.role == "student" else 99,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Ensure standard demo accounts always have active quota for smooth testing
    if user.email in ("student@demo.test", "ahmad@utm.my", "admin@demo.test") and user.quota_remaining < 5:
        user.quota_remaining = 20 if user.role == "student" else 99
        db.commit()
        db.refresh(user)

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "tenant_id": user.tenant_id,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "tenant": tenant,
    }


@router.post("/refill-quota")
def refill_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Refills quota balance for the current user (convenience for demo evaluation)."""
    current_user.quota_remaining = 20 if current_user.role == "student" else 99
    db.commit()
    db.refresh(current_user)
    return {
        "message": "Quota refilled successfully",
        "quota_remaining": current_user.quota_remaining
    }
