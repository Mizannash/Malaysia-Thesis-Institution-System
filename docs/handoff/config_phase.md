# MTIS Phase Handoff: API Key Centralization & Data-Source Architecture

**Phase**: Configuration Centralization & Data-Source Architecture  
**Role**: Builder Agent (Staged for Verifier Audit; Uncommitted)  
**Date**: October 22, 2026  
**Status**: Ready for Verifier Audit  

---

## 1. Executive Summary

This phase centralizes all MTIS API keys, provider settings, and data acquisition configurations into a single, strictly validated environment-driven configuration system. No API keys or secrets are hardcoded anywhere in the codebase.

The system features:
1. **Centralized Configuration**: `backend/config.py` and `backend/app/config.py` load strictly from environment variables using Pydantic Settings, supporting `LLM_PROVIDER` (`deepseek` or `openai`), optional keys, default models, polite-pool email for OpenAlex, and `DEMO_MODE`.
2. **Unified LLM Adapter**: `backend/ai/llm_adapter.py` provides a single unified `complete(prompt: str, schema: type[BaseModel]) -> BaseModel` interface with automatic provider routing, graceful fallback (e.g. from DeepSeek to OpenAI if DeepSeek key is missing), and structured JSONL logging to `logs/ai_calls.jsonl`.
3. **Data Source Documentation**: `docs/data_sources.md` contains an end-to-end architectural flow diagram and source comparison table detailing acquisition type, authentication, cost, and degradation fallbacks for OpenAlex, UTM repository, and LLMs.
4. **Scraper Architecture Documentation**: `backend/agents/utm_scraper.py` and `backend/app/agents/utm_scraper.py` include the exact DSpace Playwright acquisition docstring and typed `ScraperError` definition.
5. **Acceptance Test Suite**: `tests/acceptance/test_config_modes.py` verifies all 3 required config scenarios.

---

## 2. File Inventory

| File | Status | Purpose |
| :--- | :--- | :--- |
| `backend/app/config.py` | Modified | Centralized Pydantic Settings with provider defaults and strict validation |
| `backend/config.py` | Created | Bridge re-exporting `Settings`, `settings`, and validation routines |
| `backend/app/ai/llm_adapter.py` | Created | Single `complete()` interface with routing, fallback, and JSONL logging |
| `backend/ai/llm_adapter.py` | Created | Bridge re-exporting `complete`, `LLMAdapter`, and `resolve_provider_config` |
| `backend/app/ai/provider.py` | Modified | Integrated with centralized settings and `resolve_provider_config` |
| `backend/app/agents/utm_scraper.py` | Modified | Added architecture docstring and `ScraperError` class |
| `backend/agents/utm_scraper.py` | Modified | Bridge updated with architecture docstring and `ScraperError` export |
| `backend/app/main.py` | Modified | Lifespan startup check via `validate_startup_config` |
| `docker-compose.yml` | Modified | Configured environment variables pass-through for backend container |
| `.env.example` | Modified | Added commented LLM, Data sources, and Mode sections |
| `docs/data_sources.md` | Created | Data sources architecture, ASCII flow diagram, and fallback matrix |
| `tests/acceptance/test_config_modes.py` | Created | 3 acceptance test cases for config modes and provider fallback |

---

## 3. Verification & Acceptance Evidence

### 3.1. Zero Hardcoded Keys Audit
- Command: `git grep -i -E "AIza|sk-[a-zA-Z0-9]{20,}" backend/ frontend/`
- Result: **0 matches found**. All API keys are loaded strictly via `os.getenv` or `Settings` from `.env`.

### 3.2. .env Gitignore Verification
- Command: `git check-ignore -v .env`
- Result: `.gitignore:1:.env .env` (confirmed ignored). `.env.example` committed with empty values only.

### 3.3. Config Modes Acceptance Test Execution
- Command: `pytest tests/acceptance/test_config_modes.py -v`
- Output:
  ```
  tests/acceptance/test_config_modes.py::test_demo_mode_true_all_keys_empty_pipeline_runs_on_fixtures PASSED [ 33%]
  tests/acceptance/test_config_modes.py::test_demo_mode_false_both_llm_keys_empty_startup_fails PASSED [ 66%]
  tests/acceptance/test_config_modes.py::test_llm_provider_deepseek_fallback_to_openai_logged PASSED [100%]
  ======================== 3 passed, 1 warning in 4.07s =========================
  ```

### 3.4. Full Acceptance Test Suite Regression Check
- Command: `pytest tests/acceptance/test_uc*.py tests/acceptance/test_ai_stress.py tests/acceptance/test_tenant_isolation.py tests/acceptance/test_config_modes.py -v`
- Result: **24 passed, 1 skipped** (live OpenAlex call skipped by default per D5 reproducibility policy).

### 3.5. Repository Guard Integrity Check
- Command: `powershell -ExecutionPolicy Bypass -File scripts\guard.ps1`
- Result: `Guard passed: blueprint.json is untouched and all 11 acceptance test files are present.`

---

## 4. Instructions for Verifier Agent
1. Review `docs/data_sources.md` for architecture and matrix correctness.
2. Confirm `.env` is gitignored (`git status --ignored` should show `.env`).
3. Run `pytest tests/acceptance/test_config_modes.py -v`.
4. Stage changes and commit according to project protocol.
