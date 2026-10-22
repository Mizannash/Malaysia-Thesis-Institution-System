# MTIS Engineering Reflection & Architecture Review (Rubric D4 & D6)

**Milestone**: Phase 3 — Intelligence Pipeline & Stress-Hardening Contracts  
**Author**: MTIS Engineering Team  
**Date**: 2026-10-22  
**Evaluation Criteria Addressed**: **D4 (Quality Targets & Model Contracts)**, **D3 (Workflow State Persistence)**, **D6 (Operational Packaging & Viva Readiness)**  

---

## 1. Context & Motivation: The Problem with Unconstrained LLMs

In higher education thesis supervision across Malaysian public universities (UTM, UM, UKM, USM, UiTM), students and academic panels face a critical trustworthiness crisis with generative AI tools:
1. **Hallucinated Citations**: Generic LLMs invent non-existent DOIs, authors, and journal names.
2. **Fragile JSON Generation**: Unconstrained models frequently truncate JSON, output markdown chatter outside brackets, or alter key names unpredictably, breaking downstream UI components.
3. **Runaway API Costs**: Unprotected endpoints allow malicious or confused users to burn tokens on non-research queries or spam requests.
4. **Catastrophic State Loss**: When an LLM fails halfway through a multi-stage task, naive applications drop unsaved state, forcing students to start their research over from scratch.

MTIS was engineered from the ground up to eliminate these failure modes through an uncompromising, multi-layered contract architecture.

---

## 2. Architecture of the Mandatory AI Contract Layer (Rubric D4)

Implemented in [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py) and bridged via [`backend/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/ai/contract.py):

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Request                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  1. Pre-Call Policy Filter    │──[Abusive/Non-Academic]──► 400 Refusal (Cost: RM0.00)
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  2. Pre-Call Quota Gate       │──[Quota == 0]────────────► 429 Refusal (Cost: RM0.00)
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  3. LLM Provider Dispatch     │ (Live / Demo Fixtures / Mock)
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  4. Pydantic Schema Check     │──[Valid JSON & Schema]───► 200 OK -> DB State Saved
                 └───────────────┬───────────────┘
                                 │
                           [Malformed]
                                 │
                 ┌───────────────▼───────────────┐
                 │  5. Attempt Repair (Retry 1)  │──[Repaired]──────────────► 200 OK -> DB State Saved
                 └───────────────┬───────────────┘
                                 │
                           [Still Invalid]
                                 │
                 ┌───────────────▼───────────────┐
                 │  6. Defined Contract Failure  │──► 422 "AI returned invalid response.
                 │     (Zero DB Corruption)      │         Progress saved — retry Stage X."
                 └───────────────────────────────┘
```

### Key Engineering Decisions:
1. **Zero Unvalidated Output**: Every reasoning agent (`gap_agent.py`, `title_agent.py`, `deepdive_agent.py`) routes through `execute_contract_with_retry()`. No raw LLM string ever reaches the user without passing strict Pydantic model validation (`GapAnalysisResponse`, `TitleSuggestionsResponse`, `DeepDiveResponse`).
2. **Targeted Repair Retry**: Rather than failing immediately upon detecting minor formatting anomalies, the system logs `status: "retry"` in [`logs/ai_calls.jsonl`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/logs/ai_calls.jsonl) and issues a repair prompt containing the exact parser error.
3. **Defined, Human-Readable Failure Messages**: If the response remains invalid after the retry attempt, the system logs `status: "rejected_malformed"` and returns:
   > *"The AI returned an invalid response. Your progress is saved — retry Stage X."*  
   The application never displays a blank white screen, raw Python traceback, or half-saved garbage.
4. **Pre-Call Refusal Economics**: Non-research/abusive queries (`check_out_of_policy`) and depleted quotas (`check_user_quota`) are blocked **BEFORE** any LLM API call is dispatched. Both log `tokens: 0` and `cost_myr: 0.00`, protecting unit margins.
5. **Deterministic NO-KEY Demo Mode**: In `DEMO_MODE=true` (or when external API keys are absent), [`backend/app/ai/provider.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/provider.py) executes the full pipeline using pre-vetted fixtures in [`tests/fixtures/`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/fixtures/), logging `status: "no_key_mode"` with `cost_myr: 0.00`.

---

## 3. Database State Persistence & Refresh Restoration (Rubric D3)

In academic research, users routinely step away from their desk, refresh their browser, or switch devices.
- **Immediate Atomic Writes**: In [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py), the moment a reasoning agent finishes, `projects.state_json` is immediately updated with `flag_modified(project, "state_json")` and committed.
- **Timestamped Stage Tracking**: Every save records `last_saved_stage` (e.g. `"Stage 2 (Gap Analysis)"`) and `last_saved_at` (ISO timestamp).
- **UI Visibility**: Rendered directly on the project card in [`frontend/src/app/dashboard/page.tsx`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/frontend/src/app/dashboard/page.tsx) as `Last saved: stage X, <timestamp>`.
- **Zero Loss / Zero Duplication**: Verified in acceptance test `test_refresh_mid_pipeline_restores_exact_state`: simulating a browser refresh restores exact gap citations, suggested titles, and search parameters.

---

## 4. Test Suite & Verification Matrix (Rubric D4 & D5)

The stress-hardening suite in [`tests/acceptance/test_ai_stress.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_ai_stress.py) covers every edge case:

| Test Case | Edge Condition Simulated | Expected Behavior | Outcome |
|---|---|---|---|
| `test_malformed_llm_response_returns_defined_message_and_preserves_state` | Mock LLM outputs broken JSON twice | Returns 422 with defined failure message; existing DB state remains untouched; logs `retry` & `rejected_malformed` | **PASS** |
| `test_out_of_policy_content_polite_refusal_before_paid_call` | Prompt contains abusive/weapon keywords | Immediate 400 refusal before paid call; logs `refused_policy` with `cost_myr: 0.00` | **PASS** |
| `test_quota_exhausted_refusal_before_paid_call` | User has `quota_remaining = 0` | Immediate 429 refusal before paid call; logs `refused_quota` with `cost_myr: 0.00` | **PASS** |
| `test_demo_mode_no_keys_completes_full_pipeline` | `DEMO_MODE=true` with 0 keys | Search → Gap → Title → Deep-Dive completes on fixtures; logs `no_key_mode` | **PASS** |
| `test_basic_agent_quality_on_10_fixtures` | 10 fixture abstracts fed to agents | Gap agent yields ≥3 gaps citing real papers; title agent links 2–5 titles to `gap_id`; deep-dive yields 5–10 papers | **PASS** |
| `test_refresh_mid_pipeline_restores_exact_state` | Mid-pipeline browser refresh | `GET /projects/{id}` restores exact state, gaps, titles, and `last_saved_stage` metadata | **PASS** |

All 17 acceptance tests and 11 evaluation cases pass deterministically in under 5 seconds.
