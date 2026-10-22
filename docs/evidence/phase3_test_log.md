# Phase 3 Test & Verification Log: AI Reasoning Agents & Stress Contracts

**Date**: 2026-10-22  
**Environment**: Python 3.12, FastAPI, SQLite/PostgreSQL, DEMO_MODE  
**Verifier**: Hermes / Antigravity Pair Verifier  
**Target Criteria**: **D4 (Quality Targets & Model Contracts)**, **D3 (Workflow State Persistence)**, **D5 (Reliability & Testing)**, **D6 (Operational Readiness)**  

---

## 1. Task 1: Audit of the Mandatory AI Contract Layer

### Verification Findings:
1. **Zero Unvalidated Output**:
   - In [`backend/app/agents/gap_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/gap_agent.py), [`title_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/title_agent.py), and [`deepdive_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/deepdive_agent.py), all LLM outputs route strictly through `execute_contract_with_retry()` in [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py).
   - Validates JSON parsing and strict Pydantic models (`GapAnalysisResponse`, `TitleSuggestionsResponse`, `DeepDiveResponse`).
   - If invalid, executes exactly ONE repair prompt. If still invalid, raises `AIContractError` with defined user message:
     `"The AI returned an invalid response. Your progress is saved — retry Stage X."`
   - Verified that zero raw Python exceptions, tracebacks, or blank screens are returned.
2. **Pre-Call Refusals (Zero Marginal Cost)**:
   - `check_out_of_policy()` checks input text BEFORE any paid call. On trigger, it immediately raises `AIPolicyRefusalError` (HTTP 400) and writes to `logs/ai_calls.jsonl`: `{tokens: 0, cost_myr: 0.00, status: "refused_policy"}`.
   - `check_user_quota()` checks user quota BEFORE any paid call. At `quota <= 0`, it immediately raises `AIQuotaExceededError` (HTTP 429) and writes to `logs/ai_calls.jsonl`: `{tokens: 0, cost_myr: 0.00, status: "refused_quota"}`.
   - Verified that no paid API tokens are expended for invalid, abusive, or quota-depleted calls.

---

## 2. Task 2: Acceptance Test Suite & Evals Execution

### Pytest Acceptance Suite (`pytest tests/acceptance/test_ai_stress.py -v`)
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\user\Desktop\malaysian-thesis-institution-system-mtis-build-pack
collected 6 items

tests/acceptance/test_ai_stress.py::test_malformed_llm_response_returns_defined_message_and_preserves_state PASSED [ 16%]
tests/acceptance/test_ai_stress.py::test_out_of_policy_content_polite_refusal_before_paid_call PASSED               [ 33%]
tests/acceptance/test_ai_stress.py::test_quota_exhausted_refusal_before_paid_call PASSED                           [ 50%]
tests/acceptance/test_ai_stress.py::test_demo_mode_no_keys_completes_full_pipeline PASSED                          [ 66%]
tests/acceptance/test_ai_stress.py::test_basic_agent_quality_on_10_fixtures PASSED                                 [ 83%]
tests/acceptance/test_ai_stress.py::test_refresh_mid_pipeline_restores_exact_state PASSED                         [100%]

============================== 6 passed in 4.23s ==============================
```

Full repository acceptance tests: **17 passed, 1 skipped (live network gated), 26 placeholder tests intact**.

### Automated Multi-Phase Evals Runner (`python evals/runner.py`)
```text
============================================================
MTIS MULTI-PHASE EVALUATION RESULTS (PHASE 1, 2 & 3)
============================================================
[PASS] P1_HEALTH (0.035s): HTTP 200 returned in 0.035s: {'status': 'ok', 'service': 'mtis-backend'}
[PASS] P1_AUTH_REDIRECT (0.017s): Unauthenticated request correctly refused with HTTP 401 within 0.017s (< 5.0s threshold)
[PASS] P1_CROSS_TENANT_REFUSAL (0.053s): Cross-tenant access refused with HTTP 403 in 0.053s. Detail: 'Access forbidden: Cross-tenant data access is strictly prohibited.'. Zero leaked data.
[PASS] P2_SEARCH_MY_SCOPE (0.029s): HTTP 200 returned in 0.029s with 11 papers and source tags: ['openalex', 'utm']
[PASS] P2_SEARCH_VALIDATION_ERROR (0.009s): HTTP 422 error contract returned in 0.009s: error='INVALID_QUERY_GIBBERISH'
[PASS] P2_SEARCH_DEDUPLICATION (0.058s): Deduplication confirmed in 0.058s across 11 papers with DOIs
[PASS] P3_MALFORMED_REPAIR_FAILURE (0.234s): Contract failure enforced with defined user message in 0.234s
[PASS] P3_POLICY_REFUSAL (0.043s): Out-of-policy refusal triggered before paid call in 0.043s: Refusal: Your request is outside the scope of MTIS academic thesis research. Please provide an academic thesis topic.
[PASS] P3_QUOTA_EXHAUSTION (0.041s): Quota exhaustion gate enforced before paid call in 0.041s
[PASS] P3_DEMO_MODE_PIPELINE (0.357s): Full 4-stage pipeline completed on fixtures in 0.357s with 0 external keys
[PASS] P3_STATE_PERSISTENCE_REFRESH (0.316s): Mid-pipeline reload restored exact state (gaps + titles preserved) in 0.316s: Stage 3 (Title Suggestions)
============================================================
GATE VERDICT: PASS
```

---

## 3. Task 3: Inspection of `logs/ai_calls.jsonl`

Inspected log entries confirm exact status codes and verified token/cost metrics:

| Log Event Type | Expected Status | Logged Model | Logged Tokens | Logged Cost (MYR) | Verification Status |
|---|---|---|---|---|---|
| Malformed Retry | `retry` | `mock-provider` | 120 | 0.00 | **CONFIRMED** |
| Malformed Final Rejection | `rejected_malformed` | `mock-provider` | 120 | 0.00 | **CONFIRMED** |
| Out-of-Policy Refusal | `refused_policy` | `policy-filter` | 0 | 0.00 | **CONFIRMED** (Pre-call) |
| Quota Exhaustion Refusal | `refused_quota` | `quota-gate` | 0 | 0.00 | **CONFIRMED** (Pre-call) |
| NO-KEY Fixture Gap Analysis | `no_key_mode` | `demo-fixtures` | 450 | 0.00 | **CONFIRMED** |
| NO-KEY Fixture Title Suggestion | `no_key_mode` | `demo-fixtures` | 280 | 0.00 | **CONFIRMED** |
| NO-KEY Fixture Deep-Dive Search | `no_key_mode` | `demo-fixtures` | 520 | 0.00 | **CONFIRMED** |

---

## 4. Task 4: State Persistence & UI Indicator Verification (Rubric D3)

1. **Immediate Atomic Writes**:
   - In [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py), each stage completion creates an updated copy of `project.state_json`, executes `flag_modified(project, "state_json")`, and commits to the database immediately.
2. **Metadata Markers**:
   - `last_saved_stage`: set to human-readable stage name (e.g., `"Stage 2 (Gap Analysis)"`).
   - `last_saved_at`: ISO 8601 UTC timestamp.
3. **UI Rendering**:
   - Verified [`frontend/src/app/dashboard/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/dashboard/page.tsx) renders `Last saved: {p.state_json.last_saved_stage}, {timestamp}` on research project cards.
4. **Refresh Mid-Pipeline**:
   - Tested in `test_refresh_mid_pipeline_restores_exact_state`: simulating browser refresh restores candidate gaps, suggested titles, and citations without loss or duplication.

---

## 5. Task 5: Documentation & Viva Runbook Audit (Rubric D6)

- [`demo/reflection.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/demo/reflection.md): Verified present. Contains in-depth engineering reflection on AI contract layers, failure modes, pre-call refusal economics, and explicit references to all 6 stress tests and agent modules.
- [`docs/viva_runbook.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/docs/viva_runbook.md): Verified present. Details exact live demonstration steps for the viva examination panel (D1 value hooks, D2 RLS isolation, D3 state persistence, D4 stress-hardening proofs, and D5 test suite).

---

## 6. Verifier Verdict

- **Contract Layer Audit**: **PASS**
- **Test Suite (17 active tests)**: **PASS**
- **Eval Release Gate (11 cases)**: **PASS**
- **AI Call Log Inspection**: **PASS**
- **State Persistence Verification**: **PASS**
- **D6 Documentation Audit**: **PASS**

**FINAL VERDICT**: **ALL CHECKS GREEN — PROCEED WITH SIGN-OFF COMMIT.**
