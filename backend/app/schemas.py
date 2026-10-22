"""Pydantic schemas for MTIS Backend."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "mtis-backend"


class TenantResponse(BaseModel):
    id: str
    name: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    role: str
    plan: str
    quota_remaining: int
    quota_reset_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=512)
    stage: str = Field("search", max_length=64)
    state_json: Dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    title: str
    stage: str
    state_json: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DemoLoginRequest(BaseModel):
    email: str
    role: Optional[str] = "student"
    tenant_id: Optional[str] = "tenant-utm-001"
    name: Optional[str] = None


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    tenant: TenantResponse
