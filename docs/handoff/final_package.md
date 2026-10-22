# MTIS Stranger-Proof Operational Package Handoff

**Phase**: Operational Packaging & Evaluator Stranger-Proofing  
**Target Audience**: Lecturers, Markers, and Independent Evaluators  
**Date**: October 22, 2026  
**Status**: Ready for Final Evaluator Demonstration  

---

## 1. Executive Summary

This package ensures that an academic marker or lecturer can clone the repository and reach a fully functioning, interactive demonstration of MTIS in under 10 minutes with **ZERO API keys** and zero prior local environment configuration.

All rubric requirements from D1 to D6 are completely satisfied and backed by automated evidence.

---

## 2. Key Packaging Deliverables

### 2.1. Quickstart & README Structure ([`README.md`](README.md))
- The quickstart is positioned at the top of the README:
  ```bash
  git clone https://github.com/Mizannash/Malaysia-Thesis-Institution-System.git mtis && cd mtis
  cp .env.example .env
  make demo
  ```
- Instant browser access at `http://localhost:3000`.
- Documented demonstration accounts:
  - `student@demo.test` (Free student role, 3 daily quota limit, D1/D4 upgrade hooks)
  - `supervisor@demo.test` (Supervisor role, 99 daily quota, full 5-stage pipeline & plan refinement)
  - `admin@demo.test` (Admin role, 999 daily quota, tenant administration)
  - `ahmad@utm.my` / `siti@utm.my` (UTM tenant accounts for multi-tenant barrier testing)

### 2.2. Automated Database Seeding & Entrypoint ([`scripts/seed.sh`](scripts/seed.sh) & [`scripts/seed.py`](scripts/seed.py))
- PostgreSQL database container automatically checks readiness via TCP socket polling.
- Idempotently executes migrations and seeds both institutional tenants (`tenant-utm-001` and `tenant-demo-002`) along with all seed accounts and initial sample projects.
- Safe to re-run on every boot without primary key collisions or state corruption.

### 2.3. Root Automation Harness ([`Makefile`](Makefile))
Standardized commands for machines with only Docker and Make:
- `make demo`: Prepares `.env`, starts Docker Compose stack (`db`, `backend`, `frontend`), waits for health, and displays sign-in instructions.
- `make test`: Automatically detects container or host environment and runs the acceptance test suite.
- `make clean`: Shuts down containers and purges volumes (`docker compose down -v`).

### 2.4. Comprehensive Evaluator Troubleshooting ([`TROUBLESHOOTING.md`](TROUBLESHOOTING.md))
Addresses the top 5 evaluator failure modes with diagnostic commands and one-line terminal fixes:
1. Port 3000/5432 already in use by local host services.
2. Docker daemon / Docker Desktop not running.
3. Slow Playwright image pull on campus Wi-Fi (offline fixture isolation).
4. Apple Silicon (ARM64) vs x86_64 architecture translation.
5. Cold-boot PostgreSQL connection latency and retry mechanisms.

### 2.5. Fresh-Clone Audit Log ([`docs/evidence/fresh_clone_log.md`](docs/evidence/fresh_clone_log.md))
- Generated via automated preflight audit runner ([`scripts/preflight_check.py`](scripts/preflight_check.py)).
- Proves clean clone, zero git secrets, immediate zero-key startup, and 100% test pass on fixtures.

---

## 3. Rubric Compliance Verification (D1–D6)

| Rubric Area | Criteria | Implementation & Proof |
| :--- | :--- | :--- |
| **D1: Business & Value** | Problem, Payer, Pricing | Free vs Pro (RM15/mo), RM0.0175 task cost, 33-student platform break-even ([`docs/opening_script.md`](docs/opening_script.md)). |
| **D2: Multi-Tenancy** | PostgreSQL RLS Isolation | Forced RLS policies on `users` and `projects`; cross-tenant access returns HTTP 403 Forbidden ([`tests/acceptance/test_tenant_isolation.py`](tests/acceptance/test_tenant_isolation.py)). |
| **D3: Guided Workflow** | 5-Stage Guided Pipeline | Full researcher journey from Topic Search $\rightarrow$ Gap $\rightarrow$ Title $\rightarrow$ Deep-Dive $\rightarrow$ Objectives/Plan ([`backend/app/routers/pipeline.py`](backend/app/routers/pipeline.py)). |
| **D4: Model Contracts** | AI Validation & Refusals | Strict Pydantic contracts, malformed repair retry, out-of-policy refusals before paid calls ([`backend/app/ai/contract.py`](backend/app/ai/contract.py)). |
| **D5: Testing & Reliability** | Offline Verification & Backups | 24 acceptance tests passing offline, automated backup/restore verified, atomic call logging ([`scripts/db_backup.py`](scripts/db_backup.py)). |
| **D6: Operational Delivery** | Packaging & Demo Runbook | Single `docker compose up` delivery, zero deployment files (`vercel.json`), step-by-step viva defense guide ([`docs/viva_runbook.md`](docs/viva_runbook.md)). |

---

## 4. Verification Checklist for Final Review

- [x] Zero hardcoded API keys anywhere in `backend/` or `frontend/`.
- [x] `.env` is gitignored; `.env.example` committed with empty values only.
- [x] `logs/` directory tracked with empty `.gitkeep`; all `.jsonl` files gitignored.
- [x] No personal absolute paths in repository documentation or source code.
- [x] No external deployment configurations committed (`vercel.json`, `fly.toml`, etc.).
- [x] `scripts/guard.ps1` passes (integrity of `blueprint.json` and 11 acceptance test files intact).
- [x] All 24 core acceptance tests pass.
- [x] Fresh clone audit script verifies zero-key readiness.
