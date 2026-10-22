"""FastAPI Application Entry Point for MTIS Backend."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db
from app.routers import health, auth, projects, search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mtis.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("Starting up MTIS Backend (DEMO_MODE=%s)...", settings.DEMO_MODE)
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error("Database initialization error: %s", exc)
    yield
    logger.info("Shutting down MTIS Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Malaysian Thesis Institution System (MTIS)",
    version="1.0.0",
    lifespan=lifespan,
)

# Standardized Error Handlers (Requirement 7: {"error": code, "message": ...})
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("error", f"HTTP_{exc.status_code}")
        message = exc.detail.get("message", str(exc.detail))
        detail = exc.detail.get("detail", message)
    else:
        error_code = f"HTTP_{exc.status_code}"
        message = str(exc.detail)
        detail = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_code,
            "message": message,
            "detail": detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request parameters or payload.",
            "detail": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred. Please try again later."
        }
    )


# CORS Middleware for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(search.router)


@app.get("/")
def root():
    return {
        "service": "mtis-backend",
        "status": "online",
        "demo_mode": settings.DEMO_MODE,
        "docs_url": "/docs",
    }
