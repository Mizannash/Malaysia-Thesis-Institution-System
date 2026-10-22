# Requirements

Version 1: **The must-haves only**. The source of truth is `blueprint.json`; this file explains it.

## Roles
| Role | What they do |
|---|---|
| Owner | Runs the business, pays for hosting/API costs, monitors usage and subscriptions |
| Student / Researcher | Signs in, runs research gap searches, saves and exports results |
| Admin (add via "+ Add a role") | Manages users, quotas, and abuse monitoring |

## Features
| Id | Feature | Priority | Used by | AI | What it does |
|---|---|---|---|---|---|
| F1 | Auth | Must, version 1 | Student / Researcher |  | Sign up / sign in with Google or email-password |
| F2 | Auth | Must, version 1 | Owner |  | Sign up / sign in with Google or email-password |
| F3 | Topic Search | Must, version 1 | Student / Researcher |  | Student enters a topic + MY/INT toggle; system fetches real papers from OpenAlex and UTM repository |
| F4 | Gap Analysis | Must, version 1 | Student / Researcher | yes | AI analyzes fetched paper abstracts and lists research gaps with citations |
| F5 | Title Suggestions | Must, version 1 | Student / Researcher | yes | AI generates 2–5 thesis titles (tajuk kajian) from identified gaps, EN/BM toggle |
| F6 | Deep-Dive Search | Must, version 1 | Student / Researcher | yes | On chosen title, fetches more specific papers and re-runs gap analysis |
| F7 | Objectives & Methodology | Must, version 1 | Student / Researcher | yes | Generates objectives, research questions, and methodology draft for the chosen title |
| F8 | Usage Quota | Must, version 1 | Owner |  | Limits free trial users to 3 generations/day; resets daily |
| F9 | Usage Quota | Must, version 1 | Student / Researcher |  | Limits free trial users to 3 generations/day; resets daily |
| F10 | Project History | Must, version 1 | Student / Researcher |  | Saves each research session; user can reopen past projects |
| F11 | Export to Word/PDF | Should | Student / Researcher |  | Download full research pack (gaps, titles, objectives, methodology) |
| F12 | Subscription & Payment | Should | Owner |  | Upgrade to paid plan after trial (online payment) |
| F13 | Subscription & Payment | Should | Student / Researcher |  | Upgrade to paid plan after trial (online payment) |
| F14 | Citation Checker | Should | Student / Researcher |  | Verifies every AI claim links to a real DOI/URL before display |
| F15 | Admin Dashboard | Could | Owner |  | View users, usage stats, active subscriptions |
| F16 | Plagiarism-style similarity scan | Won’t |  |  | Compare suggested title against existing theses |
| F17 | Full-text PDF reading | Won’t |  |  | AI reads entire papers, not just abstracts |
| F18 | Reference manager (Mendeley/Zotero) export | Won’t |  |  | Push citations to reference tools |

## Use cases (version 1)

### UC1 · Auth (F1)
- Actor: Student / Researcher
- Goal: UC1 — Sign in

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f1_auth.py`):
- AC1.1 Given a new user, when they sign up with Google, then an account is created and they land on the dashboard within 5 seconds

### UC2 · Auth (F2)
- Actor: Owner
- Goal: Sign up / sign in with Google or email-password

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f2_auth.py`):
- (not written: the test file holds one failing reminder)

### UC3 · Topic Search (F3)
- Actor: Student / Researcher
- Goal: Search papers

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f3_topic_search.py`):
- AC3.1 Given topic "e-wallet adoption SME Malaysia" with MY toggle on, when they search, then ≥10 real papers with titles, years, DOIs/URLs display within 30 seconds

### UC4 · Gap Analysis (F4)
- Actor: Student / Researcher
- Goal: Find gaps

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f4_gap_analysis.py`):
- AC4.1 Given fetched papers, when gap analysis runs, then ≥3 gaps are shown and every gap cites ≥2 papers from the fetched set (no uncited claims)

### UC5 · Title Suggestions (F5)
- Actor: Student / Researcher
- Goal: Get titles

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f5_title_suggestions.py`):
- AC5.1 Given gaps, when generating, then 2–5 titles appear, each traceable to a cited gap, in the selected language

### UC6 · Deep-Dive Search (F6)
- Actor: Student / Researcher
- Goal: Deep dive

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f6_deep_dive_search.py`):
- AC6.1 Given a chosen title, when the student confirms, then a new refined paper set for that title is fetched and gap-analyzed

### UC7 · Objectives & Methodology (F7)
- Actor: Student / Researcher
- Goal: Get objectives & methodology

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f7_objectives_methodology.py`):
- AC7.1 Given a chosen title, when generation completes, then objectives, research questions, and a methodology outline display, each referencing the refined papers

### UC8 · Usage Quota (F8)
- Actor: Owner
- Goal: Limits free trial users to 3 generations/day; resets daily

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f8_usage_quota.py`):
- (not written: the test file holds one failing reminder)

### UC9 · Usage Quota (F9)
- Actor: Student / Researcher
- Goal: Quota enforcement

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f9_usage_quota.py`):
- AC9.1 Given a free-trial user who has used 3 generations today, when they attempt a 4th, then they are blocked with an upgrade/wait message and quota resets after midnight

### UC10 · Project History (F10)
- Actor: Student / Researcher
- Goal: Reopen project

Main steps:
(not written)

Errors and edge cases:
- (not written)

Acceptance criteria (tests in `tests/acceptance/test_f10_project_history.py`):
- AC10.1 Given a saved session, when the user opens History, then all previous searches, gaps, and titles reload exactly

## Integrations
- File uploads
- Email sending
- Online payment
- OpenAlex API (paper search), Semantic Scholar API (backup search), UTM institutional repository scraper (Playwright), OpenAI API, DeepSeek API, Supabase Auth (Google sign-in)

## Platforms
- A web app (works on phones too)
- An admin back office for you

## Out of scope for version 1
- Plagiarism-style similarity scan
- Full-text PDF reading
- Reference manager (Mendeley/Zotero) export
- Mobile apps (iOS/Android)
- WhatsApp/chat interface
- Full-text PDF analysis of papers
- Plagiarism/similarity checker
- Reference manager export (Zotero/Mendeley)
- Multi-university library integrations beyond UTM
- Team/ supervisor collaboration features
- Anything not listed above.

## Data
See docs/DATA_MODEL.md.
