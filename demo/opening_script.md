# MTIS Demo Opening Script (Rubric D1 Evidence)

## 1. Payer & Target Audience
- **Target Customer**: Malaysian diploma, undergraduate final-year project (FYP), and postgraduate (Master's & PhD) researchers at Malaysian Higher Education Institutions (HEIs) like UTM, UM, USM, UiTM, and UKM.
- **Payer**: The student/researcher directly via micro-subscription (B2C), or funded through academic laboratory research grants and faculty departmental licenses.

---

## 2. Customer Problem (In Customer's Own Words)
> *"I don't know what to research, or how to make my topic unique enough for a thesis. Every time I meet my supervisor, they tell me: 'You need to find a solid research gap!' But where do I look? I spend weeks searching Google Scholar, UTM Library, and Springer, reading dozens of PDF abstracts, and I still don't know if my gap is defensible."*
>
> *"When I ask generic AI tools like ChatGPT for topics, they make up fake citations or cite international papers that completely ignore the Malaysian industrial or policy context. My university panel will reject that immediately. I need real literature with verified Malaysian context that proves my research is necessary."*

---

## 3. Product Solution: The 5-Stage Guided Pipeline
MTIS is an AI research guide that solves this problem in 5 structured steps:
1. **Topic Search**: Retrieves real, verifiable papers from OpenAlex and local Malaysian repositories (e.g., UTM, MyJurnal) with a Malaysian/International scope toggle.
2. **Gap Analysis**: AI extracts concrete candidate research gaps, with mandatory citation backing (≥2 real papers per gap).
3. **Title Suggestions**: Generates 2–5 defensible thesis titles (*tajuk kajian*) in English or Bahasa Melayu tied directly to the cited gaps.
4. **Deep-Dive Search**: Automatically queries targeted sub-field papers on the chosen title to ensure thoroughness.
5. **Objectives & Methodology**: Drafts research questions, SMART objectives, and a methodology outline formatted for Malaysian academic proposal defenses.

---

## 4. Pricing & Unit Economics (Break-Even Statement)

| Dimension | Metric | Detail |
|---|---|---|
| **Today's Cost to Student** | **~RM50.00 / month** | Manual searching time, paid research tool trials, wasted supervisory hours |
| **MTIS Free Tier** | **RM0** | 3 research gap analyses per day (daily reset), project history saved |
| **MTIS Pro Subscription** | **RM15.00 / student / month** | Unlimited gap searches, deep-dives, methodology exports, and supervisor view |
| **Marginal Cost per Task** | **~RM0.20 / task** | Blended OpenAlex and DeepSeek inference token cost (~1,000 tokens) |
| **Gross Margin** | **>85%** | RM15 revenue vs ~RM1.00 token cost for 5 tasks/month |

### Break-Even Statement:
> *"With fixed infrastructure costs (database, container hosting, uptime monitoring) budgeted at RM450/month, MTIS achieves complete financial break-even with just **33 paying students** across Malaysian universities. At 300 students in Year 1, MTIS generates RM4,500/month in ARR with sustainable profitability."*

---

## 5. Walkthrough Guide (Marker Demonstration)
1. **Sign-In**: Demonstrate Google Sign-In via Supabase Auth (or quick-switch to UTM Student / UTM Supervisor in Demo Mode).
2. **Identity & Tenant Verification**: Show active tenant badge (*Universiti Teknologi Malaysia*) and student role badge.
3. **Workflow Exploration**: Review the 5-stage research progression cards.
4. **Tenant Isolation Test (D2)**: Click *"Test Cross-Tenant Isolation Now"* to prove that a UTM student is strictly blocked (HTTP 403 Forbidden) from accessing Demo University's records.
