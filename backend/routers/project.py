"""
Bridge router for project and plan operations.
Exposes endpoints specified in Requirement 2:
- POST /api/plan/refine {plan_id, user_prompt}
- Stage 5 plan generation and refinement
"""
from app.routers.pipeline import router, refine_plan_endpoint, run_stage_plan
from app.routers.projects import router as projects_router

__all__ = ["router", "projects_router", "refine_plan_endpoint", "run_stage_plan"]
