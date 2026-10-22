"""Database engine, session management, and RLS context handler."""
import logging
import socket
from urllib.parse import urlparse
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.models import Base, Tenant, User, Project

logger = logging.getLogger("mtis.database")


def is_postgres_available(url: str, timeout: float = 0.5) -> bool:
    """Quickly check if the target PostgreSQL host/port is accepting connections."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


database_url = settings.DATABASE_URL
connect_args = {}

if database_url.startswith("postgresql"):
    if is_postgres_available(database_url):
        connect_args = {"connect_timeout": 2}
    else:
        logger.info("PostgreSQL service not responding on 5432. Using SQLite in DEMO_MODE.")
        database_url = "sqlite:///./demo_mtis.db"
        connect_args = {"check_same_thread": False}
elif database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
except Exception as exc:
    logger.warning("Failed to initialize engine for %s: %s. Using SQLite fallback.", database_url, exc)
    database_url = "sqlite:///./demo_mtis.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create tables and seed initial tenants/users/projects if needed."""
    Base.metadata.create_all(bind=engine)
    # Migrate newly added columns if table already existed
    try:
        from sqlalchemy import inspect
        insp = inspect(engine)
        if insp.has_table("projects"):
            cols = [c["name"] for c in insp.get_columns("projects")]
            with engine.begin() as conn:
                if "plan_id" not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN plan_id VARCHAR(64)"))
                if "current_plan_json" not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN current_plan_json JSON"))
                if "plan_version" not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN plan_version INTEGER DEFAULT 0"))
                if "last_refined_at" not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN last_refined_at TIMESTAMP"))
    except Exception as exc:
        logger.warning("Column migration check notice: %s", exc)

    with SessionLocal() as db:

        utm_tenant = db.query(Tenant).filter_by(id="tenant-utm-001").first()
        if not utm_tenant:
            utm_tenant = Tenant(id="tenant-utm-001", name="Universiti Teknologi Malaysia (UTM)")
            demo_tenant = Tenant(id="tenant-demo-002", name="Demo University")
            db.add_all([utm_tenant, demo_tenant])

            # Seed UTM Users & Projects
            utm_student = User(
                id="usr-utm-student",
                tenant_id="tenant-utm-001",
                name="Ahmad Student",
                email="ahmad@utm.my",
                role="student",
                plan="free",
                quota_remaining=3,
            )
            utm_supervisor = User(
                id="usr-utm-supervisor",
                tenant_id="tenant-utm-001",
                name="Dr. Siti Supervisor",
                email="siti@utm.my",
                role="supervisor",
                plan="pro",
                quota_remaining=99,
            )
            utm_project1 = Project(
                id="prj-utm-101",
                tenant_id="tenant-utm-001",
                user_id="usr-utm-student",
                title="AI Research Gap Analysis in SME E-Wallet Adoption",
                stage="search",
                state_json={"topic": "E-wallet adoption in Malaysian SMEs", "scope": "MY"},
            )
            utm_project2 = Project(
                id="prj-utm-102",
                tenant_id="tenant-utm-001",
                user_id="usr-utm-student",
                title="IoT Precision Farming in Johor Palm Oil Plantations",
                stage="gap",
                state_json={"topic": "IoT precision agriculture", "scope": "MY"},
            )

            # Seed Demo University Users & Projects
            demo_student = User(
                id="usr-demo-student",
                tenant_id="tenant-demo-002",
                name="Alex Demo Student",
                email="alex@demouniv.edu.my",
                role="student",
                plan="free",
                quota_remaining=3,
            )
            demo_supervisor = User(
                id="usr-demo-supervisor",
                tenant_id="tenant-demo-002",
                name="Prof. Tan Supervisor",
                email="tan@demouniv.edu.my",
                role="supervisor",
                plan="pro",
                quota_remaining=99,
            )
            demo_project = Project(
                id="prj-demo-201",
                tenant_id="tenant-demo-002",
                user_id="usr-demo-student",
                title="Blockchain Smart Contracts in Malaysian Logistic Supply Chains",
                stage="title",
                state_json={"topic": "Logistics supply chain blockchain", "scope": "INT"},
            )

            db.add_all([
                utm_student, utm_supervisor, utm_project1, utm_project2,
                demo_student, demo_supervisor, demo_project
            ])
            db.commit()


# Ensure tables and seeds are initialized
try:
    init_db()
except Exception as e:
    logger.error("Auto-init error: %s", e)


def get_db() -> Generator[Session, None, None]:
    """Dependency for yielding standard DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant_context(session: Session, tenant_id: str):
    """Sets PostgreSQL session-level tenant variable for Row-Level Security (RLS)."""
    if "postgresql" in engine.url.drivername:
        session.execute(text("SELECT set_config('app.current_tenant_id', :tenant, true)"), {"tenant": tenant_id})
