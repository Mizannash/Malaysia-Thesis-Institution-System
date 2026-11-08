"""SQLAlchemy data models for MTIS multi-tenant schema."""
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    llm_provider = Column(String(32), default="deepseek", nullable=False)
    encrypted_api_key = Column(Text, nullable=True)
    key_preview = Column(String(32), nullable=True)
    # Institution identity: students whose confirmed email ends in this domain join this tenant
    email_domain = Column(String(255), nullable=True, unique=True, index=True)
    short_name = Column(String(64), nullable=True)
    kind = Column(String(16), nullable=True)  # public | private | auto | other
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(32), nullable=False, default="student")
    plan = Column(String(32), nullable=False, default="free")
    trial_start = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    quota_remaining = Column(Integer, nullable=False, default=3)
    quota_reset_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )
    # Academic Coach chat allowance (counted per Malaysia calendar day)
    chat_count = Column(Integer, nullable=False, default=0)
    chat_count_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="users")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

    @property
    def tenant_name(self) -> Optional[str]:
        return self.tenant.name if self.tenant else None

    @property
    def access_status(self) -> str:
        from app.access import access_status
        return access_status(self)

    @property
    def trial_ends_at(self) -> Optional[datetime]:
        from app.access import trial_ends_at
        return trial_ends_at(self)

    __table_args__ = (
        CheckConstraint("role IN ('student', 'supervisor', 'admin')", name="check_user_role"),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    stage = Column(String(64), nullable=False, default="search")
    state_json = Column(JSON, nullable=False, default=dict)
    plan_id = Column(String(64), nullable=True)
    current_plan_json = Column(JSON, nullable=True)
    plan_version = Column(Integer, nullable=False, default=0)
    last_refined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


    tenant = relationship("Tenant", back_populates="projects")
    user = relationship("User", back_populates="projects")


class AIDailyUsage(Base):
    """Platform-wide count of paid AI calls per Malaysia day (spend cap, not tenant data)."""
    __tablename__ = "ai_daily_usage"

    day = Column(Date, primary_key=True)
    calls = Column(Integer, nullable=False, default=0)
