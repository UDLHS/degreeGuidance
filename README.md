# Degree Guidance — AI-Powered Sri Lankan University Admissions Platform

A student-facing decision aid for Sri Lankan A/L students choosing a university
degree. It combines **deterministic eligibility checking**, **transparent
multi-dimensional ranking**, and a **conversational AI advisor** — all grounded
in the official UGC Z-score handbooks.

> **Status:** deployed to production on Vercel + Render + Supabase + Upstash,
> serving **three years of independently-verified cutoff data** (A/L exam years
> 2022, 2023, 2024) across ~265 courses and 21 universities. ~353 tests passing.

---

## 📚 Full architecture documentation

This README is the front door. The complete, exhaustive reference — every
subsystem, every file, with diagrams — lives in **[`docs/architecture/`](docs/architecture/README.md)**:

| # | Doc | Covers |
| --- | --- | --- |
| 01 | [System Overview](docs/architecture/01-system-overview.md) | the whole machine + the yearly loop |
| 02 | [Tech Stack](docs/architecture/02-tech-stack.md) | every dependency + the non-choices |
| 03 | [Data Model](docs/architecture/03-data-model.md) | tables, ER diagram, year convention |
| 04 | [Ingestion Pipeline](docs/architecture/04-ingestion-pipeline.md) | PDF → cutoffs |
| 05 | [Eligibility Engine](docs/architecture/05-eligibility-engine.md) | the deterministic core |
| 06 | [Scoring & Recommendations](docs/architecture/06-scoring-recommendations.md) | ranking + the three tabs |
| 07 | [RAG Knowledge](docs/architecture/07-rag-knowledge.md) | pgvector + FTS + RRF |
| 08 | [AI Agent](docs/architecture/08-ai-agent.md) | the tool loop, no LangChain |
| 09 | [Admin Backend](docs/architecture/09-admin-backend.md) | every admin endpoint |
| 10 | [Admin Frontend](docs/architecture/10-admin-frontend.md) | every admin page |
| 11 | [Student Frontend](docs/architecture/11-student-frontend.md) | the flow, tabs, BFF |
| 12 | [Infrastructure](docs/architecture/12-infrastructure-deployment.md) | the split-service topology |
| 13 | [Auth & Security](docs/architecture/13-auth-security.md) | JWT, BFF token injection |
| 14 | [Testing & Quality](docs/architecture/14-testing-quality.md) | the oracle, 353 tests |
| 15 | [File Map](docs/architecture/15-file-map.md) | what every file does |
| 16 | [Design Decisions](docs/architecture/16-design-decisions.md) | the why + war stories |

---

## What it does

1. **Eligibility check (deterministic, no LLM).** The student enters Z-score,
   district, stream, and three A/L subjects. A single SQL query returns every
   course they'd qualify for under the latest cutoffs — classified `eligible` /
   `conditional` (aptitude-test) / not-eligible. Correctness is non-negotiable
   here, so no language model touches this path. → [05](docs/architecture/05-eligibility-engine.md)

2. **Personalised ranking (three tabs).** Eligible courses are scored on a
   transparent five-dimension weighted scale and split into **Safe** and
   **Consider**, ordered highest-cutoff-first when the student states no
   preferences. A third **Ambitious** tab surfaces courses just *above* their
   score (within +0.15) that later UGC selection rounds have historically
   admitted. → [06](docs/architecture/06-scoring-recommendations.md)

3. **Conversational AI advisor.** A single Gemini agent with five tools (course
   lookup, cutoff trend, factsheet RAG, course search, trust-ranked web search)
   that already knows the student's verified eligible list and never recommends
   a course out of reach. → [08](docs/architecture/08-ai-agent.md)

Behind it all is the **yearly loop**: an admin uploads a new handbook PDF, the
worker extracts the cutoff grid, the admin reviews the column mapping and
promotes — and students immediately see the new year with trend deltas. Built to
run every year, forever, with nothing hardcoded per year. → [04](docs/architecture/04-ingestion-pipeline.md)

---

## Tech stack (summary)

Full detail + reasoning in **[02-tech-stack.md](docs/architecture/02-tech-stack.md)**.

**Backend** — Python 3.13, FastAPI + Uvicorn, SQLAlchemy 2 (async) + asyncpg,
Alembic (43 migrations), Pydantic v2, **arq** (Redis job queue), **pdfplumber**
(PDF), **pgvector** (embeddings in Postgres — no separate vector DB),
**google-genai** (Gemini `gemini-3.1-flash-lite` chat + `gemini-embedding-001`
768-dim embeddings), **ddgs** (DuckDuckGo). Managed by **uv**.

**Frontend** — Next.js 14 (App Router), TypeScript, Tailwind, Radix/shadcn,
NextAuth v5.

**Infrastructure** — Vercel (web + BFF), Render (FastAPI **api** + arq **worker**
as separate services), Supabase (Postgres + pgvector, via the Session Pooler),
Upstash (Redis, TLS), Google Gemini.

**Deliberate non-choices:** no LangChain (hand-written agent + RAG), no Pinecone
(pgvector), no Celery (arq), no OpenAI/Anthropic in prod (Gemini free/cheap
tier), no microservices (modular monolith). → [16](docs/architecture/16-design-decisions.md)

---

## Repository layout

```
degree-guidance/
├── apps/
│   ├── api/         FastAPI service — routers, deps, guards, queue   → 09,13
│   └── worker/      arq worker — PDF extraction, factsheet/article indexing → 04,07
├── core/            Shared domain logic (no HTTP/UI)
│   ├── eligibility/ Deterministic SQL engine                          → 05
│   ├── scoring/     Pure-Python scorer + recommendation service       → 06
│   ├── rag/         Hybrid pgvector + FTS + RRF retrieval             → 07
│   ├── chat/        Gemini agentic loop + tools + config              → 08
│   ├── ingestion/   Grid extractor, artifact store, chunked reads     → 04
│   ├── models/      SQLAlchemy ORM                                     → 03
│   └── schemas/     Pydantic contracts
├── web/             Next.js 14 frontend (student + admin)             → 10,11
├── alembic/         43 additive migrations                            → 03
├── content/factsheets/   129 per-course markdown factsheets           → 07
├── data/            Raw handbooks, extracted CSVs, seeds
├── scripts/         PDF extractor, prod migration runner              → 04,12
├── tests/           ~353 unit + integration tests                     → 14
└── docs/architecture/    ← the full documentation set
```

Every file annotated in **[15-file-map.md](docs/architecture/15-file-map.md)**.

---

## Running locally

Backend runs in **Ubuntu on WSL2** (pgvector and asyncpg are Linux-first);
Node via **nvm**, Python via **uv**, Redis native in WSL (no Docker).

```bash
# 1. Redis (native in WSL) — ensure it's running
redis-cli ping    # -> PONG

# 2. Python deps
uv sync

# 3. Postgres 16 + pgvector, then env
cp .env.example .env     # set DATABASE_URL(+_SYNC), GEMINI_API_KEY, JWT_SECRET_KEY, REDIS_URL
uv run alembic upgrade head

# 4. Start the API
uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8077 --reload

# 5. Start the worker (separate terminal)
uv run arq apps.worker.settings.WorkerSettings

# 6. Frontend (separate terminal)
cd web && npm install && npm run dev   # http://localhost:3000
```

Local env needs `DATABASE_URL` (asyncpg) + `DATABASE_URL_SYNC` (psycopg2, for
Alembic), `GEMINI_API_KEY`, `JWT_SECRET_KEY`, `REDIS_URL`. The frontend needs
`AUTH_SECRET` / `API_BASE_URL`. Full env + the production topology in
**[12-infrastructure-deployment.md](docs/architecture/12-infrastructure-deployment.md)**.

---

## Running tests

```bash
uv run pytest                       # all ~353
uv run pytest tests/unit/           # pure logic, no DB
uv run pytest tests/integration/    # against a test database
```

The suite guards a system where wrong data hurts real students — its standout
patterns (the eligibility **oracle**, sentinel-year isolation, split-instance
artifact tests, coverage-gap pins) are described in
**[14-testing-quality.md](docs/architecture/14-testing-quality.md)**.

---

## Migrations

Locally: `uv run alembic upgrade head`. In **production**, migrations are applied
by hand-reviewed, version-guarded SQL via `scripts/apply_prod_migrations.py`
(Alembic-direct has SSL friction against Supabase) — see
**[12-infrastructure-deployment.md](docs/architecture/12-infrastructure-deployment.md)**.

---

## The year convention (important)

A cutoff dataset's `year` is the **A/L examination year** from the book's own
header, and **`handbook_YYYY.pdf` carries exam YYYY−1 cutoffs** (the 2025 book →
exam 2024). When uploading, enter the **exam year**, not the file year — getting
this wrong duplicates a dataset. → [03](docs/architecture/03-data-model.md),
[16 §2.4](docs/architecture/16-design-decisions.md)

---

*This platform is a decision aid, not a guarantee. Z-score cutoffs change every
year with applicant numbers and available seats. Always verify against the
official UGC handbook before applying.*
