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

## 🌐 Mode C: Cloud Deployment (Frontend on Netlify)

MTIS is structured as a modern decoupled full-stack application:
* **Frontend**: Next.js 14 Web Application (deploys cleanly on **Netlify**)
* **Backend**: FastAPI Python Server + PostgreSQL (deploys on Render, Railway, Fly.io, or any Docker VPS)

### Deploying Frontend to Netlify from GitHub

1. **Connect Repository in Netlify**:
   * Log into [Netlify](https://app.netlify.com/) and click **"Add new site"** → **"Import an existing project"**.
   * Select **GitHub** and authorize access to `Mizannash/Malaysia-Thesis-Institution-System`.

2. **Build Settings**:
   * Netlify automatically reads the included [`netlify.toml`](netlify.toml) with zero manual configuration required:
     * **Base directory**: `frontend`
     * **Build command**: `npm run build`
     * **Publish directory**: `.next`

3. **Configure Environment Variables** (In Netlify Site Settings → *Environment variables*):
   * `NEXT_PUBLIC_API_URL`: Your live backend API URL (e.g. `https://mtis-backend.onrender.com`).
     *(Note: If left unset or set to `http://localhost:8000`, the frontend will attempt to connect to localhost).*
   * `NEXT_PUBLIC_DEMO_MODE`: `true`
   * `NODE_VERSION`: `20`

4. **Deploy**:
   * Click **"Deploy site"**. Netlify will build Next.js and serve the app with global CDN distribution and SSL.

---

## 🚀 Mode D: Production (Supabase + Render + Netlify)

Live site: `https://malaysia-thesis-institution-system.netlify.app`. Real MTIS accounts (email + password with "Forgot password", run by Supabase Auth), a real PostgreSQL database, and the FastAPI backend with live DeepSeek on Render. Demo login is switched off in production.

Do the steps in this order. Keep every secret in the dashboards; never commit it.

### Step 1 — Supabase project (database + sign-in)
1. Go to [supabase.com](https://supabase.com) → **New project**. Pick region **Southeast Asia (Singapore)**, set a strong database password, and save it in your password manager.
2. **Project Settings → API**: copy the **Project URL** (`https://<ref>.supabase.co`) and the **anon public** key.
3. **Connect** (top bar) → **Session pooler** → copy the URI. It looks like
   `postgresql://postgres.<ref>:<PASSWORD>@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres`.
   Use the *Session pooler*, not the direct connection: Render's free plan only has IPv4.
4. **Authentication → URL Configuration**:
   * Site URL: `https://malaysia-thesis-institution-system.netlify.app`
   * Redirect URLs: add all four:
     * `https://malaysia-thesis-institution-system.netlify.app/login`
     * `https://malaysia-thesis-institution-system.netlify.app/reset-password`
     * `http://localhost:3000/login`
     * `http://localhost:3000/reset-password`

### Step 2 — Email accounts (sign up, confirm, forgot password)
1. Supabase → **Authentication → Sign In / Providers → Email**: turn **Enable Email provider** on, turn **Confirm email** on, set **Minimum password length** to `8`, then **Save**.
2. (Optional) **Authentication → Emails**: edit the "Confirm signup" and "Reset password" templates (subject and text) to add Bahasa Malaysia. Keep the `{{ .ConfirmationURL }}` link in each template.
3. Which university a new user joins is decided by the server from their email:
   * `@utm.my` and its subdomains (e.g. `@graduate.utm.my`) → UTM.
   * Any other email (Gmail, Yahoo, …) → **Independent Researchers**.
   * More universities: set `TENANT_EMAIL_DOMAINS` on Render, e.g. `utm.my:tenant-utm-001,um.edu.my:tenant-um-001` (the tenant row must exist).
   * To move one user: set `tenant_id` in their Supabase `app_metadata` (Authentication → Users → user → edit). Users cannot choose it themselves.

Google sign-in is off for now. To add it later, create a Google OAuth client with redirect URI `https://<ref>.supabase.co/auth/v1/callback`, enable Google under Sign In / Providers, and show the Google button again on the login page.

### Step 3 — Backend on Render
1. [render.com](https://render.com) → **New → Blueprint** → connect GitHub → choose `Mizannash/Malaysia-Thesis-Institution-System`. Render reads [`render.yaml`](render.yaml) and creates `mtis-backend` (Docker, free plan, Singapore).
2. Fill in the secrets it asks for:

   | Variable | Value |
   | :--- | :--- |
   | `DEEPSEEK_API_KEY` | your DeepSeek key |
   | `DATABASE_URL` | the Session pooler URI from Step 1.3 |
   | `SUPABASE_URL` | `https://<ref>.supabase.co` |
   | `ALLOWED_ORIGINS` | `https://malaysia-thesis-institution-system.netlify.app` |

   Already set by the blueprint: `APP_ENV=production`, `DEMO_MODE=false`, `LLM_PROVIDER=deepseek`, `AI_DAILY_GLOBAL_LIMIT=300`, `CHAT_DAILY_LIMIT=30`, and a generated `APP_SECRET`.
3. When the deploy is live, open `https://mtis-backend.onrender.com/health` → `{"status":"ok"}`. (Use the URL Render shows if the name differs.)
   * If the deploy log says `DATABASE_URL is unreachable`, re-check the pooler URI and password. Production never falls back to SQLite.
   * The free plan sleeps after ~15 minutes idle; the first request after that takes 30–60 seconds.

### Step 4 — Point Netlify at the backend
Netlify → Site configuration → **Environment variables**:

| Variable | Value |
| :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://mtis-backend.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://<ref>.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | the anon public key (it is designed to be public) |

Then **Deploys → Trigger deploy → Clear cache and deploy site**. With Supabase configured, the login page shows **Sign in / Create account** with "Forgot password?"; the demo personas disappear.

### Step 5 — Check it works
1. Open the site → **Create account** → open the confirmation email → you return to the site and land on the dashboard.
2. Run a topic search and ask Prof. Bijak a question → a real DeepSeek reply.
3. Sign out → **Forgot password?** → open the reset email → choose a new password → you are signed in again.
4. Create a second account → it cannot see the first account's projects.
5. Supabase → Table editor → `ai_daily_usage` → today's `calls` goes up with each AI call. At 300 the app answers "MTIS has reached today's AI limit" until midnight (Malaysia time).

### Step 6 — Make yourself the admin
Create your own account first, then Supabase → **Table Editor → `users`** → find your email → change `role` to `admin` → Save. Sign out and in again.

### Step 7 — Before real students: a real email sender
Supabase's built-in email sends only a few emails per hour and is meant for testing. Before launch:
1. Create a free [Resend](https://resend.com) account (3,000 emails/month) and an API key.
2. Supabase → **Authentication → SMTP Settings** → enable custom SMTP:
   host `smtp.resend.com`, port `465`, username `resend`, password = the Resend API key, sender e.g. `MTIS <no-reply@your-domain>`.
3. Without your own domain, Resend can only send to your own address; add and verify a domain in Resend to email students.

### New variables for `.env.example`
Add these to `.env.example` by hand (the agent is not allowed to open `.env*` files):
```
AI_DAILY_GLOBAL_LIMIT=300
CHAT_DAILY_LIMIT=30
ALLOWED_ORIGINS=*
TENANT_EMAIL_DOMAINS=utm.my:tenant-utm-001
SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```


---

## 🔐 Environment Variables Summary

| Variable | Scope | Default (Native) | Default (Docker) | Default (Netlify) | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend | `postgresql://user:password@localhost:5432/...` | `postgresql://user:password@db:5432/...` | N/A | Database connection |
| `DEMO_MODE` | Backend | `true` | `true` | N/A | Enables zero-key local fixture inference |
| `LLM_PROVIDER` | Backend | `deepseek` | `deepseek` | N/A | Model provider (`deepseek` or `openai`) |
| `APP_SECRET` | Backend | Random token | Random token | N/A | JWT and AES-256 master key |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:8000` | `http://localhost:8000` | `https://your-backend.url` | Browser API target URL |
| `NEXT_PUBLIC_DEMO_MODE`| Frontend | `true` | `true` | `true` | Demo mode UI switch |

