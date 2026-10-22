# Submission Message: Malaysian Thesis Institution System (MTIS)

**To**: Academic Evaluation Committee & Course Lecturers  
**From**: MTIS Engineering Team  
**Subject**: MTIS Full Integration & Ship Protocol — Final Delivery Package  
**Repository**: [https://github.com/Mizannash/Malaysia-Thesis-Institution-System.git](https://github.com/Mizannash/Malaysia-Thesis-Institution-System.git)  

---

### Dear Lecturers and Evaluators,

We are proud to present the final, hardened delivery of the **Malaysian Thesis Institution System (MTIS)** — an AI research guide that empowers Malaysian diploma, degree, and postgraduate researchers to identify defensible research gaps, formulate bilingual thesis titles (English / Bahasa Melayu), and structure robust research objectives and methodologies citing authentic institutional literature.

### 🌟 1. Visual Design & User Experience Excellence
Following our thorough integration of the **ScholarPulse / ThesisPilot visual blueprint** (`design Website/`), the platform delivers an encouraging, structured, and profoundly calm academic workspace:
- **Calm, High-Clarity Workspace**: Soft, paper-tinted neutral surfaces (`#f8f9ff`), elevated crisp white cards (`#ffffff`), and sky-blue horizon focus elements (`#006194` / `#0284c7`) designed to eliminate cognitive fatigue during multi-hour literature synthesis.
- **Top 5-Step Academic Roadmap**: A visual progress tracker guiding researchers through the complete journey:
  1. *Topic Definition* (OpenAlex & UTM ePrints repository indexing)
  2. *Gap Analysis* (AI candidate gap discovery citing $\ge 2$ empirical papers)
  3. *Title Suggestions* (Defended thesis titles in English & Bahasa Melayu)
  4. *Deep-Dive Search* (Sub-field paper targeting for methodology alignment)
  5. *Objectives & Methodology* (Stage 5 structured plan generation & iterative refinement)
- **Supportive Coach Companions**: Warm ivory cards (`#fffbeb`) bounded by reassuring 3px amber margins (`#f59e0b`) providing contextual academic guidance at each step of the dissertation journey.
- **Low-Friction Authentication**: Quick demo persona selectors on the login page allow instant campus role switching (`student@demo.test`, `supervisor@demo.test`, `ahmad@utm.my`) with zero external login friction.

### 🔐 2. Cryptographic Security & Stranger-Proof Architecture
- **AES-256-GCM Encrypted Storage**: Tenant API keys are encrypted at rest using AES-256 before database insertion. Plaintext credentials never exist in git history, database columns, or server logs. Previews are securely masked (`sk-...5566`).
- **Seamless DEMO / LIVE Mode Toggling**: The system operates 100% out-of-the-box in `DEMO_MODE=true` using high-fidelity local fixtures (zero API keys or configuration needed). Users can toggle to `LIVE_MODE` at any time from the dashboard settings modal.
- **PostgreSQL Row Level Security (RLS)**: Cryptographically verified institutional tenant boundaries prevent cross-tenant data leaks between universities (confirmed with HTTP 403 Forbidden assertions).

### 🧪 3. Verification & Acceptance Summary
- **Acceptance Tests**: **25 Passed, 1 Documented Conditional Skip** (100% Core Coverage).
  - *Documented Skip*: `test_uc2_live_openalex_query` is intentionally gated behind `RUN_LIVE_TESTS=1` to guarantee deterministic, offline reproducibility for the evaluator per Rubric D5.
- **Eval Release Gate**: **14 / 14 Multi-Phase Evals Passed (100% PASS)**.
- **Lecturer Simulation**: Full cloned-repo journey verified with a **100% PASS** verdict across all 6 steps (`docs/evidence/lecturer_simulation_log.md`).

### 🚀 4. Quickstart for Markers (Sub-10-Minute Demonstration)
```bash
# Clone the repository
git clone https://github.com/Mizannash/Malaysia-Thesis-Institution-System.git mtis
cd mtis

# Launch the demo stack (zero external keys needed)
make demo

# Visit in browser: http://localhost:3000
# Sign in using student@demo.test or ahmad@utm.my
```

Thank you for reviewing MTIS. All architectural specifications, viva runbooks, and design evidence logs are fully documented in `docs/` and ready for evaluation.
