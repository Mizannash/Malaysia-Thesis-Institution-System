import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database import get_db, set_tenant_context
from app.models import Project, User
from app.schemas import ProjectResponse, ProjectCreate
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[str] = None
    state_json: Optional[Dict[str, Any]] = None
    current_plan_json: Optional[Dict[str, Any]] = None


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List projects with strict tenant isolation.
    - Students see only their own projects within their tenant.
    - Supervisors see all projects within their tenant ("All Projects (this tenant)" view).
    """
    set_tenant_context(db, current_user.tenant_id)

    query = db.query(Project).filter(Project.tenant_id == current_user.tenant_id)

    if current_user.role == "student":
        query = query.filter(Project.user_id == current_user.id)

    return query.order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    req: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new research project tied to the authenticated user and tenant."""
    set_tenant_context(db, current_user.tenant_id)

    project = Project(
        id=f"prj-{uuid.uuid4().hex[:8]}",
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        title=req.title,
        stage=req.stage,
        state_json=req.state_json,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single project by ID with tenant isolation verification.
    If the requested project belongs to another tenant, returns 403 Forbidden.
    """
    set_tenant_context(db, current_user.tenant_id)

    # First check if project exists across the entire database to determine cross-tenant refusal
    target_project = db.query(Project).filter(Project.id == project_id).first()

    if not target_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Multi-tenant boundary check
    if target_project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Cross-tenant data access is strictly prohibited.",
        )

    # Within same tenant: student can only access their own project
    if current_user.role == "student" and target_project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You may only view your own projects.",
        )

    return target_project


@router.patch("/{project_id}", response_model=ProjectResponse)
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    req: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update project attributes (title, stage, state_json, current_plan_json).
    Enforces strict multi-tenant isolation and ownership checks.
    """
    set_tenant_context(db, current_user.tenant_id)

    target_project = db.query(Project).filter(Project.id == project_id).first()
    if not target_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if target_project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Cross-tenant data access is strictly prohibited.",
        )

    if current_user.role == "student" and target_project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You may only update your own projects.",
        )

    if req.title is not None:
        target_project.title = req.title
    if req.stage is not None:
        target_project.stage = req.stage
    if req.state_json is not None:
        target_project.state_json = req.state_json
        flag_modified(target_project, "state_json")
    if req.current_plan_json is not None:
        target_project.current_plan_json = req.current_plan_json
        flag_modified(target_project, "current_plan_json")

    db.commit()
    db.refresh(target_project)
    return target_project
