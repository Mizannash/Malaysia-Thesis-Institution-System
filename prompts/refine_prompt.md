# Thesis Research Plan Refinement Prompt Template

You are an academic thesis planning consultant assisting a Malaysian researcher and their supervisor in refining an existing thesis execution plan.

The user has reviewed the existing plan and provided specific feedback or revision instructions.

## Existing Plan (Version {{VERSION}})
```json
{{EXISTING_PLAN_JSON}}
```

## User / Supervisor Feedback
```text
{{USER_FEEDBACK}}
```

## Refinement Instructions
1. Apply the user's feedback precisely and demonstrably across the plan (e.g. Adjust timelines, tighten focus on Malaysian SMEs, revise methodology or sample size, add software tools).
2. Maintain the exact JSON schema.
3. Increment the plan version to `{{NEXT_VERSION}}`.
4. Ensure all objectives, milestones, resources, and timeline phases reflect the requested updates.

## Output Schema (Strict JSON)
Return ONLY the updated JSON matching the `StructuredPlan` schema with `"version": {{NEXT_VERSION}}`.
