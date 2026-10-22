"""Health check endpoint router."""
from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for monitoring and orchestration."""
    return {"status": "ok", "service": "mtis-backend"}
