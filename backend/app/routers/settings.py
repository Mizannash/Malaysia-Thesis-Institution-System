"""
Router for User Settings and Tenant API Key Management.
Allows users to securely save and toggle custom API keys encrypted via AES-256.
"""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, set_tenant_context
from app.models import User, Tenant
from app.auth import get_current_user
from app.config import settings
from app.security import encrypt_api_key, decrypt_api_key, mask_api_key

router = APIRouter(prefix="/api/settings", tags=["Settings & Keys"])


class ApiKeyUpdateRequest(BaseModel):
    llm_provider: Optional[str] = None
    provider: Optional[str] = None
    api_key: str = Field(..., min_length=5, description="Plaintext API key to be encrypted via AES-256")


class ApiKeyStatusResponse(BaseModel):
    llm_provider: str
    provider: str
    has_key: bool
    has_custom_key: bool
    key_preview: Optional[str] = None
    demo_mode: bool
    tenant_id: str
    tenant_name: str


class ToggleDemoModeRequest(BaseModel):
    demo_mode: bool


@router.get("/keys", response_model=ApiKeyStatusResponse)
def get_api_key_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves current tenant's API key status without exposing the secret."""
    set_tenant_context(db, current_user.tenant_id)
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    provider = tenant.llm_provider or getattr(settings, "LLM_PROVIDER", "deepseek")
    has_custom = bool(tenant.encrypted_api_key)
    preview = tenant.key_preview or (mask_api_key(settings.DEEPSEEK_API_KEY) if getattr(settings, "DEEPSEEK_API_KEY", None) else None)

    return ApiKeyStatusResponse(
        llm_provider=provider,
        provider=provider,
        has_key=has_custom,
        has_custom_key=has_custom,
        key_preview=preview,
        demo_mode=getattr(settings, "DEMO_MODE", True),
        tenant_id=tenant.id,
        tenant_name=tenant.name,
    )


@router.post("/keys")
def save_tenant_api_key(
    req: ApiKeyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Encrypts the supplied API key using AES-256-GCM and persists it to the tenant profile.
    The raw API key is immediately discarded from memory and never stored in plain text.
    """
    set_tenant_context(db, current_user.tenant_id)
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    provider = req.provider or req.llm_provider or "deepseek"
    encrypted_key = encrypt_api_key(req.api_key)
    preview = mask_api_key(req.api_key)

    tenant.llm_provider = provider
    tenant.encrypted_api_key = encrypted_key
    tenant.key_preview = preview
    db.commit()

    return {
        "status": "saved",
        "llm_provider": provider,
        "provider": provider,
        "has_key": True,
        "has_custom_key": True,
        "key_preview": preview,
        "tenant_id": tenant.id,
        "demo_mode": getattr(settings, "DEMO_MODE", True),
        "message": f"Successfully encrypted and saved {provider.title()} API key with AES-256.",
    }


@router.delete("/keys")
def delete_tenant_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes the stored encrypted API key for the current tenant."""
    set_tenant_context(db, current_user.tenant_id)
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.encrypted_api_key = None
    tenant.key_preview = None
    db.commit()

    return {
        "status": "deleted",
        "has_key": False,
        "has_custom_key": False,
        "key_preview": None,
        "tenant_id": tenant.id,
        "demo_mode": getattr(settings, "DEMO_MODE", True),
        "message": "Tenant custom API key removed. Falling back to DEMO_MODE or environment keys.",
    }


@router.post("/mode")
def toggle_demo_mode(
    req: ToggleDemoModeRequest,
    current_user: User = Depends(get_current_user),
):
    """Toggles global DEMO_MODE state for testing zero-key vs live API execution."""
    settings.DEMO_MODE = req.demo_mode
    return {
        "demo_mode": settings.DEMO_MODE,
        "message": f"DEMO_MODE set to {settings.DEMO_MODE}."
    }
