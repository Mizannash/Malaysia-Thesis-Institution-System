# Phase 1 Foundation Handoff Document

This document summarizes all components created for Phase 1 of the Malaysian Thesis Institution System (MTIS), satisfying rubric criteria **D1 (Value hooks)** and **D2 (Identity, roles, and multi-tenant isolation)**.

---

## 1. Monorepo Architecture Overview

```text
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings, DEMO_MODE toggle, DB/Supabase envs
│   │   ├── database.py            # SQLAlchemy session, engine, tenant RLS context setter
│   │   ├── models.py              # Tenants, Users, Projects tables
│   │   ├── schemas.py             # Pydantic validation models
│   │   ├── auth.py                # Supabase / Demo auth verification & tenant injection
│   │   ├── main.py                # FastAPI entrypoint with /health and CORS
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py          # /health route returning {"status":"ok","service":"mtis-backend"}
│   │       ├── auth.py            # /auth/me, /auth/tenants, /auth/demo-login
│   │       └── projects.py        # /projects CRUD with strict cross-tenant 403 refusal
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout with metadata
│   │   │   ├── globals.css        # Premium dark mode theme with glassmorphism
│   │   │   ├── page.tsx           # Home landing page introducing MTIS
│   │   │   ├── login/page.tsx     # Google Sign-in & test persona switcher
│   │   │   ├── dashboard/page.tsx # Protected dashboard: badges, 5 workflow cards, cross-tenant test widget
│   │   │   └── pricing/page.tsx   # Public pricing (RM15/mo), unit economics & break-even statement
│   │   └── lib/
│   │       ├── api.ts             # Authenticated API client
│   │       └── supabase.ts        # Supabase client with Google OAuth integration
│   ├── middleware.ts              # Protects /dashboard (redirects unauthenticated to /login)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── Dockerfile
│
├── database/
│   └── init.sql                   # Multi-tenant schema, RLS policies, and UTM/Demo Univ seeds
│
├── docker-compose.yml             # Orchestration for frontend (3000), backend (8000), db (5432)
│
├── tests/acceptance/
│   ├── test_uc1_auth.py           # Google / Supabase sign-up and <5s dashboard redirect
│   └── test_tenant_isolation.py   # API and DB-level cross-tenant 403 assertion & RLS checks
│
├── evals/
│   └── cases.json                 # Added Phase 1 eval cases (health, auth redirect, cross-tenant refusal)
│
└── demo/
    ├── README.md
    └── opening_script.md          # Customer problem, payer, RM15/mo pricing, break-even statement
```

---

## 2. Multi-Tenancy & Row-Level Security (RLS) Implementation (D2)

- **Two Seeded Tenants**:
  1. `tenant-utm-001`: Universiti Teknologi Malaysia (UTM)
  2. `tenant-demo-002`: Demo University (for isolation marker tests)
- **Roles**:
  - `student`: Sees only their own research projects in their institution.
  - `supervisor`: Has supervisory oversight of all projects in their institution; receives the supervisor badge.
- **Row-Level Security**:
  - Enabled on `projects` and `users` via PostgreSQL policies (`tenant_id = get_current_tenant()`).
  - Session-level tenant context (`SET LOCAL app.current_tenant_id`) is strictly bound per API request.
  - Cross-tenant requests return **HTTP 403 Forbidden** with zero leaked data.

---

## 3. DEMO_MODE Configuration

- When `DEMO_MODE=true` (or when no external Supabase/OpenAI credentials exist in `.env`), the application runs entirely offline.
- Mock personas can be logged in with a single click from the UI:
  - UTM Student: `ahmad@utm.my`
  - UTM Supervisor: `siti@utm.my`
  - Demo University Student: `alex@demouniv.edu.my`
- The system boots cleanly on any fresh environment without requiring external cloud subscriptions.

---

## 4. Verification & Testing

To run the Phase 1 acceptance tests:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/acceptance/test_uc1_auth.py tests/acceptance/test_tenant_isolation.py -v
```

To run all services with Docker Compose:
```bash
docker compose up -d
```
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
