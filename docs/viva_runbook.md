# MTIS Viva Defense Runbook & Examiner Cheat Sheet (Rubric D6)

**Project**: Malaysian Thesis Institution System (MTIS)  
**Target Audience**: Academic Examination Panel, Viva Examiners, Industrial Assessors  
**Scope**: Verification & Direct Code/Test Evidence Matrix across Rubrics D1 through D6  

---

## 1. Quick Verification Commands (Pre-Flight Checks)

```bash
# 1. Blueprint & Milestone Test Guard Check
powershell -ExecutionPolicy Bypass -File .\scripts\guard.ps1

# 2. Complete Acceptance Suite Run
.\.venv\Scripts\pytest.exe -v

# 3. Multi-Phase Eval Gate Run
.\.venv\Scripts\python.exe evals/runner.py

# 4. Disaster Recovery Backup & Restore Check
python scripts/db_backup.py
python scripts/db_restore.py -i database/backups/<backup_file>.sql
```

---

## 2. Examiner Technical Cheat Sheet (D1–D6 Matrix)

| Technical Topic / Examiner Question | Inspector Action & File Location | Live Verification Command & Evidence |
|---|---|---|
| **D1: Customer Problem & Payer**<br>"Who is the payer and what is the exact customer problem in their own words?" | Open [`docs/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/opening_script.md#L1-L24) and [`demo/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/demo/opening_script.md#L1-L24). | View Section 1 & 2: Identifies Malaysian diploma, FYP, and Master's/PhD students; customer-voice quotes on supervisor gap rejections and semester delay anxiety. |
| **D1: Pricing Model & Unit Economics**<br>"What is your price, marginal task cost, and break-even point?" | Open [`docs/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/opening_script.md#L26-L40) and [`frontend/src/app/pricing/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/pricing/page.tsx). | Table shows Free (RM0) vs Pro (RM15/mo); ~RM0.20 inference cost per run; break-even achieved at 33 paying students against RM450/mo infrastructure. |
| **D1: Core Value Proposition**<br>"What is the primary value hook that makes students pay?" | Open [`frontend/src/app/plan/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/plan/page.tsx) and [`docs/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/opening_script.md#L16-L25). | Stage 5 structured plan synthesis and iterative refinement loop: saves months of trial-and-error, delivering >160x ROI on a RM2,500–RM5,000 semester fee. |
| **D2: Multi-Tenant Database Isolation**<br>"How do you enforce institutional multi-tenant isolation at the database layer?" | Open [`database/init.sql`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/database/init.sql#L45-L87) lines 45–87. | Shows `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` and `tenant_isolation_users` policy enforcing `tenant_id = get_current_tenant()`. |
| **D2: Cross-Tenant Attack Refusal**<br>"What happens if a user from UTM tries to read or modify Demo University records?" | Open [`backend/app/routers/projects.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/projects.py#L79-L85) lines 79–85. | Run `pytest tests/acceptance/test_tenant_isolation.py -v`. Returns HTTP 403 Forbidden: *"Cross-tenant data access is strictly prohibited."* |
| **D2: UI Isolation Assertion**<br>"Can you demonstrate live tenant boundary security in the web interface?" | Navigate to `http://localhost:3000/dashboard`, scroll to bottom card. | Click **"Test Cross-Tenant Isolation Now"**; confirmed green banner displaying HTTP 403 refusal without data leakage. |
| **D3: Guided 5-Stage Pipeline**<br>"How does the 5-stage research progression work end-to-end?" | Open [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py) and [`frontend/src/app/dashboard/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/dashboard/page.tsx#L112-L149). | Review the 5 stages: 1. Search (OpenAlex/UTM) $\rightarrow$ 2. Gap Analysis $\rightarrow$ 3. Title Suggestions $\rightarrow$ 4. Deep-Dive $\rightarrow$ 5. Objectives & Plan. |
| **D3: Workflow State Persistence**<br>"What happens if a student refreshes their browser mid-pipeline?" | Open [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py#L123-L136) lines 123–136. | Run `pytest -k "test_refresh_mid_pipeline" -v`. Shows immediate commit to `state_json` with `flag_modified`; page reload restores exact state. |
| **D3: Versioned Plan Refinement**<br>"How does the supervisor/student feedback loop work?" | Open [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py#L358-L480) line 358 (`POST /api/plan/refine`). | Run `pytest -k "test_iterative_refinement" -v`. Diffs v1 vs v2 JSON in DB; records `plan_version = 2` and `last_refined_at`. |
| **D4: Schema Validation & Contracts**<br>"How do you ensure LLM outputs conform to required data structures?" | Open [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py#L159-L206) line 159 (`execute_contract_with_retry`). | Pydantic schema validation (`schema_cls.model_validate`); invalid outputs trigger repair loop; zero unvalidated data touches client. |
| **D4: Malformed LLM Replies & Repair**<br>"What happens if the model outputs broken JSON or conversational filler?" | Open [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py#L207-L255) line 207. | Run `pytest -k "test_malformed_llm" -v`. Logs `retry`; on double failure logs `rejected_malformed` and returns 422 with defined message. |
| **D4: Out-of-Policy Refusals**<br>"How do you block prompt injections or abusive non-academic requests?" | Open [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py#L113-L130) line 113 (`check_out_of_policy`). | Run `pytest -k "test_out_of_policy" -v`. Pre-call filter rejects with HTTP 400 *before* paid call; inspect `logs/ai_calls.jsonl` (`cost_myr: 0.00`). |
| **D4: Rate Limits & Quotas**<br>"How do you handle API rate limits and quota exhaustion?" | Open [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py#L132-L148) line 132 (`check_user_quota`). | Run `pytest -k "test_quota_exhausted" -v`. Quota check occurs *before* paid call; returns HTTP 429; logs `refused_quota` with `cost_myr: 0.00`. |
| **D4: Zero-Key Demo Mode**<br>"Can the system function without live paid API keys?" | Open [`backend/app/ai/provider.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/provider.py#L42-L95) line 42. | Run `pytest -k "test_demo_mode" -v`. Full 5-stage pipeline completes using cached fixtures in `tests/fixtures/`; logs `no_key_mode`. |
| **D5: Audit & Zero Half-Saves**<br>"How do you prove failed requests don't write orphaned rows or corrupt data?" | Open [`backend/app/routers/search.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/search.py#L65-L80) lines 65–80. | Run `pytest -k "test_uc2_search_invalid_input_zero_db_writes" -v`. Verifies zero project rows written on 422 validation failure. |
| **D5: Operational Backups & Disaster Recovery**<br>"How do you perform database backups and prove they can be restored?" | Open [`scripts/db_backup.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/scripts/db_backup.py) and [`scripts/db_restore.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/scripts/db_restore.py). | Check [`docs/evidence/backup_restore_log.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/evidence/backup_restore_log.md). Verified `pg_dump` snapshot (363KB) and `psql` restore with 100% integrity. |
| **D5: Cost & Token Logging**<br>"Where are per-call token counts and inference costs tracked?" | Open [`logs/ai_calls.jsonl`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/logs/ai_calls.jsonl) and [`docs/cost_per_request.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/cost_per_request.md). | Every AI call records `{user, stage, model, tokens, cost_myr, status, timestamp}` with running aggregate metrics. |
| **D6: Rejected Scope & Architecture Review**<br>"What major design was rejected during development and why?" | Open [`docs/reflection.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/reflection.md#L15-L60) Section 2. | Detailed discussion on rejecting dynamic `pgvector` indexing: prevented cross-tenant RLS vector leakage, avoided 4x token inflation, and preserved exact DOI citation provenance. |
| **D6: Production Readiness & Release Gate**<br>"How do you guarantee quality before any deployment release?" | Open [`evals/cases.json`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/evals/cases.json) and [`evals/runner.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/evals/runner.py). | Run `python evals/runner.py`. Release gate verifies all 14 multi-phase critical test cases return `GATE VERDICT: PASS`. |
