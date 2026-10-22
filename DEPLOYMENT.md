# MTIS Deployment Guide

This guide details the two supported deployment architectures for the **Malaysian Thesis Institution System (MTIS)**:
* **Mode A: Native Development (Windows PowerShell)** — Fast live iteration with React Fast Refresh & Python hot reload.
* **Mode B: Full Stack Docker Deployment** — Single-command reproducible container stack.

---

## 🔑 Demonstration Accounts

Out-of-the-box, the multi-tenant database is pre-seeded with three demo evaluation accounts:

| Role | Email | Password | Tenant | Features Accessible |
| :--- | :--- | :--- | :--- | :--- |
| **Researcher / Student** | `student@demo.test` | Any value | Demo University | Search, Gaps, Titles, Deep-Dive, Research Plan Studio |
| **Researcher (UTM)** | `ahmad@utm.my` | Any value | UTM Campus | Institutional Search, UTM Thesis Corpus, Plan Refinement |
| **System Admin (Owner)** | `admin@demo.test` | Any value | Demo University | User Directory, Subscription Upgrades, Quotas, System KPIs |

*In `DEMO_MODE=true`, the system operates 100% offline using verified local fixtures (`tests/fixtures/`) with zero external API keys required.*

---

## 💻 Mode A: Native Local Run (Windows PowerShell)

In Native Dev Mode, the database runs in an isolated PostgreSQL container, while the FastAPI backend and Next.js frontend run natively on Windows for instant debugging and live reload.

### Prerequisites
1. **Docker Desktop** (running for PostgreSQL)
2. **Python 3.12+** with virtual environment (`.venv`)
3. **Node.js 20+** and npm

---

### Step 1: Start PostgreSQL Database
```powershell
# From repo root: start only the postgres container
docker compose up -d db
```
*Port 5432 is published to `localhost:5432` with persistent volume `pgdata`.*

---

### Step 2: Seed the Database (First-time or fresh database)
```powershell
cd c:\Users\user\Desktop\malaysian-thesis-institution-system-mtis-build-pack
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis"
python scripts\seed.py
```

---

### Step 3: Terminal 1 — Start Native Backend (FastAPI)
```powershell
cd c:\Users\user\Desktop\malaysian-thesis-institution-system-mtis-build-pack\backend
..\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis"
$env:DEMO_MODE="true"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
* Backend API: `http://127.0.0.1:8000`
* Swagger Interactive Docs: `http://127.0.0.1:8000/docs`
* Health Endpoint: `http://127.0.0.1:8000/health`

---

### Step 4: Terminal 2 — Start Native Frontend (Next.js)
```powershell
cd c:\Users\user\Desktop\malaysian-thesis-institution-system-mtis-build-pack\frontend
npm run dev
```
* Frontend Web App: `http://localhost:3000`
* Configuration file: `frontend/.env.local` (`NEXT_PUBLIC_API_URL=http://localhost:8000`)

---

## 🐳 Mode B: Docker Full Stack Deployment

The Docker deployment packages the entire stack (`db`, `backend`, `frontend`) into isolated containers with automated database migration and seeding.

### Step 1: Launch Stack
```bash
# From repository root
docker compose up -d --build
```

### What Happens Automatically:
1. `mtis-postgres-db` starts and reports healthy via internal health check.
2. `mtis-backend-api` executes entrypoint [`scripts/seed.sh`](scripts/seed.sh):
   - Waits for database socket availability.
   - Executes idempotent seeding (`scripts/seed.py`) with `PYTHONPATH=/app`.
   - Starts Uvicorn production server on port 8000.
3. `mtis-frontend-web` builds optimized Next.js production bundle and serves on port 3000.

### Step 2: Verification
```bash
docker ps
curl http://localhost:8000/health
curl http://localhost:3000
```

### Clean Shutdown
```bash
# Stop containers (preserves postgres database volume pgdata)
docker compose down

# To completely wipe and reset database:
docker compose down -v
```

---

## 🔐 Environment Variables Summary

| Variable | Scope | Default (Native) | Default (Docker) | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend | `postgresql://user:password@localhost:5432/...` | `postgresql://user:password@db:5432/...` | Database connection |
| `DEMO_MODE` | Backend | `true` | `true` | Enables zero-key local fixture inference |
| `LLM_PROVIDER` | Backend | `deepseek` | `deepseek` | Model provider (`deepseek` or `openai`) |
| `APP_SECRET` | Backend | Random token | Random token | JWT and AES-256 master key |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000` | `http://localhost:8000` | Browser API target URL |
