"""Authentication and tenant isolation helpers."""
from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, set_tenant_context
from app.models import User, Tenant

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create local JWT token for session / demo mode."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.APP_SECRET, algorithm=ALGORITHM)


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer token from Supabase or Demo mode and return active User with tenant context."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    try:
        # 1. Try decoding with local APP_SECRET (Demo mode / local auth)
        payload = jwt.decode(token, settings.APP_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
    except JWTError:
        # 2. If Supabase JWT secret is configured, try Supabase token verification
        if settings.SUPABASE_JWT_SECRET:
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience="authenticated",
                )
                user_id = payload.get("sub")
                tenant_id = payload.get("app_metadata", {}).get("tenant_id", "tenant-utm-001")
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # If user does not exist yet (e.g. fresh Google sign-up in Supabase)
        email = payload.get("email", f"{user_id}@utm.my")
        name = payload.get("name", "New Student")
        tenant_id = tenant_id or "tenant-utm-001"

        user = User(
            id=user_id,
            tenant_id=tenant_id,
            name=name,
            email=email,
            role="student",
            plan="free",
            quota_remaining=3,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Auto-reset daily quota if quota_reset_at has passed
    now = datetime.now(timezone.utc)
    reset_at = user.quota_reset_at
    if reset_at is not None:
        if reset_at.tzinfo is None:
            reset_at = reset_at.replace(tzinfo=timezone.utc)
        if now >= reset_at:
            plan_defaults = {"free": 3, "pro": 99, "enterprise": 999}
            user.quota_remaining = plan_defaults.get(user.plan, 3)
            user.quota_reset_at = now + timedelta(days=1)
            db.commit()
            db.refresh(user)

    # CRITICAL MULTI-TENANCY ENFORCEMENT:
    # Set the session tenant context so PostgreSQL Row Level Security (RLS) is applied
    set_tenant_context(db, user.tenant_id)

    return user


def require_supervisor(current_user: User = Depends(get_current_user)) -> User:
    """Enforces supervisor/admin role for protected management routes."""
    if current_user.role not in ("supervisor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: supervisor or administrator privilege required",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Enforces administrator role for system owner management routes."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: administrator privilege required",
        )
    return current_user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional user authentication: returns active User if valid token provided, else None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return get_current_user(authorization=authorization, db=db)
    except Exception:
        return None
