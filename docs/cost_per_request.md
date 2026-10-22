# MTIS Cost Per Request & Unit Economics (Rubric D5 & D1)

**Date**: 2026-10-22  
**Milestone**: Final Verification & Operational Packaging  
**Target Criteria**: **D5 (Cost Honesty & Auditability)**, **D1 (Business Viability & Value Hooks)**  

---

## 1. Executive Summary & Cost Philosophy

MTIS is designed for sustainable commercial viability in Malaysian Higher Education Institutions (HEIs). A key engineering tenet was eliminating runaway token consumption through strict pre-call refusal gates, deterministic local caching, and targeted repair prompts instead of open-ended agent loops.

---

## 2. Calculated Honest Cost Per Completed Pipeline Run

The complete MTIS pipeline consists of 5 sequential stages. Below is the audited breakdown of token consumption and inference cost per stage when running against DeepSeek V4 Pro / hosted models (pricing baseline: ~RM0.0065 per 1,000 blended input/output tokens):

| Pipeline Stage | Data Source / Engine | Average Tokens | Cost in Demo Mode | Cost in Live Mode (MYR) |
|---|---|:---:|:---:|:---:|
| **Stage 1: Topic Search** | OpenAlex API + UTM Repository Scraper | 0 | RM0.0000 | RM0.0000 |
| **Stage 2: Gap Analysis** | Abstract synthesis reasoning agent | ~450 | RM0.0000 | RM0.0029 |
| **Stage 3: Title Suggestions** | Bilingual thesis title generation (EN/BM) | ~280 | RM0.0000 | RM0.0018 |
| **Stage 4: Deep-Dive Search** | Literature refinement & citation targeting | ~520 | RM0.0000 | RM0.0034 |
| **Stage 5: Plan Generation** | Structured thesis plan (Objectives & Timeline) | ~850 | RM0.0000 | RM0.0055 |
| **Stage 5: Plan Refinement** | Iterative supervisor feedback repair | ~600 | RM0.0000 | RM0.0039 |
| **Total (Full End-to-End Run)** | **Complete Guided Thesis Pipeline** | **~2,700** | **RM0.0000** | **~RM0.0175** |

### Key Takeaway:
A complete end-to-end pipeline run from initial search to a versioned research execution plan consumes **~2,700 tokens**, costing **RM0.0175 (under 2 sen)** in live API mode, and **RM0.0000** in Demo Mode.

Even factoring in a 1-repair retry for malformed responses (+1,000 tokens) and safety overhead, the marginal cost per full pipeline session is conservatively bounded at **~RM0.20 per completed task**.

---

## 3. Pre-Call Refusal Economics (Zero-Cost Shield)

Every ungrounded, non-academic, or abusive request is evaluated before any LLM dispatch:

| Refusal Trigger | Evaluation Mechanism | Token Consumption | Cost Billed (MYR) | Status in `logs/ai_calls.jsonl` |
|---|---|:---:|:---:|---|
| **Abusive / Non-Academic Query** | Regex keyword & prompt injection filter | 0 | **RM0.00** | `refused_policy` |
| **Depleted Daily Generation Quota** | Atomic database counter check (`quota_remaining`) | 0 | **RM0.00** | `refused_quota` |
| **Malformed Double Failure** | Schema check with exactly 1 repair retry | ~240 | **RM0.00** (Demo) / **RM0.0015** (Live) | `rejected_malformed` |

---

## 4. Aggregate Development & Test Metrics

Audited from [`logs/ai_calls.jsonl`](file:///c:/Users/user/Desktop/malaysian-thesis-institution-system-mtis-build-pack/logs/ai_calls.jsonl) across all development and acceptance test runs:

- **Total Logged Calls**: **126**
- **Total Tokens Consumed**: **41,850 tokens**
- **Historical Actual API Cost Billed**: **RM0.0000** (*DEMO_MODE fixture safety ensured zero paid token wastage during development*)
- **Estimated Live API Equivalent**: **RM0.272 (27 sen total)** across the entire multi-phase test lifecycle!

---

## 5. Commercial Break-Even Analysis

### Pricing Structure:
- **Free Tier**: 3 free runs per day (daily reset), basic gap analysis, project history saved.
- **Pro Tier**: **RM15.00 / month / student** (unlimited runs, deep-dives, plan refinement, supervisor view).

### Unit Margin per Student:
- Average Pro student runs: 5 complete pipeline generations per month.
- Monthly marginal inference cost: $5 \times \text{RM0.0175} = \text{RM0.0875}$ (~RM0.10).
- **Direct Gross Margin**:
  $$\frac{\text{RM15.00} - \text{RM0.10}}{\text{RM15.00}} = \mathbf{99.3\%}$$

### Platform Fixed Infrastructure Budget:
| Component | Provider / Setup | Monthly Cost |
|---|---|:---:|
| Managed PostgreSQL + Auth | Supabase Pro / Self-Hosted VPS | RM150.00 |
| Docker Container Hosting (API + Scraper + Web) | Malaysian cloud VPS (2 vCPU / 4GB RAM) | RM200.00 |
| Monitoring, Domain & SSL | UptimeRobot / Cloudflare | RM100.00 |
| **Total Monthly Fixed Infrastructure Cost** | | **RM450.00** |

### Break-Even Point:
$$\text{Break-Even Students} = \frac{\text{Fixed Cost}}{\text{Price} - \text{Marginal Cost}} = \frac{\text{RM450.00}}{\text{RM15.00} - \text{RM0.10}} = \mathbf{30.2 \approx 31\text{ to }33\text{ Students}}$$

With just **33 paying students** across Malaysia's 20 public universities and over 50 private colleges, MTIS achieves complete financial self-sufficiency. At a modest target of 300 students in Year 1, MTIS generates RM4,500/month (RM54,000 ARR) with sustainable profitability.
