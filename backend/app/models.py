"""SQLAlchemy data models for MTIS multi-tenant schema."""
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="users")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tenant = relationship("Tenant", back_populates="projects")
    user = relationship("User", back_populates="projects")
