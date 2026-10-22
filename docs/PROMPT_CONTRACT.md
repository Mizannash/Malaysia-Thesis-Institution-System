# Prompt contracts

One contract per AI feature. Every reply is checked in code before anything uses it. Shared by all of them: output format **JSON fields, checked by code**, failure policy **Always human review**, examples **Two or three**.

## 1. Gap Analysis (F4)
- What the AI does: not chosen.
- When it runs: not chosen.
- Where the result goes: not chosen.
- Used by: Student / Researcher. Model: not decided yet.

### Role
You are the assistant of Malaysian Thesis Institution System (MTIS). Your job: AI analyzes fetched paper abstracts and lists research gaps with citations.

### Input
(what comes in)

### Output
(what goes out)

### Checks (in code, on every reply)
- Syntax: the reply parses.
- Business: every rule above holds.

## 2. Title Suggestions (F5)
- What the AI does: not chosen.
- When it runs: not chosen.
- Where the result goes: not chosen.
- Used by: Student / Researcher. Model: not decided yet.

### Role
You are the assistant of Malaysian Thesis Institution System (MTIS). Your job: AI generates 2–5 thesis titles (tajuk kajian) from identified gaps, EN/BM toggle.

### Input
(what comes in)

### Output
(what goes out)

### Checks (in code, on every reply)
- Syntax: the reply parses.
- Business: every rule above holds.

## 3. Deep-Dive Search (F6)
- What the AI does: not chosen.
- When it runs: not chosen.
- Where the result goes: not chosen.
- Used by: Student / Researcher. Model: not decided yet.

### Role
You are the assistant of Malaysian Thesis Institution System (MTIS). Your job: On chosen title, fetches more specific papers and re-runs gap analysis.

### Input
(what comes in)

### Output
(what goes out)

### Checks (in code, on every reply)
- Syntax: the reply parses.
- Business: every rule above holds.

## 4. Objectives & Methodology (F7)
- What the AI does: not chosen.
- When it runs: not chosen.
- Where the result goes: not chosen.
- Used by: Student / Researcher. Model: not decided yet.

### Role
You are the assistant of Malaysian Thesis Institution System (MTIS). Your job: Generates objectives, research questions, and methodology draft for the chosen title.

### Input
(what comes in)

### Output
(what goes out)

### Checks (in code, on every reply)
- Syntax: the reply parses.
- Business: every rule above holds.

## Failure policy
- Always human review.

## Examples
- Two or three: take them from real requests, with personal data removed; the worked examples above come first.
