"""Authentication and tenant isolation helpers."""
import logging
import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, set_tenant_context
from app.models import User, Tenant

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

# Supabase signing keys (JWKS), cached for an hour
SUPABASE_ASYMMETRIC_ALGORITHMS = ("ES256", "RS256")
JWKS_CACHE_SECONDS = 3600
_jwks_cache: Dict[str, Any] = {"keys": [], "fetched_at": 0.0}


def _fetch_supabase_jwks(supabase_url: str) -> Dict[str, Any]:
    url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(url, timeout=5.0)
    resp.raise_for_status()
    return resp.json()


def clear_jwks_cache():
    _jwks_cache["keys"] = []
    _jwks_cache["fetched_at"] = 0.0


def _supabase_signing_key(kid: Optional[str]) -> Optional[Dict[str, Any]]:
    """Finds the JWKS key by kid, refreshing the cache once if the kid is unknown or stale."""
    for attempt in range(2):
        stale = time.time() - _jwks_cache["fetched_at"] > JWKS_CACHE_SECONDS
        if attempt == 1 or stale or not _jwks_cache["keys"]:
            try:
                _jwks_cache["keys"] = _fetch_supabase_jwks(settings.SUPABASE_URL).get("keys", [])
                _jwks_cache["fetched_at"] = time.time()
            except Exception as exc:
                logger.warning("Could not fetch Supabase JWKS: %s", type(exc).__name__)
                return None
        for key in _jwks_cache["keys"]:
            if key.get("kid") == kid:
                return key
    return None


INDEPENDENT_TENANT_ID = "tenant-independent"


def tenant_for_new_user(payload: Dict[str, Any], db: Optional[Session] = None) -> str:
    """
    Chooses the institution for a new Supabase user, server-side:
    1. app_metadata.tenant_id (only admins / the server can write it)
    2. the TENANT_EMAIL_DOMAINS override (email domain or any of its subdomains)
    3. the institution list in the database; unknown .edu.my domains are created automatically
    4. otherwise the Independent Researchers tenant.
    user_metadata is user-writable and is never trusted for this.
    """
    admin_tenant = (payload.get("app_metadata") or {}).get("tenant_id")
    if admin_tenant:
        return admin_tenant
    email = (payload.get("email") or "").strip().lower()
    host = email.rpartition("@")[2]
    for domain, tenant_id in settings.tenant_email_domains.items():
        if host == domain or host.endswith("." + domain):
            return tenant_id
    if db is not None:
        from app.institutions import resolve_institution
        institution = resolve_institution(db, email)
        if institution:
            return institution
    return INDEPENDENT_TENANT_ID


def decode_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verifies a Supabase access token: asymmetric signing keys (ES256/RS256 via JWKS) with
    audience and issuer checks, or the legacy HS256 shared secret. Raises JWTError when invalid.
    """
    header = jwt.get_unverified_header(token)
    alg = header.get("alg")
    if alg in SUPABASE_ASYMMETRIC_ALGORITHMS and settings.SUPABASE_URL:
        key = _supabase_signing_key(header.get("kid"))
        if key is None:
            raise JWTError("Unknown Supabase signing key")
        return jwt.decode(
            token,
            key,
            algorithms=[alg],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1",
        )
    if alg == "HS256" and settings.SUPABASE_JWT_SECRET:
        return jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
    raise JWTError("Unsupported token")


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
        # 2. If Supabase is configured, verify the Supabase access token (JWKS or legacy secret)
        if settings.SUPABASE_URL or settings.SUPABASE_JWT_SECRET:
            try:
                payload = decode_supabase_token(token)
                user_id = payload.get("sub")
                tenant_id = (payload.get("app_metadata") or {}).get("tenant_id", "tenant-utm-001")
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
        # If user does not exist yet (fresh Supabase sign-up): the server decides the university
        email = payload.get("email") or f"{user_id}@unknown.invalid"
        user_meta = payload.get("user_metadata") or {}
        name = (user_meta.get("full_name") or payload.get("name") or email.split("@")[0]).strip()[:255]
        if "app_metadata" in payload or "user_metadata" in payload:
            tenant_id = tenant_for_new_user(payload, db)
        tenant_id = tenant_id or INDEPENDENT_TENANT_ID

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


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """Admins and supervisors only: tenant-wide settings such as the API key."""
    if current_user.role not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: staff privilege required",
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
