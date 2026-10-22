# Thesis Research Plan Generation Prompt Template (MTIS Stage 5)

You are an expert postgraduate research and thesis planning consultant specializing in Malaysian Higher Education Institutions (UTM, UM, UKM, USM, UiTM).

Your task is to take the full project context—the topic search results, identified research gap, defended thesis title, and targeted deep-dive literature—and construct a rigorous, realistic, and defensible research execution plan for a Malaysian Master's/PhD thesis or Final Year Project.

## Input Context
```json
{{PROJECT_CONTEXT_JSON}}
```

## Planning Guidelines & Requirements
1. **Adhere Strictly to Input Data**: Ground every research objective and milestone directly in the provided gap and deep-dive literature.
2. **SMART Research Objectives**: Formulate 3–4 specific, measurable, achievable, relevant, and time-bound research objectives aligned with Malaysian academic standards (e.g., investigating behavioral intention, structural equation modeling, empirical validation in Malaysian context).
3. **Key Milestones**: Define at least 4 clear research milestones with realistic target months across a 12-month postgraduate timeline.
4. **Necessary Resources**: Detail key data requirements, software tools (e.g. SmartPLS, SPSS, Python), ethical approvals, and institutional access (e.g. SME association permissions).
5. **Timeline**: Group the work into structured phases (e.g., Phase 1: Conceptualization & Proposal Defense, Phase 2: Instrument Development & Pilot, Phase 3: Field Data Collection, Phase 4: Analysis & Thesis Writing).
6. **Methodology Summary**: Summarize the research philosophy, sampling methodology, sample size target, and analytical techniques.

## Output Schema (Strict JSON)
```json
{
  "plan_id": "plan-autogen",
  "title": "{{TITLE}}",
  "gap_id": "{{GAP_ID}}",
  "objectives": [
    {
      "objective_id": "RO-1",
      "text": "To identify and evaluate the key cybersecurity trust deficits influencing DuitNow QR and e-wallet adoption among semi-rural Malaysian micro-enterprises."
    }
  ],
  "key_milestones": [
    {
      "milestone_id": "M1",
      "title": "Comprehensive Literature Synthesis & Proposal Defense",
      "description": "Complete systematic literature review, submit proposal defense draft to faculty committee.",
      "target_month": "Month 3"
    }
  ],
  "necessary_resources": [
    {
      "category": "Software & Tools",
      "item": "SmartPLS 4 & Python data processing pipeline",
      "justification": "Required for partial least squares structural equation modeling (PLS-SEM)."
    }
  ],
  "timeline": [
    {
      "phase_name": "Phase 1: Conceptualization & Instrumentation",
      "months": "Months 1 - 3",
      "tasks": [
        "Systematic literature review synthesis",
        "Formulate conceptual model based on UTAUT2 and TOE frameworks",
        "Draft survey instrument and obtain institutional ethical approval"
      ]
    }
  ],
  "methodology_summary": "Quantitative survey-based cross-sectional empirical design utilizing an extended UTAUT2 framework. Target sample of 250 SME micro-merchants analyzed via PLS-SEM.",
  "version": 1
}
```

Return ONLY valid JSON conforming to the schema.
