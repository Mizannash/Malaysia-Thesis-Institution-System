# Lecturer Journey & Visual Simulation Verification Log (Phase 4)

**Audit Execution Date**: 2026-10-22  
**Target Environment**: Fresh Clone Simulation (`make demo`, DEMO_MODE=True, Zero API Keys)  
**Visual Blueprint Sourced**: `design Website/` (ScholarPulse / ThesisPilot Design System)  
**Verification Harness**: Automated Design-Driven Simulation Runner (`scripts/simulate_lecturer.py`)  

---

## 1. Design & Visual Fidelity Checkpoint

The visual layout and interaction hierarchy across all user-facing views was audited directly against the blueprint files:
- `design Website/thesispilot/DESIGN.md` (Design tokens, color roles, typography, tonal elevation)
- `design Website/scholarpulse_control_panel/code.html` (5-step academic pipeline tracker, hero mission card)
- `design Website/scholarpulse_literature_search/code.html` (Conversational prompt card, search shortcuts)
- `design Website/scholarpulse_research_plan/code.html` (Proposal methodology canvas, coach refinement loop)

### Visual Fidelity Audit Summary:
| Visual Component | Blueprint Specification | Code Implementation | Verdict |
|---|---|---|---|
| **Color System** | Canvas `#f8f9ff`, cards `#ffffff`, Sky Blue `#006194`/`#0284c7`, Sage Green `#006c49`/`#10b981`, Ivory Coach note `#fffbeb` with `#f59e0b` border | Defined in [`frontend/src/app/globals.css`](../../frontend/src/app/globals.css) via standard CSS variables | **PASS** |
| **Typography** | `Plus Jakarta Sans` (headers & body), `Inter` (labels/badges), `JetBrains Mono` (code/citations) | Loaded in [`frontend/src/app/globals.css`](../../frontend/src/app/globals.css) | **PASS** |
| **Login View** | Centered clean card, brand header, Google Supabase trigger, quick persona pills (`student@demo.test`, `ahmad@utm.my`) | Implemented in [`frontend/src/app/login/page.tsx`](../../frontend/src/app/login/page.tsx) | **PASS** |
| **5-Stage Pipeline** | Topic Search → Gap Analysis → Title Suggestions → Deep-Dive Search → Plan Generation & Refinement | Top roadmap strip in [`frontend/src/app/dashboard/page.tsx`](../../frontend/src/app/dashboard/page.tsx) | **PASS** |
| **Hero Action Card** | Active stage banner, plain-language thesis prompt, candidate gaps strip with citation badges | Primary action canvas in [`frontend/src/app/dashboard/page.tsx`](../../frontend/src/app/dashboard/page.tsx) | **PASS** |
| **Coach Callouts** | Left 3px amber `#f59e0b` border, `#fffbeb` ivory fill, reassuring academic guidance note | `.coach-card` component across all views | **PASS** |
| **Key Management** | Modal with AES-256 encrypted storage, DEMO_MODE toggle, masked key preview (`sk-...xxxx`) | Settings modal in [`frontend/src/app/dashboard/page.tsx`](../../frontend/src/app/dashboard/page.tsx) | **PASS** |
| **Plan & Refine** | Objectives (§ 01), Milestones (§ 02), Timeline (§ 03), Resources (§ 04) + Refine with Coach input | Implemented in [`frontend/src/app/plan/page.tsx`](../../frontend/src/app/plan/page.tsx) | **PASS** |

---

## 2. Full Simulation Transcript & Verdicts

```text
=================================================================
MTIS LECTURER SIMULATION RUNNER (DESIGN & E2E PROTOCOL)
=================================================================

[STEP 1] Quickstart Authentication (student@demo.test)
  -> Status: PASS
  -> Authenticated as student@demo.test in tenant: tenant-demo-002

[STEP 2] Dashboard Data Hierarchy & Roadmap Verification
  -> Verified user student@demo.test, quota remaining: 10
  -> Active project: prj-da3e1b6b ('Cryo-EM Neural Attention in Protein Folding')
  -> 5-Stage Roadmap: Topic -> Gap -> Title -> Deep-Dive -> Plan
  -> Status: PASS

[STEP 3] Guided Pipeline Execution (Stage 2 -> Stage 3 -> Stage 4)
  -> Stage 2 (Gap Analysis): 3 candidate gaps identified with citations
  -> Stage 3 (Title Suggestions): 3 defended titles generated (EN/BM)
  -> Stage 4 (Deep-Dive Search): 6 sub-field papers retrieved
  -> Status: PASS

[STEP 4] Stage 5 Research Plan Generation & Iterative Refinement
  -> Plan v1 generated: 3 SMART objectives, 4 milestones
  -> Plan refined to v2: Refined based on supervisor/student feedback: 'Focus on Malaysian smallholders and shorten duration to 18 months'
  -> Status: PASS

[STEP 5] Tenant Boundary Isolation (Sign in as ahmad@utm.my)
  -> Cross-tenant refusal verified (HTTP 403): Access forbidden: Cross-tenant data access is strictly prohibited.
  -> Status: PASS

[STEP 6] AES-256 Encrypted API Key Management & Mode Toggle
  -> Encrypted key saved: deepseek, preview: sk-...5566
  -> Toggled mode: DEMO_MODE=False
  -> Reset back to safe default: DEMO_MODE=True
  -> Clean key deletion verified: has_custom_key=False
  -> Status: PASS

=================================================================
ALL 6 STEPS OF LECTURER SIMULATION VERIFIED: 100% PASS
=================================================================
```

---

## 3. Step-by-Step Verdict Table

| Step # | Simulation Phase | Verification Checks | Outcome |
|---|---|---|---|
| **Step 1** | Quickstart Authentication | `make demo` auto-seeds `student@demo.test`; demo-login issues JWT with claims; sets tenant context `tenant-demo-002`. | **PASS** |
| **Step 2** | Dashboard Visual Hierarchy | 5-step doctoral roadmap reflects Stage 1–5 progression; hero card shows active project state; tenant indicator displays Demo University. | **PASS** |
| **Step 3** | Pipeline Execution | Stage 2 Gap analysis extracts candidate gaps citing $\ge 2$ papers; Stage 3 Title agent generates bilingual (EN/BM) titles; Stage 4 Deep-Dive retrieves sub-field literature. | **PASS** |
| **Step 4** | Plan & Refinement | Stage 5 synthesizes structured plan; refinement router accepts user prompt, increments version to v2, and updates PostgreSQL database without partial corruption. | **PASS** |
| **Step 5** | Tenant Isolation Assertion | Signing in as `ahmad@utm.my` (`tenant-utm-001`) and attempting to read `prj-demo-201` returns `403 Forbidden` with zero data leakage. | **PASS** |
| **Step 6** | Encrypted Key Management | AES-256 encryption encrypts key before DB insert; preview is masked (`sk-...5566`); zero plaintext stored; DEMO_MODE toggles cleanly. | **PASS** |

---

## 4. Overall Lecturer Simulation Verdict

**FINAL VERDICT: 100% PASS**  
The entire customer and lecturer journey executes seamlessly with zero API keys required, adheres strictly to the ScholarPulse / ThesisPilot visual design blueprint, and maintains cryptographic isolation and contract reliability.
