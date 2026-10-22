# MTIS Evaluation Rubric Evidence Map (D1–D6)

This document tracks MTIS implementation artifacts and verification logs against the six evaluation rubric criteria (D1–D6).

---

## Rubric Matrix

| Rubric Criterion | Description | Status | Evidence Files | Summary / Verification Notes |
|---|---|---|---|---|
| **D1** | **Value Hooks & Business Viability** | **COVERED** | - [`demo/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/demo/opening_script.md)<br>- [`frontend/src/app/pricing/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/pricing/page.tsx) | Payer identified (Malaysian HEI students / RMC labs); customer-voice problem documented; RM15/mo student pricing; ~RM0.20/run unit cost; 33-student break-even statement. |
| **D2** | **Identity, Roles & Multi-Tenant Isolation** | **COVERED** | - [`database/init.sql`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/database/init.sql)<br>- [`backend/app/auth.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/auth.py)<br>- [`backend/app/routers/projects.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/projects.py)<br>- [`tests/acceptance/test_tenant_isolation.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_tenant_isolation.py)<br>- [`docs/evidence/phase1_isolation.png`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/evidence/phase1_isolation.png) | PostgreSQL RLS enabled and forced; UTM (`tenant-utm-001`) and Demo Univ (`tenant-demo-002`) seeded; roles (`student`, `supervisor`); cross-tenant access returns 403 Forbidden with zero data leakage. |
| **D3** | **Workflow & AI Guided Pipeline** | *PENDING* | - [`frontend/src/app/dashboard/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/dashboard/page.tsx) (UI Stubs) | 5-stage pipeline: Topic Search → Gap Analysis → Title Suggestions → Deep-Dive → Objectives & Methodology. To be completed in Phase 2–4. |
| **D4** | **Quality Targets & Model Contracts** | *PENDING* | - [`docs/QUALITY.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/QUALITY.md)<br>- [`docs/PROMPT_CONTRACT.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/PROMPT_CONTRACT.md) | Quality thresholds (2+ real citations per gap, schema contracts, response formatting). Implemented in Phase 4. |
| **D5** | **Testing, Acceptance & Reliability** | **COVERED (Phase 1)** | - [`docs/evidence/phase1_test_log.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/evidence/phase1_test_log.md)<br>- [`docs/evidence/evals_run_2026-10-22.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/evidence/evals_run_2026-10-22.md)<br>- [`tests/acceptance/test_uc1_auth.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_uc1_auth.py)<br>- [`tests/acceptance/test_tenant_isolation.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_tenant_isolation.py) | 5/5 Phase 1 acceptance tests passing; 3/3 Phase 1 evaluation cases passing; `scripts/guard.ps1` confirms blueprint integrity and preservation of all 11 future milestone placeholders. |
| **D6** | **Deployment & Operational Packaging** | *PENDING* | - [`docker-compose.yml`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docker-compose.yml) | Local multi-container orchestration. Zero cloud deployment configs per security rule. Production release gate scheduled for Phase 6. |

---

## Phase Sign-Off Summary
- **Phase 1 Verdict**: **PASSED**
- **Criteria Covered**: **D1**, **D2** (and Phase 1 portions of **D5**)
- **Criteria Pending**: **D3**, **D4**, **D6** (Scheduled per `BUILD_PLAN.md`)
