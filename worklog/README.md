# Worklog & Collaboration Record

This folder tracks handoffs and verification audits between **Antigravity (Builder)** and **Hermes (Verifier)**.

## Collaboration Rules
1. **Builder (Antigravity)**:
   - Plans each milestone before writing code.
   - Writes or updates acceptance tests first (verifying they fail before implementation).
   - Writes application code within the milestone scope.
   - Logs completed milestones, test outputs, and diffs here.

2. **Verifier (Hermes)**:
   - Verifies environment, migrations, and script isolation.
   - Performs automated audits on git diffs using `scripts/verify-hermes.ps1`.
   - Confirms that `blueprint.json` has not been altered (`scripts/guard.ps1`).
   - Assesses release gate evals (`evals/cases.json`).

## Milestones Record
- [x] **Setup**: Repository initialized, Python 3.12 `.venv` created, `docker-compose.dev.yml` created, `scripts/` runners configured, Hermes Verifier hooked up.
