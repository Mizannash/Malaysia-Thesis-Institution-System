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


SQLITE_FALLBACK_URL = "sqlite:///./demo_mtis.db"


def resolve_database_url(url: str, production: bool, check=is_postgres_available) -> str:
    """
    Picks the database URL to use.
    - Development: falls back to local SQLite when PostgreSQL is unreachable.
    - Production: never falls back (data would vanish on redeploy); fails loudly instead.
    Supabase connections get sslmode=require.
    """
    if not url.startswith("postgresql"):
        return url
    if not check(url, timeout=5.0 if production else 0.5):
        if production:
            raise RuntimeError(
                "Startup configuration error: DATABASE_URL is unreachable. "
                "Production never falls back to SQLite; check the Supabase Session pooler connection string."
            )
        logger.info("PostgreSQL service not responding on 5432. Using SQLite in DEMO_MODE.")
        return SQLITE_FALLBACK_URL
    host = urlparse(url).hostname or ""
    if "supabase" in host and "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


database_url = resolve_database_url(settings.DATABASE_URL, production=settings.is_production)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {"connect_timeout": 5}

try:
    engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
except Exception as exc:
    if settings.is_production:
        raise
    logger.warning("Failed to initialize engine: %s. Using SQLite fallback.", type(exc).__name__)
    database_url = SQLITE_FALLBACK_URL
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
        if insp.has_table("tenants"):
            t_cols = [c["name"] for c in insp.get_columns("tenants")]
            with engine.begin() as conn:
                if "llm_provider" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN llm_provider VARCHAR(32) DEFAULT 'deepseek'"))
                if "encrypted_api_key" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN encrypted_api_key TEXT"))
                if "key_preview" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN key_preview VARCHAR(32)"))
                if "email_domain" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN email_domain VARCHAR(255)"))
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_email_domain ON tenants (email_domain)"))
                if "short_name" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN short_name VARCHAR(64)"))
                if "kind" not in t_cols:
                    conn.execute(text("ALTER TABLE tenants ADD COLUMN kind VARCHAR(16)"))
        if insp.has_table("users"):
            u_cols = [c["name"] for c in insp.get_columns("users")]
            with engine.begin() as conn:
                if "chat_count" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN chat_count INTEGER NOT NULL DEFAULT 0"))
                if "chat_count_date" not in u_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN chat_count_date DATE"))
    except Exception as exc:
        logger.warning("Column migration check notice: %s", exc)

    with SessionLocal() as db:

        # Private-email sign-ups (Gmail, Yahoo, ...) join this tenant; must exist in every environment
        if not db.query(Tenant).filter_by(id="tenant-independent").first():
            db.add(Tenant(id="tenant-independent", name="Independent Researchers"))
            db.commit()

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
                name="Demo Student",
                email="student@demo.test",
                role="student",
                plan="free",
                quota_remaining=3,
            )
            demo_supervisor = User(
                id="usr-demo-supervisor",
                tenant_id="tenant-demo-002",
                name="Demo Supervisor",
                email="supervisor@demo.test",
                role="supervisor",
                plan="pro",
                quota_remaining=99,
            )
            demo_admin = User(
                id="usr-demo-admin",
                tenant_id="tenant-demo-002",
                name="Demo Admin",
                email="admin@demo.test",
                role="admin",
                plan="enterprise",
                quota_remaining=999,
            )
            demo_alex = User(
                id="usr-demo-alex",
                tenant_id="tenant-demo-002",
                name="Alex Demo Student",
                email="alex@demouniv.edu.my",
                role="student",
                plan="free",
                quota_remaining=3,
            )
            demo_tan = User(
                id="usr-demo-tan",
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
                demo_student, demo_supervisor, demo_admin, demo_alex, demo_tan, demo_project
            ])
            db.commit()

        # Malaysian institutions (after the demo seed, so UTM's existing row just gets its domain)
        from app.institutions import seed_institutions
        seed_institutions(db)


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
