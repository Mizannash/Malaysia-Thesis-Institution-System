# MTIS Functional Test Checklist: Complete System Audit

This checklist documents the complete click-through and functional audit of the **Malaysian Thesis Institution System (MTIS)** executed against the live native environment (FastAPI on `:8000`, Next.js on `:3000`, PostgreSQL on `:5432`).

### Institutional Role Model (Two Roles Only)
1. **Researcher / Student (Customer)**: Conducts academic research, searches institutional literature, discovers gaps, formulates defended titles, generates structured thesis plans, and refines milestones with the Academic Coach.
2. **System Owner / Admin (Owner)**: Manages platform users, monitors system health metrics, administers subscription plan tiers (Free / Pro / Enterprise), resets quotas, onboards researchers, and configures global API keys / offline demo modes.

---

## SECTION A: RESEARCHER / STUDENT FEATURES

### 1. Authentication & Session Security (Researcher)
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-AUTH-01** | Login Page Render | `GET /login` | Form renders with institutional branding, Google Auth (coming soon badge), and Demo Researcher quick-fill buttons | **PASS** |
| **STU-AUTH-02** | Demo Researcher Login | Click "Demo University Researcher" (`student@demo.test`) | 200 OK; returns JWT access token with role `student`, stores token, redirects to `/dashboard` | **PASS** |
| **STU-AUTH-03** | UTM Researcher Login | Click "UTM Researcher (Ahmad)" (`ahmad@utm.my`) | 200 OK; returns JWT with UTM tenant context (`tenant-utm-001`), redirects to `/dashboard` | **PASS** |
| **STU-AUTH-04** | Route Protection: Dashboard | Access `http://localhost:3000/dashboard` unauthenticated | Redirection guard immediately redirects unauthenticated user to `/login` | **PASS** |
| **STU-AUTH-05** | Route Protection: Plan Studio | Access `http://localhost:3000/plan` unauthenticated | Guard redirects immediately to `/login` | **PASS** |
| **STU-AUTH-06** | Session Invalidation | Click "Sign Out" button in dashboard header | JWT cleared from localStorage; redirected to `/login` | **PASS** |

### 2. Public Showcase & Marketing Navigation
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-LAND-01** | Brand Navigation | Click Logo / "ScholarPulse MTIS" | Navigates to `/` landing page | **PASS** |
| **STU-LAND-02** | Pricing Link | Click "Pricing (RM15/mo)" in navbar | Navigates to `/pricing` subscription tier comparison table | **PASS** |
| **STU-LAND-03** | Hero CTA Button | Click "Get Started with Zero Keys" | Navigates to `/login` | **PASS** |
| **STU-LAND-04** | Secondary Hero CTA | Click "View Student Pricing" | Navigates to `/pricing` | **PASS** |
| **STU-LAND-05** | Architecture Cards | Inspect 3 showcase cards | Displays Local Repository Indexing, 5-Stage Workflow, Tenant Isolation | **PASS** |

### 3. Thesis Roadmap & Workspace Control Panel
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-DASH-01** | Control Panel Load | Authenticated `GET /dashboard` | 200 OK; loads header, tenant badge, roadmap, and project sidebar | **PASS** |
| **STU-DASH-02** | Active Thesis Banner | Inspect active project banner | Displays thesis title, stage metadata, and project identifier | **PASS** |
| **STU-DASH-03** | 5-Step Pipeline Tracker | Inspect 5 pipeline stage cards | Stages 1 through 5 rendered with active step highlighted | **PASS** |
| **STU-DASH-04** | Daily Quota Badge | Inspect quota badge in header | Renders remaining daily quota balance (e.g. `Quota: 5 / 5 Left`) | **PASS** |
| **STU-DASH-05** | Create New Project | Click "+ New Project" button | Creates fresh project record via `POST /projects`, resets stage to `search`, prepends to sidebar | **PASS** |
| **STU-DASH-06** | Project Switching | Click another project in sidebar | Switches active project context, updates literature, gaps, and titles | **PASS** |
| **STU-DASH-07** | Subscriptions Link | Click "Subscriptions" button in header | Navigates cleanly to `/pricing` | **PASS** |

### 4. Stage 1: Topic Literature Search & Article Discovery
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-SRCH-01** | Scope Switcher | Click "Malaysian (UTM & MY)" vs "Global (OpenAlex)" | Toggles search scope between `MY` and `INT` | **PASS** |
| **STU-SRCH-02** | Search Execution | Enter "blockchain supply chain" and submit | 200 OK; returns 11 papers with titles, authors, citations, and institutions | **PASS** |
| **STU-SRCH-03** | Search Loading Feedback | Submit search query | Button disables, spinner animates, text shows "Searching..." | **PASS** |
| **STU-SRCH-04** | Search Result Cards | Inspect retrieved paper cards | Displays paper title, author list, year, citation count, and institutional badge | **PASS** |
| **STU-SRCH-05** | Empty Results State | Search an obscure non-existent keyword in offline mode | Displays clear alert: "No articles found matching query" instead of silent blank | **PASS** |
| **STU-SRCH-06** | Empty Query Guard | Submit with empty search input | Button remains disabled; prevents wasted empty API requests | **PASS** |

### 5. Stages 2 to 4: Gap Analysis, Title Suggestions & Deep-Dive
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-PIPE-01** | Run Gap Analysis | Click "Run Stage 2: Gap Analysis" | 200 OK; generates 3 defended research gaps citing retrieved papers; advances stage to `gap` | **PASS** |
| **STU-PIPE-02** | Gap Cards Display | Inspect candidate gap cards | Displays description, citation defense tags, and supporting paper IDs | **PASS** |
| **STU-PIPE-03** | Run Title Suggestions | Click "Run Stage 3: Title Suggestions" | 200 OK; generates bilingual (EN/BM) title proposals with defense rationale; advances stage to `title` | **PASS** |
| **STU-PIPE-04** | Title Selection | Click "Select This Title" | Saves chosen title to project record and synchronizes across views | **PASS** |
| **STU-PIPE-05** | Run Deep-Dive Search | Click "Run Stage 4: Deep-Dive" | 200 OK; queries sub-field papers aligned to chosen title; advances stage to `deepdive` | **PASS** |

### 6. Stage 5: Research Plan Studio & Academic Coach Refinement (`/plan`)
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-PLAN-01** | Plan Studio Load | Authenticated `GET /plan?projectId={id}` | 200 OK; loads Research Objectives, Methodology, Gantt Timeline, and Coach chat | **PASS** |
| **STU-PLAN-02** | Generate Plan (v1) | Click "Generate Research Plan" | 200 OK; creates structured objectives, data sources, and 12-month milestone timeline | **PASS** |
| **STU-PLAN-03** | Coach Iterative Refine | Submit refinement prompt: "Shorten timeline to 9 months" | 200 OK; increments plan version (v2, v3), updates milestones, provides coach rationale | **PASS** |
| **STU-PLAN-04** | Milestone Visualizer | Inspect timeline milestones | Renders Gantt-style cards with completion quarters and deliverable targets | **PASS** |

### 7. Academic Coach Assistant (Dashboard Companion)
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-COACH-01** | Stage-Specific Guidance | Switch between Search, Gap, Title, and Plan stages | Coach note dynamically updates with context-relevant advice | **PASS** |
| **STU-COACH-02** | Quick Exploration Chips | Click prompt chip (e.g. "🌴 IoT Smart Agriculture") | Automatically populates topic search input and executes query | **PASS** |
| **STU-COACH-03** | Conversational Form | Enter research question in coach input and submit | Dispatches query to search and analysis pipeline | **PASS** |

### 8. Personal Settings & Tenant API Key Encryption
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **STU-SETT-01** | Open Settings Modal | Click "API Settings" / Key icon in navbar | Opens modal explaining AES-256 encryption & offline mode toggle | **PASS** |
| **STU-SETT-02** | Save Custom API Key | Enter `sk-test-key-9988` and click Save | 200 OK; encrypted server-side; masked preview shows `sk-...9988` | **PASS** |
| **STU-SETT-03** | Mode Toggle | Click "Toggle Offline Mode" | 200 OK; switches between DEMO_MODE (true) and LIVE (false) | **PASS** |
| **STU-SETT-04** | Wipe API Key | Click "Remove Key" | 200 OK; database key record securely deleted; UI returns to empty state | **PASS** |

---

## SECTION B: SYSTEM OWNER / ADMIN FEATURES

### 1. Authentication & Route Privilege Enforcement (Admin)
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-AUTH-01** | Admin Login | Click "System Admin (Owner)" (`admin@demo.test`) | 200 OK; returns JWT with role `admin`, provides access to owner routes | **PASS** |
| **ADM-AUTH-02** | Unauthorized Student Rejection | Student token calls `GET /api/admin/users` | 403 Forbidden `{"detail":"Forbidden: administrator privilege required"}` | **PASS** |
| **ADM-AUTH-03** | Unauthorized Unauthenticated Rejection | No token calls `GET /api/admin/users` | 401 Unauthorized | **PASS** |

### 2. System Overview & Platform Health Metrics
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-METR-01** | Query Platform Stats | `GET /api/admin/stats` with Admin token | 200 OK; returns total users, student count, admin count, plans breakdown, total projects | **PASS** |
| **ADM-METR-02** | Total Users KPI | Inspect `total_users` in stats response | Accurately returns platform count (238 users) | **PASS** |
| **ADM-METR-03** | Plans Breakdown KPI | Inspect `plans_breakdown` in stats response | Accurately reports distribution (`free: 204`, `pro: 33`, `enterprise: 1`) | **PASS** |
| **ADM-METR-04** | Total Projects KPI | Inspect `total_projects` in stats response | Accurately reports active multi-tenant thesis projects (208 projects) | **PASS** |
| **ADM-METR-05** | Service Health KPI | Inspect `service_status` in stats response | Returns `"healthy"` | **PASS** |

### 3. User Directory & Subscription Management
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-USER-01** | Query User Directory | `GET /api/admin/users` with Admin token | 200 OK; returns complete directory across all tenants with roles, plans, quotas | **PASS** |
| **ADM-USER-02** | User Search & Filter | Filter user list by email or name | Directory instantly filters matching researcher records | **PASS** |
| **ADM-USER-03** | Upgrade to Pro Plan | `PATCH /api/admin/users/usr-demo-student/plan` with `{"plan":"pro","reset_quota":true}` | 200 OK; user tier updated to `pro`, quota balance immediately credited to 99 requests | **PASS** |
| **ADM-USER-04** | Upgrade to Enterprise Plan | `PATCH /api/admin/users/usr-demo-student/plan` with `{"plan":"enterprise","reset_quota":true}` | 200 OK; user tier updated to `enterprise`, quota set to 999 | **PASS** |
| **ADM-USER-05** | Downgrade to Free Plan | `PATCH /api/admin/users/usr-demo-student/plan` with `{"plan":"free","reset_quota":true}` | 200 OK; tier reverted to `free`, quota adjusted to 3 requests | **PASS** |
| **ADM-USER-06** | Custom Quota Override | `PATCH /api/admin/users/usr-demo-student/plan` with `{"plan":"pro","quota_remaining":150}` | 200 OK; quota overridden to exactly 150 requests | **PASS** |
| **ADM-USER-07** | Invalid Plan Rejection | `PATCH /api/admin/users/usr-demo-student/plan` with `{"plan":"invalid_tier"}` | 400 Bad Request with allowed tiers list | **PASS** |
| **ADM-USER-08** | Non-Existent User Rejection | `PATCH /api/admin/users/usr-nonexistent/plan` | 404 Not Found | **PASS** |

### 4. Researcher Onboarding
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-ONBD-01** | Onboard New Researcher | `POST /api/admin/users` with name, email, role, plan, tenant | 201 Created; creates user with deterministic ID, plan defaults, and active quota | **PASS** |
| **ADM-ONBD-02** | Duplicate Email Conflict | `POST /api/admin/users` with existing email | 409 Conflict with clear error message | **PASS** |
| **ADM-ONBD-03** | Invalid Tenant Rejection | `POST /api/admin/users` with non-existent tenant ID | 404 Not Found for tenant | **PASS** |

### 5. Global API Configuration & System Mode Control
| ID | Test Item | Target / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ADM-CONF-01** | Global API Key Status | `GET /api/settings/keys` | 200 OK; inspects master encryption status and active model provider | **PASS** |
| **ADM-CONF-02** | Master API Key Update | `POST /api/settings/keys` with production DeepSeek/OpenAI key | 200 OK; securely encrypted with AES-256 for platform-wide LLM fallback | **PASS** |
| **ADM-CONF-03** | Global Mode Switch | `POST /api/settings/mode` | 200 OK; switches system between offline fixture mode and live LLM mode | **PASS** |

---

## 3. Automated Acceptance Test Verification
```
tests/acceptance/test_admin.py .....                     [PASS]
tests/acceptance/test_ai_stress.py ..................... [PASS]
tests/acceptance/test_config_modes.py .                  [PASS]
tests/acceptance/test_tenant_isolation.py .             [PASS]
tests/acceptance/test_uc1_auth.py ..                    [PASS]
tests/acceptance/test_uc2_search.py ..                  [PASS]
tests/acceptance/test_uc4_plan.py .                     [PASS]
tests/acceptance/test_uc_e2e_pipeline.py .              [PASS]
Total: 30 Passed, 1 Skipped, 0 Failed (100% Core Passing Rate)
```
