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
    plan_id: Optional[str] = None
    current_plan_json: Optional[Dict[str, Any]] = None
    plan_version: int = 0
    last_refined_at: Optional[datetime] = None
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


class Paper(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    source: str = "openalex"  # "openalex" | "utm"
    citation_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    query: str
    scope: str = "MY"  # "MY" | "INT"


class SearchResponse(BaseModel):
    query: str
    scope: str
    total: int
    papers: list[Paper]
    sources: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[Any] = None


class GapItem(BaseModel):
    gap_id: str
    description: str
    supporting_paper_ids: list[str] = Field(default_factory=list)


class GapAnalysisResponse(BaseModel):
    gaps: list[GapItem]


class TitleItem(BaseModel):
    title: str
    language: str = "EN"  # "EN" | "BM"
    gap_id: str
    rationale: Optional[str] = None


class TitleSuggestionsResponse(BaseModel):
    titles: list[TitleItem]


class DeepDiveResponse(BaseModel):
    chosen_title: str
    gap_id: str
    papers: list[Paper]


class GapAnalysisRequest(BaseModel):
    project_id: Optional[str] = None
    papers: Optional[list[Paper]] = None


class TitleSuggestionsRequest(BaseModel):
    project_id: Optional[str] = None
    gap_id: Optional[str] = None
    gap: Optional[GapItem] = None
    language: Optional[str] = "EN"


class DeepDiveRequest(BaseModel):
    project_id: Optional[str] = None
    chosen_title: str
    gap_id: Optional[str] = "GAP-01"


class ResearchObjective(BaseModel):
    objective_id: str
    text: str


class PlanMilestone(BaseModel):
    milestone_id: str
    title: str
    description: str
    target_month: str


class PlanResource(BaseModel):
    category: str
    item: str
    justification: Optional[str] = None


class TimelinePhase(BaseModel):
    phase_name: str
    months: str
    tasks: list[str] = Field(default_factory=list)


class StructuredPlan(BaseModel):
    plan_id: str
    title: str
    gap_id: Optional[str] = None
    objectives: list[ResearchObjective] = Field(default_factory=list)
    key_milestones: list[PlanMilestone] = Field(default_factory=list)
    necessary_resources: list[PlanResource] = Field(default_factory=list)
    timeline: list[TimelinePhase] = Field(default_factory=list)
    methodology_summary: Optional[str] = None
    version: int = 1


class PlanGenerateRequest(BaseModel):
    project_id: Optional[str] = None
    custom_instructions: Optional[str] = None


class PlanRefineRequest(BaseModel):
    plan_id: Optional[str] = None
    project_id: Optional[str] = None
    user_prompt: str


class PlanRefineResponse(BaseModel):
    project_id: str
    plan_id: str
    plan_version: int
    plan: StructuredPlan
    diff_summary: Optional[str] = None


