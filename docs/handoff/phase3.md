# Phase 3 Handoff: AI Reasoning Agents & Stress-Hardening Contracts (Rubric D4 & D3)

**Role**: Builder Agent  
**Status**: Ready for Verifier Audit (Staged, not committed per AGENTS.md)  
**Date**: 2026-10-22  
**Target Milestone**: Phase 3 / Stage 2–4 Reasoning Agents with Strict AI Contracts  

---

## 1. Executive Summary

Phase 3 delivers the core AI reasoning agents spanning the MTIS guided pipeline:
1. **Stage 2: Gap Analysis Agent** (`backend/app/agents/gap_agent.py` & `prompts/gap_prompt.md`): Analyzes retrieved literature abstracts and extracts genuine research gaps citing ≥1 (typically ≥2) valid paper IDs.
2. **Stage 3: Title Suggestions Agent** (`backend/app/agents/title_agent.py` & `prompts/title_prompt.md`): Generates 2–5 defended thesis titles (in English or Bahasa Melayu) linking directly back to the selected `gap_id`.
3. **Stage 4: Deep-Dive Search Agent** (`backend/app/agents/deepdive_agent.py` & `prompts/deepdive_prompt.md`): Refines literature for the chosen title, retrieving 5–10 targeted papers.

### The Mandatory AI Contract Layer (Rubric D4 Heart - 20 Marks)
Located in `backend/app/ai/contract.py` (with bridge `backend/ai/contract.py`):
- **Pydantic Schema Validation**: Every LLM response is strictly validated against `GapAnalysisResponse`, `TitleSuggestionsResponse`, or `DeepDiveResponse`.
- **Malformed & Truncated Rejection + 1 Repair Retry**:
  - If the LLM produces invalid/broken JSON, it logs `status: "retry"` and immediately sends a targeted repair prompt.
  - If still invalid after retry, it logs `status: "rejected_malformed"` and returns a defined human-readable failure message:  
    `"The AI returned an invalid response. Your progress is saved — retry Stage X."`  
    Zero raw Python exceptions, zero blank screens, zero half-saved DB corruption.
- **Out-of-Policy Refusal Filter**:
  - Non-research and abusive queries (weapons, malware, recipes, poems, jailbreaks) are rejected **BEFORE** any paid API call.
  - Returns: `"Refusal: Your request is outside the scope of MTIS academic thesis research. Please provide an academic thesis topic."`
  - Log line records `status: "refused_policy"` with `cost_myr: 0.00`.
- **Per-User Quota Gate**:
  - Daily generation quota is verified **BEFORE** any paid API call.
  - At quota = 0, returns: `"Daily generation quota exceeded. Please upgrade your plan or wait for the quota reset."`
  - Log line records `status: "refused_quota"` with `cost_myr: 0.00`.
- **NO-KEY Mode (`DEMO_MODE=true`)**:
  - With `DEMO_MODE=true` and no API keys, the full 4-stage pipeline runs deterministically on cached fixtures (`tests/fixtures/`) with `cost_myr: 0.00` and `status: "no_key_mode"`.
- **Append-Only Logging** (`logs/ai_calls.jsonl`):
  - Every call logs `{user, stage, model, tokens, cost_myr, status, timestamp}`.

### State Persistence & Refresh Restoration (Rubric D3)
- Stage completion triggers immediate database writes to `projects.state_json` with `flag_modified` mutation tracking.
- Updates metadata: `"last_saved_stage"` and `"last_saved_at"`.
- Frontend dashboard renders: `"Last saved: stage X, <timestamp>"`.
- Mid-pipeline refresh restores exact state; zero data loss, zero duplicated records.

---

## 2. Inventory of Changes

### New Modules & Agents
- `prompts/gap_prompt.md`: System and user prompt for Stage 2 Gap Analysis.
- `prompts/title_prompt.md`: Bilingual thesis title prompt for Stage 3.
- `prompts/deepdive_prompt.md`: Targeted literature refinement prompt for Stage 4.
- `backend/app/ai/provider.py`: Swappable LLM adapter (mock, demo-fixtures, DeepSeek/OpenAI live API).
- `backend/app/ai/contract.py`: Mandatory AI contract layer enforcing repair retry, policy filter, quota gate, and JSONL logging.
- `backend/ai/contract.py`: Bridge export for root import compatibility.
- `backend/app/agents/gap_agent.py` & `backend/agents/gap_agent.py`: Gap reasoning agent.
- `backend/app/agents/title_agent.py` & `backend/agents/title_agent.py`: Title suggestions reasoning agent.
- `backend/app/agents/deepdive_agent.py` & `backend/agents/deepdive_agent.py`: Deep-dive search reasoning agent.
- `backend/app/routers/pipeline.py`: Pipeline endpoints with atomic DB state persistence.
- `tests/fixtures/sample_abstracts.json`: 10 structured academic abstracts with paper IDs P1..P10.
- `tests/fixtures/gap_fixture.json`: ≥3 sample gaps with citations linking to valid IDs.
- `tests/fixtures/title_fixture.json`: 2–5 thesis titles linked to gap IDs.
- `tests/fixtures/deepdive_fixture.json`: 6 targeted papers for title refinement.
- `tests/acceptance/test_ai_stress.py`: Comprehensive stress-hardening acceptance tests.

### Modified Files
- `backend/app/schemas.py`: Added `GapItem`, `GapAnalysisResponse`, `TitleItem`, `TitleSuggestionsResponse`, `DeepDiveResponse`, and pipeline request models.
- `backend/app/main.py`: Mounted `pipeline.router`.
- `frontend/src/app/dashboard/page.tsx`: Added display for `"Last saved: stage X, <timestamp>"`.
- `evals/cases.json`: Added 5 new Phase 3 eval cases (`P3_MALFORMED_REPAIR_FAILURE`, `P3_POLICY_REFUSAL`, `P3_QUOTA_EXHAUSTION`, `P3_DEMO_MODE_PIPELINE`, `P3_STATE_PERSISTENCE_REFRESH`).
- `evals/runner.py`: Implemented automated runner execution for Phase 3 cases.

---

## 3. Test & Evaluation Verification Evidence

### Acceptance Test Suite
Command: `.\.venv\Scripts\pytest.exe tests/acceptance/test_ai_stress.py -v`
```text
tests/acceptance/test_ai_stress.py::test_malformed_llm_response_returns_defined_message_and_preserves_state PASSED
tests/acceptance/test_ai_stress.py::test_out_of_policy_content_polite_refusal_before_paid_call PASSED
tests/acceptance/test_ai_stress.py::test_quota_exhausted_refusal_before_paid_call PASSED
tests/acceptance/test_ai_stress.py::test_demo_mode_no_keys_completes_full_pipeline PASSED
tests/acceptance/test_ai_stress.py::test_basic_agent_quality_on_10_fixtures PASSED
tests/acceptance/test_ai_stress.py::test_refresh_mid_pipeline_restores_exact_state PASSED
======================== 6 passed in 4.23s ========================
```

Full Active Suite: **17 passed, 1 live skipped, 26 future placeholders intact**.

### Automated Eval Runner
Command: `.\.venv\Scripts\python.exe evals/runner.py`
```text
============================================================
MTIS MULTI-PHASE EVALUATION RESULTS (PHASE 1, 2 & 3)
============================================================
[PASS] P1_HEALTH (0.045s)
[PASS] P1_AUTH_REDIRECT (0.019s)
[PASS] P1_CROSS_TENANT_REFUSAL (0.050s)
[PASS] P2_SEARCH_MY_SCOPE (0.034s)
[PASS] P2_SEARCH_VALIDATION_ERROR (0.010s)
[PASS] P2_SEARCH_DEDUPLICATION (0.058s)
[PASS] P3_MALFORMED_REPAIR_FAILURE (0.123s)
[PASS] P3_POLICY_REFUSAL (0.114s)
[PASS] P3_QUOTA_EXHAUSTION (0.060s)
[PASS] P3_DEMO_MODE_PIPELINE (0.326s)
[PASS] P3_STATE_PERSISTENCE_REFRESH (0.227s)
============================================================
GATE VERDICT: PASS
```

### Logging Evidence (`logs/ai_calls.jsonl`)
Confirmed log lines for:
- `status: "retry"`
- `status: "rejected_malformed"`
- `status: "refused_policy"` (`cost_myr: 0.00`)
- `status: "refused_quota"` (`cost_myr: 0.00`)
- `status: "no_key_mode"` (`cost_myr: 0.00`)

---

## 4. Instructions for Verifier Agent (Hermes)

1. Run `.\scripts\guard.ps1` to confirm `blueprint.json` is untouched and all 11 acceptance placeholder files exist.
2. Run `.\.venv\Scripts\pytest.exe -v` to confirm all 17 active tests pass.
3. Run `.\.venv\Scripts\python.exe evals/runner.py` to confirm 11/11 eval cases pass.
4. Verify `logs/ai_calls.jsonl` contains proper JSON lines with defined statuses and zero-cost policy/quota refusals.
5. If all checks pass, commit:
   `git commit -m "phase-3: reasoning agents & stress-hardening contracts [verified]"`
