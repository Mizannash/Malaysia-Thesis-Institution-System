# Phase 5 Handoff: Viva Preparation, Technical Reflection & Final Documentation (Rubrics D5 & D6)

**Role**: Builder Agent  
**Status**: Ready for Verifier Audit (Staged, not committed per AGENTS.md)  
**Date**: 2026-10-22  
**Target Milestone**: Phase 5 / Viva Runbook, Engineering Reflection, and Final Audit  

---

## 1. Executive Summary

Phase 5 completes the operational auditability and viva defense preparation for MTIS, satisfying Rubrics **D6 (Viva / Reflection)** and **D5 (Audit & Technical Honesty)**:

1. **Engineering Reflection Document (Rubric D6)** ([`docs/reflection.md`](docs/reflection.md)):
   - **Mandatory Honest Scope Rejection**: Detailed architectural analysis of why dynamic vector embeddings with PostgreSQL `pgvector` was explicitly **rejected** during development:
     - *Multi-Tenant Isolation Breach Risks (D2)*: Vector approximate nearest neighbor (ANN) indexes operate across physical tables prior to Row-Level Security (RLS) post-filters, risking cross-tenant vector leakage between institutions.
     - *Unit Economics Inflation (D1 & D5)*: Vectorizing abstracts would inflate per-task token costs from **RM0.0175** to **~RM0.85**, breaking our 33-student break-even target.
     - *Academic Defensibility*: Malaysian supervisory panels demand exact DOI and bibliographical provenance, which fuzzy cosine similarity scores cannot provide.
   - **Technical Limits & Boundaries**: Transparently documents Playwright scraper fallback mechanisms, inference latency bounds (double-failure SLA $\le 30$s), and free-tier daily quota enforcement.

2. **Viva Defense Runbook (Rubric D6)** ([`docs/viva_runbook.md`](docs/viva_runbook.md)):
   - Structured as a comprehensive, direct cheat sheet table:
     - **Column 1**: Technical Topic / Examiner Question.
     - **Column 2**: Inspector Action & Exact Clickable File Line.
     - **Column 3**: Live Verification Command & Evidence.
   - Fully covers all rubric areas: D1 (pricing/break-even), D2 (RLS & 403 refusal), D3 (5-stage guided pipeline & state refresh), D4 (AI contract, malformed repair retry, out-of-policy refusal), D5 (zero half-saves, backup/restore), and D6 (rejected scope, release gate).

3. **Cost Per Request & Unit Economics (Rubric D5 & D1)** ([`docs/cost_per_request.md`](docs/cost_per_request.md)):
   - Complete 5-stage pipeline breakdown:
     - Stage 1 (Search): RM0.0000
     - Stage 2 (Gap Analysis, ~450 tokens): RM0.0029
     - Stage 3 (Title Suggestions, ~280 tokens): RM0.0018
     - Stage 4 (Deep-Dive Literature, ~520 tokens): RM0.0034
     - Stage 5 (Plan Generation, ~850 tokens): RM0.0055
     - Stage 5 (Plan Refinement, ~600 tokens): RM0.0039
   - Total tokens per complete run: **~2,700 tokens**.
   - Marginal inference cost: **RM0.0175 (under 2 sen)** in live API mode; **RM0.0000** in Demo Mode.
   - Student Pro Plan (RM15.00/mo) yields **>99% direct inference margin**.
   - Fixed infrastructure budget: RM450.00/mo $\rightarrow$ Break-even achieved at **31 to 33 paying students**.

4. **Aggregate Logging Metrics (Rubric D5)**:
   - Appended structured aggregate metrics line to [`logs/ai_calls.jsonl`](logs/ai_calls.jsonl) and [`backend/logs/ai_calls.jsonl`](backend/logs/ai_calls.jsonl).
   - Audited historical metrics across development: 126 calls, 41,850 tokens, RM0.00 actual spend (fixture protection), equivalent to RM0.27 total live spend.

5. **End-to-End Acceptance Integration Test** ([`tests/acceptance/test_uc_e2e_pipeline.py`](tests/acceptance/test_uc_e2e_pipeline.py)):
   - Executes the full 5-stage workflow sequentially using fixtures:
     Search $\rightarrow$ Gap Analysis $\rightarrow$ Title Suggestions $\rightarrow$ Deep-Dive Search $\rightarrow$ Plan Generation $\rightarrow$ Iterative Plan Refinement.
   - Asserts complete `StructuredPlan` schema integrity, version increment to v2, and database persistence.
   - **Passed** in 3.38s.

---

## 2. Test & Verification Evidence

- **E2E Integration Test**: `pytest tests/acceptance/test_uc_e2e_pipeline.py -v` $\rightarrow$ **1 passed in 3.38s**.
- **Full Acceptance Suite**: `pytest tests/acceptance/ -v` $\rightarrow$ **21 active tests passed**, 1 live-network test skipped, 26 future milestone placeholders preserved.
- **Evaluation Runner**: `python evals/runner.py` $\rightarrow$ **14/14 EVAL CASES PASSED (GATE VERDICT: PASS)**.
- **Integrity Guard**: `powershell -ExecutionPolicy Bypass -File scripts\guard.ps1` $\rightarrow$ **SHA256 verified, blueprint.json untouched, all 11 milestone placeholder test files intact**.

---

## 3. Instructions for Verifier
1. Verify `git status` — all changes staged, zero commits by Builder Agent.
2. Confirm `scripts/guard.ps1` passes with expected SHA-256 hash.
3. Review [`docs/reflection.md`](docs/reflection.md) for the rejected `pgvector` architectural review.
4. Review [`docs/viva_runbook.md`](docs/viva_runbook.md) table for exact question-action-evidence mappings.
5. Review [`docs/cost_per_request.md`](docs/cost_per_request.md) for the honest RM0.0175 per-run cost and break-even calculations.
6. Run `pytest tests/acceptance/test_uc_e2e_pipeline.py -v`.
7. If all checks pass, commit per verifier instructions.
