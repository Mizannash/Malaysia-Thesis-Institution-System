# MTIS Academic Viva Defense Runbook (Rubric D6 Evidence)

**Project**: Malaysian Thesis Institution System (MTIS)  
**Document**: Examiner Demonstration & Live Verification Runbook  
**Audience**: Thesis Examination Panel, Industrial Evaluators, Academic Supervisors  
**Applicable Milestones**: Phase 1 through Phase 3  

---

## 1. System Overview & Pre-Flight Checks

Before presenting to the examination committee, verify that the environment is operational:

```bash
# 1. Verify environment and guard script
powershell -ExecutionPolicy Bypass -File .\scripts\guard.ps1
# Expected output: Guard passed: blueprint.json is untouched and all 11 acceptance test files are present.

# 2. Run the acceptance test suite
.\.venv\Scripts\pytest.exe -v
# Expected: 17 passed, 1 skipped (live network gated)

# 3. Run the automated evaluation release gate
.\.venv\Scripts\python.exe evals/runner.py
# Expected: GATE VERDICT: PASS (11/11 cases passed)
```

---

## 2. Live Viva Demonstration Script

### Part 1: Value Proposition & Unit Economics (Rubric D1)
1. **Open Frontend**: Navigate to `http://localhost:3000/pricing`.
2. **Explain the Payer**:
   - Primary: Malaysian undergraduate final-year project (FYP) and postgraduate (Master's/PhD) students.
   - Secondary: University research labs and Faculty RMC research grants.
3. **Show Price & Unit Cost**:
   - Student Pro Plan: **RM15.00/month**.
   - Marginal inference cost per task: **~RM0.20** (~1,000 blended tokens via OpenAlex + DeepSeek).
   - Break-Even: **33 paying students** cover fixed monthly infrastructure (RM450/month).
   - Documented in: [`demo/opening_script.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/demo/opening_script.md).

---

### Part 2: Identity & Multi-Tenant Isolation (Rubric D2)
1. **Open Dashboard**: Log in at `http://localhost:3000/login` via Demo Mode as `ahmad@utm.my` (UTM Student, Tenant: `tenant-utm-001`).
2. **Point out Multi-Tenant Context**:
   - Active institution badge: *Universiti Teknologi Malaysia (UTM)*.
   - User role badge: *Student*.
   - Daily quota counter: *3 / 3 Free Runs Left*.
3. **Trigger Live Cross-Tenant Isolation Assertion**:
   - Scroll to the bottom card: *"Tenant Isolation Security Assertion (Rubric D2)"*.
   - Click **"Test Cross-Tenant Isolation Now"**.
   - Result: HTTP 403 Forbidden confirmed with message:  
     `"Access forbidden: Cross-tenant data access is strictly prohibited."`
   - Zero data from Demo University (`tenant-demo-002`) is exposed.
   - Backed by: PostgreSQL Row-Level Security in [`database/init.sql`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/database/init.sql) and [`tests/acceptance/test_tenant_isolation.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_tenant_isolation.py).

---

### Part 3: Guided Literature Workflow & State Persistence (Rubric D3)
1. **Explain the 5-Stage Guided Pipeline**:
   - Stage 1: Topic Search (OpenAlex + UTM institutional repository).
   - Stage 2: Gap Analysis (Synthesizes candidate gaps citing real papers).
   - Stage 3: Title Suggestions (Generates 2–5 thesis titles in EN/BM).
   - Stage 4: Deep-Dive Search (Refines literature for the chosen title).
   - Stage 5: Objectives & Methodology (Drafts proposal defense outline).
2. **Demonstrate State Persistence & Page Refresh**:
   - Point to a research project card on the dashboard.
   - Observe the timestamped badge: `Last saved: Stage 2 (Gap Analysis), 10/22/2026, 4:58:23 PM`.
   - **Press F5 (Browser Refresh)**:
     - The page reloads; the project title, literature list, and candidate gaps remain perfectly restored from `projects.state_json`.
     - Zero data loss, zero duplicated rows.
   - Code reference: [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py).
   - Test reference: `test_refresh_mid_pipeline_restores_exact_state` in [`tests/acceptance/test_ai_stress.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_ai_stress.py).

---

### Part 4: AI Contract Stress-Hardening & Failure Proofs (Rubric D4)
Demonstrate that the AI feature survives adversarial conditions without crashing:

1. **Proof 1: Malformed LLM Response Rejection & Repair Retry**:
   - Explain to examiners: When an LLM produces truncated or malformed JSON, MTIS rejects it, logs `status: "retry"`, and issues a repair prompt.
   - If repair also fails, it logs `status: "rejected_malformed"` and displays:
     > *"The AI returned an invalid response. Your progress is saved — retry Stage X."*
   - Verified by test: `test_malformed_llm_response_returns_defined_message_and_preserves_state`.

2. **Proof 2: Out-of-Policy Refusal BEFORE Paid Calls**:
   - Submit a non-academic query (e.g., weapon or malware instructions).
   - The pre-call filter rejects the prompt with HTTP 400 before dispatching to the LLM.
   - Open [`logs/ai_calls.jsonl`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/logs/ai_calls.jsonl) to show the log entry:
     `{"user": "...", "stage": "gap", "model": "policy-filter", "tokens": 0, "cost_myr": 0.0, "status": "refused_policy"}`.

3. **Proof 3: Quota Exhaustion Gate BEFORE Paid Calls**:
   - When a free student reaches 0 daily runs, subsequent calls are rejected with HTTP 429.
   - Log entry proves zero cost:
     `{"user": "...", "stage": "gap", "model": "quota-gate", "tokens": 0, "cost_myr": 0.0, "status": "refused_quota"}`.

4. **Proof 4: Deterministic Zero-Key DEMO_MODE**:
   - The entire pipeline executes on local cached fixtures with zero external keys.
   - Log entry proves: `status: "no_key_mode"`, `cost_myr: 0.00`.
   - Contract implementation: [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py).

---

## 5. Artifact Directory & File Index

| Component | File Path |
|---|---|
| **Contract Layer** | [`backend/app/ai/contract.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/contract.py) |
| **Provider Adapter** | [`backend/app/ai/provider.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/ai/provider.py) |
| **Gap Agent** | [`backend/app/agents/gap_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/gap_agent.py) |
| **Title Agent** | [`backend/app/agents/title_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/title_agent.py) |
| **Deep-Dive Agent** | [`backend/app/agents/deepdive_agent.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/agents/deepdive_agent.py) |
| **Pipeline Router** | [`backend/app/routers/pipeline.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/backend/app/routers/pipeline.py) |
| **Prompts** | [`prompts/`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/prompts/) (`gap_prompt.md`, `title_prompt.md`, `deepdive_prompt.md`) |
| **Fixtures** | [`tests/fixtures/`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/fixtures/) |
| **Stress Tests** | [`tests/acceptance/test_ai_stress.py`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/tests/acceptance/test_ai_stress.py) |
| **Call Audit Log** | [`logs/ai_calls.jsonl`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/logs/ai_calls.jsonl) |
| **Engineering Reflection** | [`demo/reflection.md`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/demo/reflection.md) |
