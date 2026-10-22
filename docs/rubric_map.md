# MTIS Evaluation Rubric Evidence Map (D1–D6)

This document tracks MTIS implementation artifacts and verification logs against the six evaluation rubric criteria (D1–D6).

---

## Rubric Matrix

| Rubric Criterion | Description | Status | Evidence Files | Summary / Verification Notes |
|---|---|---|---|---|
| **D1** | **Value Hooks & Business Viability** | **COVERED** | - [`docs/opening_script.md`](docs/opening_script.md)<br>- [`demo/opening_script.md`](demo/opening_script.md)<br>- [`frontend/src/app/pricing/page.tsx`](frontend/src/app/pricing/page.tsx)<br>- [`frontend/src/app/plan/page.tsx`](frontend/src/app/plan/page.tsx) | Stage 5 structured plan generation and iterative refinement loop linked as primary value proposition; customer-voice problem documented; student break-even (>160x ROI on avoiding semester delay); RM15/mo student pricing; 33-student platform break-even statement. |
| **D2** | **Identity, Roles & Multi-Tenant Isolation** | **COVERED** | - [`database/init.sql`](database/init.sql)<br>- [`backend/app/auth.py`](backend/app/auth.py)<br>- [`backend/app/routers/projects.py`](backend/app/routers/projects.py)<br>- [`tests/acceptance/test_tenant_isolation.py`](tests/acceptance/test_tenant_isolation.py)<br>- [`docs/evidence/phase1_isolation.png`](docs/evidence/phase1_isolation.png) | PostgreSQL RLS enabled and forced; UTM (`tenant-utm-001`) and Demo Univ (`tenant-demo-002`) seeded; roles (`student`, `supervisor`); cross-tenant access returns 403 Forbidden with zero data leakage. |
| **D3** | **Workflow & AI Guided Pipeline** | **COVERED (Stages 1–5 Complete)** | - [`backend/app/routers/pipeline.py`](backend/app/routers/pipeline.py)<br>- [`backend/app/routers/search.py`](backend/app/routers/search.py)<br>- [`backend/app/agents/plan_agent.py`](backend/app/agents/plan_agent.py)<br>- [`tests/acceptance/test_uc4_plan.py`](tests/acceptance/test_uc4_plan.py)<br>- [`frontend/src/app/plan/page.tsx`](frontend/src/app/plan/page.tsx) | Complete 5-stage pipeline (Topic Search → Gap Analysis → Title Suggestions → Deep-Dive Search → Plan Generation & Refinement). Database schema tracks `plan_id`, `current_plan_json`, `plan_version`, and `last_refined_at`. State changes and version increments committed immediately to PostgreSQL. |
| **D4** | **Quality Targets & Model Contracts** | **COVERED** | - [`backend/app/ai/contract.py`](backend/app/ai/contract.py)<br>- [`backend/app/agents/gap_agent.py`](backend/app/agents/gap_agent.py)<br>- [`backend/app/agents/title_agent.py`](backend/app/agents/title_agent.py)<br>- [`backend/app/agents/deepdive_agent.py`](backend/app/agents/deepdive_agent.py)<br>- [`backend/app/agents/plan_agent.py`](backend/app/agents/plan_agent.py)<br>- [`logs/ai_calls.jsonl`](logs/ai_calls.jsonl) | Mandatory AI contract layer: Pydantic schema validation across all stages, malformed reply rejection with 1 repair retry, defined user-facing message on double failure ("The AI returned an invalid response. Your progress is saved — retry Stage X."). Out-of-policy and quota refusals execute BEFORE paid calls with RM0.00 cost. AES-256 encrypted tenant API key storage with masked previews (`sk-...xxxx`). |
| **D5** | **Testing, Acceptance & Reliability** | **COVERED (Phases 1–5)** | - [`docs/evidence/phase1_test_log.md`](docs/evidence/phase1_test_log.md)<br>- [`docs/evidence/phase2_test_log.md`](docs/evidence/phase2_test_log.md)<br>- [`docs/evidence/phase3_test_log.md`](docs/evidence/phase3_test_log.md)<br>- [`docs/evidence/phase4_test_log.md`](docs/evidence/phase4_test_log.md)<br>- [`docs/evidence/final_test_log.md`](docs/evidence/final_test_log.md)<br>- [`docs/evidence/backup_restore_log.md`](docs/evidence/backup_restore_log.md) | 25/26 implemented acceptance tests passing; 1 conditionally skipped live network test (documented below for 100% offline reproducibility); 14/14 automated evaluation cases passing across all phases; `scripts/db_backup.py` and `scripts/db_restore.py` verified with 100% relational integrity restored. |
| **D6** | **Deployment & Operational Packaging** | **COVERED** | - [`docs/viva_runbook.md`](docs/viva_runbook.md)<br>- [`demo/reflection.md`](demo/reflection.md)<br>- [`docker-compose.yml`](docker-compose.yml)<br>- [`Makefile`](Makefile)<br>- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)<br>- [`docs/evidence/fresh_clone_log.md`](docs/evidence/fresh_clone_log.md)<br>- [`docs/evidence/lecturer_simulation_log.md`](docs/evidence/lecturer_simulation_log.md) | Comprehensive viva demonstration script and engineering reflection artifacts completed. Multi-container orchestration, stranger-proof Makefile (`make demo`, `make test`, `make clean`), auto-seeding entrypoint (`scripts/seed.sh`), and verified fresh clone audit log with 100% test pass. Visual interface adheres to `design Website` (ScholarPulse / ThesisPilot). |

---

## Documented Conditional Test Skips (D5 Reproducibility)

| Test Identifier | File | Classification | Condition & Justification |
|---|---|---|---|
| `test_uc2_live_openalex_query` | [`tests/acceptance/test_uc2_search.py`](tests/acceptance/test_uc2_search.py#L196-L211) | **Intentionally Skipped** (Zero-Network Default) | Per Rubric **D5 (Reliability & Offline Reproducibility)** and `AGENTS.md`, default test runs MUST NOT depend on external live networks, public polite-pool internet latency, or 3rd-party API rate limits. The default acceptance suite runs against deterministically cached local fixtures. To activate live outbound network queries against `api.openalex.org`, export `RUN_LIVE_TESTS=1`. |

---

## Phase Sign-Off Summary
- **Phase 1 Verdict**: **PASSED** (D1, D2, Phase 1 D5)
- **Phase 2 Verdict**: **PASSED** (D3 Data Acquisition & Gateway, D5 Testing/Reliability/Cost Honesty)
- **Phase 3 Verdict**: **PASSED** (D4 Intelligence Pipeline & Stress Contracts, D3 State Persistence, D6 Viva Runbook)
- **Phase 4 Verdict**: **PASSED** (D1 Value Proposition & Plan Generation, D3 Versioned State Tracking & Refinement Loop, D5 Backup & Restore Operations)
- **Phase 5 & Final Gate Verdict**: **PASSED (ALL CRITERIA D1–D6 FULLY COVERED, VISUAL DESIGN INTEGRATED, HARDENED & VERIFIED)**
