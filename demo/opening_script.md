# MTIS Demo Opening Script (Rubric D1 Evidence)

## 1. Payer & Target Audience
- **Target Customer**: Malaysian diploma, undergraduate final-year project (FYP), and postgraduate (Master's & PhD) researchers at Malaysian Higher Education Institutions (HEIs) including Universiti Teknologi Malaysia (UTM), Universiti Malaya (UM), Universiti Sains Malaysia (USM), Universiti Teknologi MARA (UiTM), and Universiti Kebangsaan Malaysia (UKM).
- **Payer**: The student/researcher directly via micro-subscription (B2C: RM15.00/month), or funded through faculty departmental software licenses and academic research grant allocations (B2B/Institutional).

---

## 2. Customer Problem (In Customer's Own Words)
> *"I don't know what to research, or how to make my topic unique enough for a thesis. Every time I meet my supervisor, they tell me: 'You need to find a solid research gap!' But where do I look? I spend weeks searching Google Scholar, UTM Library, and Springer, reading dozens of PDF abstracts, and I still don't know if my gap is defensible."*
>
> *"When I finally propose a title, my supervisor asks: 'What are your specific research objectives? What is your timeline and methodology?' Draft proposal rejections cost me entire semesters. At RM2,500 to RM5,000 per semester in tuition and living allowances, a stalled proposal is a massive financial and mental drain. Generic AI tools hallucinate fake citations or provide vague advice that ignores Malaysian institutional formatting."*

---

## 3. Product Solution & The Primary Value Proposition: Structured Plan Generation
MTIS is an AI research guide that accompanies the researcher from raw query to a fully defense-ready thesis execution plan across 5 stages:
1. **Topic Search**: Retrieves real, verifiable papers from OpenAlex and local Malaysian repositories (e.g., UTM, MyJurnal) with a Malaysian/International scope toggle.
2. **Gap Analysis**: AI extracts concrete candidate research gaps backed by mandatory citations (≥2 verified papers per gap).
3. **Title Suggestions**: Generates 2–5 defensible thesis titles (*tajuk kajian*) in English or Bahasa Melayu tied directly to cited gaps.
4. **Deep-Dive Search**: Automatically queries targeted sub-field papers on the chosen title to ensure thoroughness.
5. **Stage 5 Plan Generation & Iterative Refinement (The Core Value Hook)**:
   - **Structured Execution Plan**: Synthesizes the entire project context into a defense-ready plan covering research objectives, key milestone deliverables, necessary resources, and a high-level timeline.
   - **Iterative Refinement Loop**: Directly solves supervisor feedback cycles (e.g., *"Too ambitious: focus on Malaysian SMEs only"*, *"Reduce timeline to 18 months"*). The agent adapts objectives, milestones, and timeline tasks through targeted repair prompts, persisting new versioned plans (`plan_version`, `last_refined_at`) directly to PostgreSQL.

---

## 4. Pricing, Unit Economics & Break-Even Analysis

### A. The Student's Break-Even (Value ROI)
- **Tuition Cost of a 1-Semester Proposal Delay**: **RM2,500 – RM5,000** in Malaysian public/private universities.
- **Cost of MTIS Pro Subscription**: **RM15.00 / month** (or RM0 on the Free Tier with 3 daily runs).
- **Break-Even Metric**: If MTIS saves just **3 days of research dead-ends** or prevents **1 draft proposal rejection** by a supervisory committee, the student achieves a **>160x return on investment** relative to the RM15 cost.

### B. The Platform's Break-Even & Unit Economics

| Dimension | Metric | Detail |
|---|---|---|
| **Today's Cost to Student** | **~RM50.00 / month** | Manual searching time, paid research tool trials, wasted supervisory hours |
| **MTIS Free Tier** | **RM0** | 3 research pipeline generations per day (daily reset), project history saved |
| **MTIS Pro Subscription** | **RM15.00 / student / month** | Unlimited pipeline searches, deep-dives, plan refinement loop, and supervisor view |
| **Marginal Cost per Full Plan** | **~RM0.20 / task** | Blended OpenAlex and DeepSeek inference token cost (~1,500 tokens across 5 stages) |
| **Gross Margin** | **>85%** | RM15 revenue vs ~RM1.20 token cost for 6 full plan generations/month |

### Platform Break-Even Statement:
> *"With fixed infrastructure costs (PostgreSQL, container orchestration, uptime monitoring) budgeted at RM450/month, MTIS achieves complete financial break-even with just **33 paying students** across Malaysian universities. At 300 paying students in Year 1, MTIS generates RM4,500/month (RM54,000 ARR) with an operating gross margin exceeding 85%."*

---

## 5. Walkthrough Guide (Marker Demonstration)
1. **Sign-In & Identity (D2)**: Sign in via Google Auth or Demo Mode (UTM Student / UTM Supervisor). Active tenant badge (*Universiti Teknologi Malaysia*) confirms multi-tenant session isolation.
2. **Data Acquisition (D3/D5)**: Search `"E-wallet adoption in Malaysian SMEs"` with Malaysian repository scope enabled.
3. **Reasoning Pipeline (D4)**: Progress through Stage 2 (Gap Analysis with citation check), Stage 3 (Title Suggestions in EN/BM), and Stage 4 (Deep-Dive literature search).
4. **Plan Studio & Versioned Refinement (D1/D3)**:
   - Navigate to `/plan` to review the synthesized structured thesis plan (Version 1).
   - Inspect Research Objectives, Key Milestones, Resources, and Timeline.
   - Enter supervisor feedback: *"Too ambitious: please focus specifically on Malaysian SMEs and reduce timeline to 18 months."*
   - Trigger the refinement loop: watch the agent update to **Version 2**, display the diff summary, and persist the new state to PostgreSQL with `last_refined_at`.
5. **Operational Integrity (D5)**: Execute `scripts/db_backup.py` and `scripts/db_restore.py` to confirm zero-downtime backup readiness.
