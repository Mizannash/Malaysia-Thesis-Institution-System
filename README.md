# Malaysian Thesis Institution System (MTIS)

MTIS is an AI-guided academic research co-pilot that helps Malaysian diploma, undergraduate FYP, and postgraduate students identify novel research gaps and generate structured thesis titles, objectives, and methodologies.

---

## 🚀 Quickstart (no API keys needed)

```bash
git clone https://github.com/Mizannash/Malaysia-Thesis-Institution-System.git mtis && cd mtis
cp .env.example .env      # DEMO_MODE=true already works with compose up
make demo                 # or: docker compose up -d db backend frontend
```

Open **http://localhost:3000** in your browser — sign in with:
```
student@demo.test / supervisor@demo.test (see SEED_ACCOUNTS below)
```

### Seed Demonstration Accounts (Zero Keys Required)

The system automatically initializes and seeds two isolated university tenants on first boot:

| Role | Email | Tenant / Institution | Plan | Quota | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Student** | `student@demo.test` | Demo University (`tenant-demo-002`) | Free | 3 daily | Test student workflow, quota limits, and pricing upgrade hooks (D1, D4) |
| **Supervisor** | `supervisor@demo.test` | Demo University (`tenant-demo-002`) | Pro | 99 daily | Test full 5-stage research pipeline and iterative plan refinement (D3, D4) |
| **Admin** | `admin@demo.test` | Demo University (`tenant-demo-002`) | Enterprise | 999 daily | Test tenant administration and institutional analytics |
| **UTM Student** | `ahmad@utm.my` | UTM (`tenant-utm-001`) | Free | 3 daily | Test Malaysian-specific institutional literature and RLS boundaries (D2) |
| **UTM Supervisor** | `siti@utm.my` | UTM (`tenant-utm-001`) | Pro | 99 daily | Test cross-tenant attack refusal (HTTP 403) and isolated supervision (D2) |

---

## 🏛️ Architecture Diagram

```
                               ┌────────────────────────────────────────────────┐
                               │           Next.js 14 Web Frontend              │
                               │            (http://localhost:3000)             │
                               └───────────────────────┬────────────────────────┘
                                                       │ REST API / JWT
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │          FastAPI Backend Application           │
                               │            (http://localhost:8000)             │
                               └───────────┬────────────────────────┬───────────┘
                                           │                        │
                    ┌──────────────────────┘                        └──────────────────────┐
                    ▼                                                                      ▼
       ┌────────────────────────┐                                             ┌────────────────────────┐
       │ Multi-Tenant Context   │                                             │ Data Acquisition Layer │
       │ (app.current_tenant_id)│                                             │ (MY / INT Scope)       │
       └───────────┬────────────┘                                             └───────────┬────────────┘
                   │                                                                      │
                   ▼                                                                      ├─▶ OpenAlex API (Polite Pool)
       ┌────────────────────────┐                                                         └─▶ UTM e-repository (Playwright)
       │ PostgreSQL 17 (RLS)    │                                                                 │
       │ - Row Level Security   │                                                                 ▼
       │ - Forced Tenant Schema │                                             ┌────────────────────────┐
       └────────────────────────┘                                             │  Reasoning Pipeline    │
                                                                              │  (Stages 1 to 5)       │
                                                                              └───────────┬────────────┘
                                                                                          │
                                                                                          ▼
                                                                              ┌────────────────────────┐
                                                                              │  LLM Provider Adapter  │
                                                                              │  (DeepSeek / OpenAI)   │
                                                                              └───────────┬────────────┘
                                                                                          │
                                                                    ┌─────────────────────┴─────────────────────┐
                                                                    ▼                                           ▼
                                                         ┌──────────────────────┐                    ┌──────────────────────┐
                                                         │ Live Model Provider  │                    │ Local Fixture Engine │
                                                         │ (deepseek-chat)      │                    │ (DEMO_MODE=true)     │
                                                         └──────────────────────┘                    └──────────────────────┘
```

---

## 🎬 Demo Video Link & Presentation Script

- **Demo Walkthrough Video**: [MTIS 5-Stage Live Viva Video](https://youtu.be/demo-placeholder) *(or review interactive transcript in [`demo/opening_script.md`](demo/opening_script.md))*.
- **Live Defense Runbook**: Refer to [`docs/viva_runbook.md`](docs/viva_runbook.md) for step-by-step examiner demonstration prompts.
- **Engineering Reflection**: See [`docs/reflection.md`](docs/reflection.md) for architectural trade-offs, including the rejected dynamic vector database proposal.

---

## 📋 Rubric Evidence Map

MTIS satisfies 100% of the course rubric requirements across all 6 dimensions. Full traceability is documented in [`docs/rubric_map.md`](docs/rubric_map.md):

| Dimension | Description | Status | Primary Evidence Location |
| :--- | :--- | :--- | :--- |
| **D1** | **Customer Problem & Value Hook** | **COVERED** | [`docs/opening_script.md`](docs/opening_script.md), [`frontend/src/app/pricing/page.tsx`](frontend/src/app/pricing/page.tsx) |
| **D2** | **Multi-Tenant Database Isolation** | **COVERED** | [`database/init.sql`](database/init.sql), [`tests/acceptance/test_tenant_isolation.py`](tests/acceptance/test_tenant_isolation.py) |
| **D3** | **Workflow State & 5-Stage Pipeline** | **COVERED** | [`backend/app/routers/pipeline.py`](backend/app/routers/pipeline.py), [`tests/acceptance/test_uc4_plan.py`](tests/acceptance/test_uc4_plan.py) |
| **D4** | **AI Contract Layer & Stress Contracts** | **COVERED** | [`backend/app/ai/contract.py`](backend/app/ai/contract.py), [`tests/acceptance/test_ai_stress.py`](tests/acceptance/test_ai_stress.py) |
| **D5** | **Testing, Backups & Cost Honesty** | **COVERED** | [`tests/acceptance/`](tests/acceptance/), [`scripts/db_backup.py`](scripts/db_backup.py), [`docs/cost_per_request.md`](docs/cost_per_request.md) |
| **D6** | **Operational Packaging & Viva Runbook** | **COVERED** | [`docs/viva_runbook.md`](docs/viva_runbook.md), [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md), [`Makefile`](Makefile) |

---

## 🧪 How to Run Tests

### Running with Docker (Zero Host Dependencies)
If your machine has only Docker and Make installed:
```bash
make test
```
Or via Docker Compose directly:
```bash
docker compose run --rm backend pytest tests/acceptance/ -v
```

### Running Locally with Python
If you have a local Python 3.12 environment:
```bash
pip install -r backend/requirements.txt
pytest tests/acceptance/ -v
```

All 24 core acceptance tests execute **100% offline** on verified fixtures (`tests/fixtures/`) without incurring external API costs.

---

## 🔑 How to Enable Live AI Keys

To transition from zero-key `DEMO_MODE` to live production inference:

1. Open your `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Configure your live provider credentials:
   ```env
   # Set DEMO_MODE to false for live model calls
   DEMO_MODE=false

   # Choose provider (deepseek or openai)
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-your-deepseek-key-here
   LLM_MODEL=deepseek-chat

   # (Optional) OpenAI key for automatic fallback
   OPENAI_API_KEY=sk-your-openai-key-here

   # OpenAlex polite pool email (free, NOT a secret)
   OPENALEX_EMAIL=your.email@university.edu.my
   ```

3. Restart the containers:
   ```bash
   docker compose restart backend
   ```
   *Note: If `DEEPSEEK_API_KEY` encounters network timeouts or rate limits, the system automatically falls back to OpenAI and records the fallback in `logs/ai_calls.jsonl`.*

---

## 🛠️ Troubleshooting

If you encounter port conflicts, Docker connection issues, or container latency, consult [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) for exact terminal fixes.
