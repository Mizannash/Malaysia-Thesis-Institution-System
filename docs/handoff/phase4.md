# Phase 4 Handoff: Plan Generation Agent, Iterative Refinement, and State Management (Rubrics D1, D3, D5)

**Role**: Builder Agent  
**Status**: Ready for Verifier Audit (Staged, not committed per AGENTS.md)  
**Date**: 2026-10-22  
**Target Milestone**: Phase 4 / Finalizing the User Journey & Operational Backup  

---

## 1. Executive Summary

Phase 4 finalizes the end-to-end user journey by introducing the Stage 5 Plan Generation Agent, the iterative supervisor/student refinement loop, and complete versioned state tracking:

1. **Stage 5 Plan Generation Agent** (`backend/app/agents/plan_agent.py` & `backend/agents/plan_agent.py`):
   - **Input**: Full project context (Search results, Gap list, Chosen title, Deep-Dive papers).
   - **Output**: Defense-ready structured research execution plan (`StructuredPlan` schema) covering research objectives (`objectives`), key deliverable milestones (`key_milestones`), necessary resources (`necessary_resources`), timeline phases (`timeline`), and methodology summary.
   - **Prompt Engineering** (`prompts/plan_prompt.md`): Instructs the LLM to act as a postgraduate thesis planning consultant adhering strictly to the provided empirical papers and gap.

2. **Iterative Refinement Loop** (`POST /api/plan/refine` & `backend/routers/project.py`):
   - Allows students and supervisors to provide feedback (e.g., *"Too ambitious: focus on Malaysian SMEs and reduce timeline to 18 months"*).
   - The agent applies a targeted repair prompt (`prompts/refine_prompt.md`), adjusts objectives, timeline, or methodology, increments `plan_version`, records `last_refined_at`, and writes the new version to the database.

3. **State Management & Versioning (Rubric D3)**:
   - The PostgreSQL `projects` table and SQLAlchemy model (`backend/app/models.py`) are expanded with:
     - `plan_id VARCHAR(64)`: Unique identifier for the research execution plan.
     - `current_plan_json JSONB`: The active structured plan payload.
     - `plan_version INT DEFAULT 0`: Incremental version counter (v1 -> v2 -> ...).
     - `last_refined_at TIMESTAMPTZ`: Timestamp of the latest refinement.
   - Automatic migration support (`backend/app/database.py`) inspects and adds missing columns dynamically on initialization.

4. **Operational Backup & Restore (Rubric D5)**:
   - `scripts/db_backup.py`: Performs database dumps using `pg_dump` locally or via `docker exec mtis-postgres-db pg_dump`, with local SQLite backup fallback. Verified against live PostgreSQL (`mtis_backup_*.sql`, ~120KB–260KB).
   - `scripts/db_restore.py`: Restores SQL dumps using `psql` locally or via Docker `mtis-postgres-db`. Verified with 100% exit code 0.

5. **Frontend Experience (Rubric D1 Value Hook)**:
   - **New "Plan View" Studio Page** (`frontend/src/app/plan/page.tsx`): Displays the structured plan document (Objectives, Milestones, Timeline, Resources, Methodology) with active `plan_version` badge and an interactive refinement panel.
   - **Dashboard Integration** (`frontend/src/app/dashboard/page.tsx`): Displays `Plan v{version}` badges on project cards with direct `View Plan` and `Generate Plan` actions.

6. **Documentation & Unit Economics (Rubric D1)**:
   - `docs/opening_script.md` and `demo/opening_script.md` finalized:
     - Establishes the structured thesis plan as the **primary customer value proposition**.
     - Calculates student break-even: avoiding a 1-semester proposal delay (RM2,500–RM5,000 tuition) yields **>160x ROI** on a RM15/month subscription.
     - Platform break-even: RM450/month fixed infrastructure cost achieved with **33 paying students** across Malaysian HEIs (>85% gross margin).

---

## 2. Inventory of Changes

### New Modules & Scripts
- `backend/app/agents/plan_agent.py`: Stage 5 Plan Generation and Iterative Refinement Agent with contract enforcement.
- `backend/agents/plan_agent.py`: Bridge export for root import compatibility.
- `backend/routers/project.py`: Bridge router exposing project refinement endpoints.
- `prompts/plan_prompt.md`: System and user prompt for Stage 5 Plan Generation.
- `prompts/refine_prompt.md`: Prompt template for iterative plan refinement.
- `tests/fixtures/plan_fixture.json`: Deterministic sample structured plan fixture.
- `scripts/db_backup.py`: Operational database backup utility for PostgreSQL and SQLite.
- `scripts/db_restore.py`: Operational database restore utility.
- `frontend/src/app/plan/page.tsx`: Dedicated Plan View page with interactive refinement studio.
- `tests/acceptance/test_uc4_plan.py`: Acceptance test suite for plan generation, refinement diffing, and tenant isolation.
- `docs/opening_script.md`: Comprehensive value proposition, opening script, and break-even analysis.

### Modified Files
- `backend/app/models.py`: Added `plan_id`, `current_plan_json`, `plan_version`, `last_refined_at` to `Project` model.
- `backend/app/database.py`: Added automatic schema inspection and migration in `init_db()`.
- `backend/app/schemas.py`: Added `StructuredPlan`, `ResearchObjective`, `PlanMilestone`, `PlanResource`, `TimelinePhase`, `PlanGenerateRequest`, `PlanRefineRequest`, `PlanRefineResponse`, and updated `ProjectResponse`.
- `backend/app/ai/provider.py`: Added mock and fixture dispatch for stages `"plan"` and `"refine"`.
- `backend/app/routers/pipeline.py`: Added `POST /projects/{project_id}/stage/plan`, `POST /api/plan/refine`, and direct agent endpoints.
- `frontend/src/app/dashboard/page.tsx`: Added Plan View links, workflow step routing, and version indicators.
- `demo/opening_script.md`: Aligned with final plan value hook and break-even metrics.
- `evals/cases.json`: Added `P4_PLAN_GENERATION`, `P4_PLAN_REFINEMENT`, `P4_DB_BACKUP_RESTORE`.
- `evals/runner.py`: Implemented automated runner execution for Phase 4 cases.

---

## 3. Test & Evaluation Verification Evidence

### Acceptance Test Suite
Command: `.\.venv\Scripts\pytest.exe tests/acceptance/test_uc4_plan.py -v`
```text
tests/acceptance/test_uc4_plan.py::test_plan_generation_within_30_seconds PASSED [ 33%]
tests/acceptance/test_uc4_plan.py::test_iterative_refinement_changes_plan_and_increments_version PASSED [ 66%]
tests/acceptance/test_uc4_plan.py::test_cross_tenant_refinement_refusal PASSED [100%]
======================== 3 passed in 3.01s ========================
```

Full Acceptance Suite Status: **20 active tests passed, 1 live skipped, 26 future placeholders preserved**.

### Automated Eval Runner
Command: `.\.venv\Scripts\python.exe evals/runner.py`
```text
============================================================
MTIS MULTI-PHASE EVALUATION RESULTS (PHASE 1, 2, 3 & 4)
============================================================
[PASS] P1_HEALTH (0.045s): HTTP 200 returned in 0.045s: {'status': 'ok', 'service': 'mtis-backend'}
[PASS] P1_AUTH_REDIRECT (0.020s): Unauthenticated request correctly refused with HTTP 401 within 0.020s (< 5.0s threshold)
[PASS] P1_CROSS_TENANT_REFUSAL (0.094s): Cross-tenant access refused with HTTP 403 in 0.094s. Detail: 'Access forbidden: Cross-tenant data access is strictly prohibited.'. Zero leaked data.
[PASS] P2_SEARCH_MY_SCOPE (0.043s): HTTP 200 returned in 0.043s with 11 papers and source tags: ['openalex', 'utm']
[PASS] P2_SEARCH_VALIDATION_ERROR (0.009s): HTTP 422 error contract returned in 0.009s: error='INVALID_QUERY_GIBBERISH'
[PASS] P2_SEARCH_DEDUPLICATION (0.021s): Deduplication confirmed in 0.021s across 11 papers with DOIs
[PASS] P3_MALFORMED_REPAIR_FAILURE (0.221s): Contract failure enforced with defined user message in 0.221s
[PASS] P3_POLICY_REFUSAL (0.044s): Out-of-policy refusal triggered before paid call in 0.044s: Refusal: Your request is outside the scope of MTIS academic thesis research. Please provide an academic thesis topic.
[PASS] P3_QUOTA_EXHAUSTION (0.053s): Quota exhaustion gate enforced before paid call in 0.053s
[PASS] P3_DEMO_MODE_PIPELINE (0.278s): Full 4-stage pipeline completed on fixtures in 0.278s with 0 external keys
[PASS] P3_STATE_PERSISTENCE_REFRESH (0.215s): Mid-pipeline reload restored exact state (gaps + titles preserved) in 0.215s: Stage 3 (Title Suggestions)
[PASS] P4_PLAN_GENERATION (0.138s): Plan generated in 0.138s (<30s) with valid schema (v1, plan_id: plan-f6683521)
[PASS] P4_PLAN_REFINEMENT (0.203s): Plan refined in 0.203s to v2 with demonstrably changed plan JSON in DB: 'Refined based on supervisor/student feedback: 'Narrow scope to Malaysian SMEs and reduce timeline to 18 months.''
[PASS] P4_DB_BACKUP_RESTORE (2.910s): Backup (266959 bytes) & restore verified successfully in 2.910s
============================================================
GATE VERDICT: PASS
```

### Operational Backup/Restore Verification
Commands tested:
- `python scripts/db_backup.py`: Successfully performed `docker exec mtis-postgres-db pg_dump`, generating 119KB+ SQL dump.
- `python scripts/db_restore.py -i database/backups/<backup_file>`: Successfully restored into `mtis-postgres-db` with zero errors.

### Integrity Guard
Command: `powershell -ExecutionPolicy Bypass -File scripts\guard.ps1`
```text
Guard passed: blueprint.json is untouched and all 11 acceptance test files are present.
```

---

## 4. Instructions for Verifier
1. Verify `git status` — all files are staged, zero commits made by Builder Agent.
2. Confirm `scripts/guard.ps1` passes with SHA256 integrity intact.
3. Run `.\.venv\Scripts\pytest.exe tests/acceptance/test_uc4_plan.py -v`.
4. Run `.\.venv\Scripts\python.exe evals/runner.py`.
5. Execute `python scripts/db_backup.py` and `python scripts/db_restore.py -i <dump>` to verify operational backup functionality.
6. Verify UI navigation from Dashboard to Plan View page (`/plan`).
