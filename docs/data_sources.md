# MTIS Data Sources Architecture

This document specifies the data acquisition, repository scraping, and reasoning model integrations for the Malaysian Thesis Institution System (MTIS).

---

## 1. Data Ingestion & Provider Architecture

The MTIS backend aggregates institutional literature from Malaysian repositories (UTM) and global academic registries (OpenAlex), routing clean structured papers through an intelligent pipeline powered by DeepSeek / OpenAI with DEMO_MODE deterministic fallback.

```
                              ┌─────────────────────────────────────────┐
                              │           Student / Researcher          │
                              └────────────────────┬────────────────────┘
                                                   │ User Query
                                                   ▼
                                 ┌──────────────────────────────────┐
                                 │     MTIS Gateway Router          │
                                 │       (/api/search)              │
                                 └─────────┬──────────────┬─────────┘
                                           │              │
                   ┌───────────────────────┘              └────────────────────────┐
                   ▼ (MY / INT Scope)                                              ▼ (MY Scope)
       ┌────────────────────────┐                                      ┌───────────────────────┐
       │   OpenAlex REST API    │                                      │ UTM e-repository      │
       │   (polite pool)        │                                      │ (Playwright headless) │
       └───────────┬────────────┘                                      └───────────┬───────────┘
                   │                                                               │
                   │  List[Paper]                                                  │  List[Paper]
                   └───────────────────────┬───────────────────────────────────────┘
                                           │ Aggregated & Deduplicated
                                           ▼
                                 ┌──────────────────────────────────┐
                                 │   State & Reasoning Pipeline     │
                                 │  (Gap -> Title -> Deep -> Plan)  │
                                 └─────────────────┬────────────────┘
                                                   │
                                                   ▼
                                 ┌──────────────────────────────────┐
                                 │    LLM Provider Adapter          │
                                 │    (backend/ai/llm_adapter.py)   │
                                 └─────────┬──────────────┬─────────┘
                                           │              │
                  ┌────────────────────────┴───────┐      └────────────────────────┐
                  ▼ (Primary / Fallback)           ▼ (Fallback)                    ▼ (DEMO_MODE=true)
       ┌────────────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
       │  DeepSeek API (V3)     │──────▶│  OpenAI API          │──────▶│  Local Fixture Engine  │
       │  deepseek-chat         │       │  gpt-4o-mini         │       │  tests/fixtures/*.json │
       └────────────────────────┘       └──────────────────────┘       └────────────────────────┘
                   │                               │                               │
                   └───────────────────────┬───────┴───────────────────────────────┘
                                           │ Log call (tokens, cost_myr, status)
                                           ▼
                               ┌───────────────────────┐
                               │  logs/ai_calls.jsonl  │
                               └───────────────────────┘
```

---

## 2. Source Summary Table

| Source | Type | Auth | Cost | Fallback if down |
| :--- | :--- | :--- | :--- | :--- |
| **OpenAlex** | REST API | email only | free | error shown, other source still used |
| **UTM repo** | Playwright | none | free | ScraperError, OpenAlex still used |
| **LLM** | REST API | API key | paid | DEMO_MODE fixtures |

---

## 3. Data Source Specifications

### 3.1. OpenAlex Academic Registry
- **Endpoint**: `https://api.openalex.org/works`
- **Protocol**: HTTPS REST API with JSON response format.
- **Authentication**: Free polite-pool identifier via `mailto` query parameter (`OPENALEX_EMAIL=your@email.com`). Not a secret; enables high-throughput polite rate limits (up to 10 requests/second).
- **Scope Routing**:
  - `scope="MY"`: Filters for Malaysian institutional affiliation using ROR/country code `institutions.country_code:MY`.
  - `scope="INT"`: Searches global academic literature.
- **Resilience & Fallback**:
  - Network timeouts (10.0s) and HTTP errors raise typed exceptions.
  - If OpenAlex is unavailable, an error is surfaced to the aggregator while institutional scraper results remain fully accessible.

### 3.2. UTM Institutional Repository
- **URL**: `https://eprints.utm.my/cgi/search/archive/simple` (theses.lib.utm.my)
- **Architecture**: DSpace / EPrints institutional archive without a public programmatic API.
- **Acquisition Strategy**: Headless browser automation (Playwright) / HTTP form parser that submits topic queries, navigates paginated search results, and parses document metadata (title, author list, publication year, abstract, and repository link).
- **Test Integrity**: Default test suites and local runs use verified HTML fixtures (`tests/fixtures/utm_search_fixture.html`) ensuring 100% reproducible execution without external network dependence (Rubric D5). Live scraping tests are marked `@pytest.mark.live`.
- **Resilience & Fallback**:
  - Scraper errors or page layout mutations raise typed `ScraperError`.
  - On failure, OpenAlex results continue to be served without interrupting user search flows.

### 3.3. LLM Reasoning Layer
- **Interface**: Unified adapter `complete(prompt: str, schema: type[BaseModel]) -> BaseModel` in `backend/ai/llm_adapter.py`.
- **Primary Provider**: DeepSeek V3 (`deepseek-chat`) via `DEEPSEEK_API_KEY`.
- **Fallback Provider**: OpenAI (`gpt-4o-mini`) via `OPENAI_API_KEY`. If the primary provider's key is not configured, the adapter automatically switches to the fallback provider and issues a structured log warning.
- **Zero-Key / Demo Mode**: When `DEMO_MODE=true`, the system boots without any external API keys and runs the complete multi-stage pipeline using deterministic fixtures (`gap_fixture.json`, `title_fixture.json`, `deepdive_fixture.json`, `plan_fixture.json`).
- **Audit & Cost Honesty**: Every LLM call appends one atomic JSON line to `logs/ai_calls.jsonl`:
  ```json
  {"user": "student@utm.my", "stage": "gap", "model": "deepseek-chat", "tokens": 450, "cost_myr": 0.0035, "status": "ok", "timestamp": "2026-10-22T12:00:00Z"}
  ```
