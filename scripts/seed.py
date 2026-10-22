"""
MTIS Database Seeding Script.
Seeds UTM and Demo University tenants, roles, and default demonstration accounts.
Idempotent and safe to run multiple times.
"""
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import engine, SessionLocal, init_db
from app.models import Base, Tenant, User, Project

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mtis.seed")


def seed_database():
    """Seeds multi-tenant database with default institutions, roles, and test accounts."""
    logger.info("Initializing schema and running migrations...")
    init_db()

    with SessionLocal() as db:
        logger.info("Checking institutional tenants...")

        # 1. Tenants
        tenants_data = [
            {"id": "tenant-utm-001", "name": "Universiti Teknologi Malaysia (UTM)"},
            {"id": "tenant-demo-002", "name": "Demo University"},
        ]
        for t_data in tenants_data:
            existing = db.query(Tenant).filter_by(id=t_data["id"]).first()
            if not existing:
                db.add(Tenant(id=t_data["id"], name=t_data["name"]))
                logger.info(f"Seeded tenant: {t_data['name']} ({t_data['id']})")
            else:
                existing.name = t_data["name"]
        db.commit()

        # 2. Demonstration Users & Roles
        users_data = [
            # Demo University accounts (for instant evaluation)
            {
                "id": "usr-demo-student",
                "tenant_id": "tenant-demo-002",
                "name": "Demo Student",
                "email": "student@demo.test",
                "role": "student",
                "plan": "free",
                "quota_remaining": 3,
            },
            {
                "id": "usr-demo-supervisor",
                "tenant_id": "tenant-demo-002",
                "name": "Demo Supervisor",
                "email": "supervisor@demo.test",
                "role": "supervisor",
                "plan": "pro",
                "quota_remaining": 99,
            },
            {
                "id": "usr-demo-admin",
                "tenant_id": "tenant-demo-002",
                "name": "Demo Admin",
                "email": "admin@demo.test",
                "role": "admin",
                "plan": "enterprise",
                "quota_remaining": 999,
            },
            # UTM Institution accounts
            {
                "id": "usr-utm-student",
                "tenant_id": "tenant-utm-001",
                "name": "Ahmad Student",
                "email": "ahmad@utm.my",
                "role": "student",
                "plan": "free",
                "quota_remaining": 3,
            },
            {
                "id": "usr-utm-supervisor",
                "tenant_id": "tenant-utm-001",
                "name": "Dr. Siti Supervisor",
                "email": "siti@utm.my",
                "role": "supervisor",
                "plan": "pro",
                "quota_remaining": 99,
            },
        ]

        for u_data in users_data:
            existing_user = db.query(User).filter_by(id=u_data["id"]).first()
            if not existing_user:
                existing_user = db.query(User).filter_by(email=u_data["email"]).first()

            if not existing_user:
                user = User(
                    id=u_data["id"],
                    tenant_id=u_data["tenant_id"],
                    name=u_data["name"],
                    email=u_data["email"],
                    role=u_data["role"],
                    plan=u_data["plan"],
                    quota_remaining=u_data["quota_remaining"],
                )
                db.add(user)
                logger.info(f"Seeded user: {u_data['email']} ({u_data['role']}, {u_data['tenant_id']})")
            else:
                existing_user.role = u_data["role"]
                existing_user.plan = u_data["plan"]
                existing_user.quota_remaining = u_data["quota_remaining"]
                existing_user.tenant_id = u_data["tenant_id"]
        db.commit()

        # 3. Sample Demonstration Projects
        projects_data = [
            {
                "id": "prj-demo-201",
                "tenant_id": "tenant-demo-002",
                "user_id": "usr-demo-student",
                "title": "Blockchain Smart Contracts in Malaysian Logistic Supply Chains",
                "stage": "title",
                "state_json": {"topic": "Logistics supply chain blockchain", "scope": "INT"},
            },
            {
                "id": "prj-utm-101",
                "tenant_id": "tenant-utm-001",
                "user_id": "usr-utm-student",
                "title": "AI Research Gap Analysis in SME E-Wallet Adoption",
                "stage": "search",
                "state_json": {"topic": "E-wallet adoption in Malaysian SMEs", "scope": "MY"},
            },
            {
                "id": "prj-utm-102",
                "tenant_id": "tenant-utm-001",
                "user_id": "usr-utm-student",
                "title": "IoT Precision Farming in Johor Palm Oil Plantations",
                "stage": "gap",
                "state_json": {"topic": "IoT precision agriculture", "scope": "MY"},
            },
        ]

        for p_data in projects_data:
            existing_p = db.query(Project).filter_by(id=p_data["id"]).first()
            if not existing_p:
                proj = Project(
                    id=p_data["id"],
                    tenant_id=p_data["tenant_id"],
                    user_id=p_data["user_id"],
                    title=p_data["title"],
                    stage=p_data["stage"],
                    state_json=p_data["state_json"],
                )
                db.add(proj)
                logger.info(f"Seeded project: {p_data['title']} ({p_data['id']})")
            else:
                existing_p.title = p_data["title"]
                existing_p.stage = p_data["stage"]
        db.commit()

    logger.info("Database seeding successfully completed. (2 tenants, 5 users, 3 projects)")


if __name__ == "__main__":
    seed_database()
