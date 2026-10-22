# Stack

**DRAFT: not confirmed.** Do not start building until the human confirms it in GigaLab and downloads the pack again.

| Layer | Choice | Why |
|---|---|---|
| Frontend | React (with Vite) | Components for rich, app-like screens; more to learn, the most examples online |
| Backend | Python: FastAPI | GigaLab's own stack: small, fast and typed; you add sign-in and an admin with libraries |
| Database | PostgreSQL | A managed database for many customers and several servers; pgvector adds embeddings |
| Hosting | not decided yet |  |
| Extras | A background job queue for slow work; Redis: cache, chat memory and rate limits (Module 6) | |

## Commands
- Install: `pip install -r requirements.txt`
- Run the tests: `pytest -q`
- Run the app: `uvicorn app.main:app --reload`

## Who looks after it
- Reads best: Python. Team: Just me, with a coding agent. Runs a Linux server: No. Live updates: No.

## Two parts
- `web/` is a separate React (with Vite) app that calls the backend’s JSON API, with its own `npm install` and build.

## Checks from GigaLab
- warn: 2 decisions are still open: Hosting, Model.
- info: React (with Vite) adds a build step and JavaScript to review: plain HTML or htmx is less to look after on your own.
