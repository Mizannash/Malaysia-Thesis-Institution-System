"""FastAPI Application Entry Point for MTIS Backend."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import health, auth, projects

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

# CORS Middleware for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local container and browser testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)


@app.get("/")
def root():
    return {
        "service": "mtis-backend",
        "status": "online",
        "demo_mode": settings.DEMO_MODE,
        "docs_url": "/docs",
    }
