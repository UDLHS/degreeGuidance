# Degree Guidance — AI-Powered Sri Lankan University Admissions Platform

An intelligent, student-facing decision aid for Sri Lankan A/L students choosing their university degree programme. The platform combines deterministic eligibility checking, transparent multi-dimensional scoring, and a conversational AI advisor — all grounded in the official UGC Z-score handbooks.

> **Status:** Active development — Week 5 of 8. Core student flow is production-ready. Chatbot advisor with live web search is live. Admin panel is operational.

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [Why This Exists](#why-this-exists)
3. [Architecture Overview](#architecture-overview)
4. [Tech Stack](#tech-stack)
5. [Key Techniques & Why They Were Chosen](#key-techniques--why-they-were-chosen)
6. [Project Structure](#project-structure)
7. [Data Pipeline](#data-pipeline)
8. [The AI Advisor (Chatbot)](#the-ai-advisor-chatbot)
9. [The Eligibility Engine](#the-eligibility-engine)
10. [The Scoring Engine](#the-scoring-engine)
11. [Admin Panel](#admin-panel)
12. [Database Schema](#database-schema)
13. [Why Ubuntu / WSL2](#why-ubuntu--wsl2)
14. [Environment Setup](#environment-setup)
15. [Running Locally](#running-locally)
16. [Running Tests](#running-tests)
17. [Alembic Migrations](#alembic-migrations)
18. [Environment Variables](#environment-variables)
19. [Development Roadmap](#development-roadmap)

---

## What It Does

Sri Lankan A/L students face a difficult, high-stakes decision every year: which degree programme to apply for across 21 state universities, 261 degree codes, and a district-quota system that makes the same degree eligible for a student in Colombo but not for the same score in Kandy. The official UGC handbook is 200+ pages. Students typically rely on word-of-mouth, older siblings, or tuition masters — not data.

This platform does three things, in sequence:

### 1 — Eligibility Check (deterministic, no LLM)
The student enters their Z-score, district, and A/L stream. The engine runs a pure SQL query against the UGC cutoff database and returns every course where the student would have qualified based on the most recently published cutoffs. The result is classified into three states:

- **Eligible** — Z-score ≥ cutoff, no aptitude test required
- **Conditional** — Z-score ≥ cutoff, but the course requires an aptitude test (Architecture, Music, Fine Arts, etc.)
- **Not eligible** — filtered out entirely; never shown

### 2 — Personalised Ranking
Eligible courses are ranked using a transparent five-dimension weighted score. The dimensions are: Z-score safety margin, university preference, interest alignment, career goal alignment, and industry outlook. The LLM never touches a score — it only generates a short explanation after the rank has been computed. Currently the first two dimensions are active (producing honest recommendations even when the student has no stated preferences).

### 3 — Conversational AI Advisor
After seeing their ranked results, the student can open a floating chat panel and ask anything: "What do engineers actually earn in Sri Lanka?", "Is the cutoff for ECS rising or falling?", "I like robotics — which of my eligible courses fits best?" The advisor knows the student's full profile (Z-score, district, stream, subjects, and the verified list of courses they can get into) and is backed by five tools that search the database, a curated knowledge base, and the live web.

---

## Why This Exists

No existing tool in Sri Lanka:
- Gives a student a **personalised, data-driven shortlist** based on actual UGC cutoffs
- **Explains** why a course is or isn't reachable in their specific district
- Provides a **conversational follow-up** that cites the actual handbook, factsheets, and trusted web sources
- Shows **multi-year cutoff trends** so a student can see whether a programme is getting harder or easier to enter
- Is **free to the student** and runs without requiring an account

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Student's Browser                       │
│  Next.js 14 (App Router)  ·  Tailwind  ·  shadcn/ui     │
└──────────────┬──────────────────────────┬───────────────┘
               │ /api/bff/*  (auth-gated) │ /api/public/* (open)
               ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│              Next.js Route Handlers (BFF)                │
│   Proxy layer — attaches JWT, forwards to FastAPI        │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP  localhost:8077
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI  (apps/api)                       │
│  /eligibility  /recommendations  /chat  /admin/*  /auth  │
└───────────┬───────────────────────┬─────────────────────┘
            │                       │
            ▼                       ▼
┌───────────────────┐   ┌─────────────────────────────────┐
│  PostgreSQL 16    │   │  Arq Worker  (apps/worker)       │
│  + pgvector ext.  │   │  PDF OCR → CSV ingestion         │
│                   │   │  Factsheet indexing (embedding)  │
│  All structured   │   └───────────────┬─────────────────┘
│  data lives here  │                   │ Redis 7 (job queue)
└───────────────────┘   ┌──────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │  Docker (Redis 7)  │
            │  localhost:6379    │
            └────────────────────┘
                        │
                        ▼ (for AI features)
            ┌────────────────────┐
            │  Google Gemini API │
            │  gemini-3.1-flash  │ (free tier)
            │  text-embedding-   │
            │  004  (768 dims)   │
            └────────────────────┘
```

**Design principle: modular monolith.** One repo, two processes (`api` + `worker`), shared `core/` package, single Postgres. This is intentionally not microservices — the domain is cohesive, the team is one person, and a monolith is easier to reason about, deploy, and hand over.

---

## Tech Stack

### Backend

| Layer | Technology | Version | Why |
|---|---|---|---|
| Language | Python | 3.13 | Async-native, rich ML/data ecosystem |
| API framework | FastAPI | 0.115 | Async, automatic OpenAPI docs, Pydantic integration |
| ASGI server | Uvicorn | 0.32 | Production-grade, supports graceful shutdown |
| ORM | SQLAlchemy (async) | 2.0 | Type-safe, full async support via asyncpg |
| DB driver | asyncpg | 0.29 | Fastest async Postgres driver for Python |
| Migrations | Alembic | 1.13 | Industry standard for SQLAlchemy-backed schemas |
| Background jobs | Arq | 0.28 | Async job queue on Redis — lightweight, no Celery overhead |
| Auth | PyJWT + bcrypt | 2.13 / 5.0 | Stateless JWT for admin, bcrypt for password hashing |
| Config | pydantic-settings | 2.3 | Type-safe `.env` parsing with validation |
| PDF extraction | pdfplumber | 0.11 | Accurate table extraction from UGC handbooks |
| AI / LLM | google-genai | 1.0 | Gemini API SDK — free tier, no billing required |
| Vector DB | pgvector | 0.3 | Postgres extension — no separate vector DB needed |
| Web search | ddgs | 9.14 | DuckDuckGo search — free, no API key, async-safe |
| Linter | ruff | 0.15 | Replaces flake8 + isort + black in one fast tool |
| Type checker | mypy | 1.10 | Catches type errors before runtime |
| Test framework | pytest + pytest-asyncio | 8.2 | Full async test support |
| Package manager | uv | latest | 10–100× faster than pip; reproducible lockfile |

### Frontend

| Layer | Technology | Version | Why |
|---|---|---|---|
| Framework | Next.js | 14.2 | App Router, RSC, built-in API routes for BFF |
| Language | TypeScript | 5 | Type safety across the entire frontend |
| Styling | Tailwind CSS | 3.4 | Utility-first — fast to build, easy to maintain |
| Component library | shadcn/ui + Radix UI | latest | Accessible, unstyled primitives — no design lock-in |
| Auth | NextAuth v5 (Auth.js) | 5.0-beta | Session management, server-side token handling |
| Icons | Lucide React | 1.18 | Consistent icon set, tree-shakeable |
| Toasts | Sonner | 2.0 | Lightweight, accessible toast notifications |

### Infrastructure

| Component | Technology | Why |
|---|---|---|
| Database | PostgreSQL 16 | ACID compliance, pgvector extension, JSON support |
| Vector extension | pgvector | Avoids a separate Pinecone/Weaviate — one database, one backup |
| Job queue broker | Redis 7 (Docker) | Required by Arq; also used for session caching |
| Container | Docker (Redis only) | Postgres and Python run natively in WSL for performance |
| Dev environment | Ubuntu 22.04 on WSL2 | See [Why Ubuntu / WSL2](#why-ubuntu--wsl2) |
| Node version manager | nvm | Per-project Node versions without sudo |

---

## Key Techniques & Why They Were Chosen

### Deterministic Eligibility (No LLM on the critical path)

The eligibility check is 100% SQL. It joins `z_score_cutoffs`, `course_stream_eligibility`, and `districts` and filters with bound parameters. No neural network, no language model, no fuzzy matching. The reason: **correctness is non-negotiable here**. If a student is told they're eligible for a course and they're not, that's a consequential error. A hallucinating LLM has no place on this decision path.

Every result carries:
- **Three-state classification**: `eligible` / `conditional` / `not_eligible`
- **Confidence tier**: `current` / `previous_year` / `estimated` — based on how old the cutoff data is relative to the newest year loaded in the database
- **Marginal flag**: set when `student_z − cutoff_z ≤ 0.05`, warning that a small cutoff shift could flip the result next year
- **Audit log**: every query writes a hash-keyed row to `eligibility_audit` for reproducibility

### Hybrid RAG Retrieval (pgvector + FTS + RRF)

The knowledge base (50 curated degree factsheets in `content/factsheets/`) is indexed using two parallel retrieval methods:

**1. Semantic search (pgvector)**
Each factsheet is chunked into ~300-token segments, embedded with Gemini `text-embedding-004` (768 dimensions), and stored in pgvector. At query time the query is embedded and an `<=>` cosine distance search returns the top-20 semantically similar chunks.

**2. Full-text search (PostgreSQL FTS)**
The same chunks are indexed in a `tsvector` column with English stemming. A `plainto_tsquery` search returns the top-20 keyword matches.

**3. Reciprocal Rank Fusion (RRF)**
The two ranked lists are fused using the RRF formula:

```
score = Σ  1 / (k + rank_i)     where k = 60
```

The top-5 fused chunks are passed to the chatbot as context.

**Why RRF?** Pure semantic search misses exact course codes ("008B"), specific Z-score numbers, and proper nouns. Pure keyword search misses paraphrases. RRF captures both and consistently outperforms either alone without requiring a trained re-ranker. It's a free, zero-latency improvement over either method alone.

**Why pgvector instead of Pinecone/Weaviate?** The entire dataset (311 chunks) fits comfortably in Postgres. Adding a second datastore means a second backup, second connection pool, second failure mode, and second billing item. pgvector gives exact cosine search with an HNSW index — at 311 vectors, it's effectively instant.

### Agentic Chatbot with 5 Tools

The chatbot uses a manual Gemini function-calling loop (not LangChain, not LlamaIndex) with up to 6 tool turns per message. The five tools are:

| Tool | What it does | When used |
|---|---|---|
| `find_course` | Fuzzy search on courses table by name/abbreviation. Expands shorthand ("ECS" → "Electronics Computer Science") before querying. 20+ abbreviation mappings, 3-strategy fallback. | Any time the student mentions a course by name or nickname |
| `lookup_course` | Full degree factsheet + Z-score cutoffs for a 3-digit course number. | Any question about a specific degree |
| `get_cutoff_trend` | Year-by-year Z-score history (2019–2023) for a course-university code. | "Is the cutoff rising?" / multi-year questions |
| `search_knowledge` | Hybrid RAG retrieval over 50 factsheets. | Curriculum, career paths, degree comparisons |
| `search_web` | Live DuckDuckGo search filtered to trusted domains. | Salary data, job market, professional body requirements |

The `search_web` tool uses a trusted-domain scoring function. Results from `.gov.lk`, `.ac.lk`, `ugc.ac.lk`, `iesl.lk`, `slmc.lk`, `worldbank.org`, `ilo.org`, and established financial media are ranked higher and tagged `[Trusted source]`.

**Why function-calling over a single large prompt?** Because the chatbot needs data the model doesn't have in its weights: this year's exact Z-score cutoff, a specific university's curriculum, current graduate salary in Sri Lanka. Embedding 261 courses × 5 years of cutoffs in the context window would be impractical. Tools fetch exactly what each question needs.

**Why Gemini and not Anthropic/OpenAI?** The chatbot runs entirely on Google Gemini's **free tier**. `text-embedding-004` is free with no rate limit. `gemini-3.1-flash-lite` handles the agentic loop at zero cost. The student pays nothing; the developer pays nothing during development.

**Why DuckDuckGo and not Google Search API?** Google's Custom Search API requires billing. DuckDuckGo (`ddgs` package) is free, requires no API key, and is safe to call from an async executor via `loop.run_in_executor`. The trusted-domain filter ensures only authoritative sources are surfaced.

### The System Prompt Is Built Per-Request (Personalisation)

Every chat request dynamically constructs a system prompt that includes:

1. The student's Z-score, district, stream, and A/L subjects
2. The **full verified eligible course list** — as a markdown table with course code, university, cutoff, and safety margin

This means the model always knows what the student can actually get into. When the student asks "I like robotics — what should I choose?", the model scans the eligible table first and never recommends a course that's out of reach. The instruction in the system prompt is explicit: *"Never recommend a course not in this table."*

### Transparent Scoring Engine

The recommendation scorer is a pure Python function — no database, no LLM. It takes a student profile and a list of eligible courses and returns a weighted score (0–100) per course broken down by five named dimensions:

- **Z-score margin** (`z_margin`) — safety above the cutoff, normalised via `tanh` so large margins don't dominate
- **University preference** (`university`) — bonus if the course is at one of the student's stated preferred universities
- **Interest alignment** (`interest`) — reserved; activates when interest tags are passed
- **Career alignment** (`career`) — reserved
- **Industry outlook** (`industry`) — reserved

Weights are configurable via a `scoring_config` database table — changeable by admin without redeployment. When a dimension has no data (student stated no preferences), its weight is redistributed proportionally across active dimensions, keeping scores honest.

**Why deterministic scoring?** Because if a student asks "why is Engineering ranked above IT for me?", the system must show a clear, auditable breakdown. An LLM-assigned score cannot explain itself reliably.

### BFF (Backend For Frontend) Proxy Pattern

The Next.js app has two sets of API route handlers:
- `/api/bff/[...path]` — requires a valid NextAuth session; attaches the JWT; forwards to FastAPI. Used for all admin endpoints.
- `/api/public/[...path]` — open; no auth. Used for the student eligibility flow and chat.

This means FastAPI is never exposed directly to the internet, CORS is not needed on the Python side, and auth enforcement happens at the Next.js middleware layer before the request reaches FastAPI.

### PDF Table Extraction Pipeline

The raw UGC handbooks (four PDFs, 2021–2025) are processed by `scripts/native_pdf_extractor/extract_cutoffs.py` using `pdfplumber`. Section 9 of each handbook spans 10 PDF pages and contains a table of 261 course codes × 25 districts. The extractor:

1. Locates Section 9 programmatically by scanning for the section header
2. Extracts each table row using pdfplumber's built-in table detection
3. Normalises district names, handles "NQC" (No Qualified Candidates) cells, converts Z-scores to 4-decimal floats
4. Writes a structured CSV to `data/cutoffs_extracted/`

The Arq worker job then loads the CSV into `z_score_cutoffs` with deduplication and validation.

---

## Project Structure

```
degree-guidance/
├── apps/
│   ├── api/                        # FastAPI application
│   │   ├── main.py                 # App factory, router registration
│   │   ├── dependencies.py         # DB session, auth dependencies
│   │   ├── admin_audit.py          # Admin action logger
│   │   └── routers/
│   │       ├── eligibility.py      # POST /eligibility
│   │       ├── recommendations.py  # POST /recommendations
│   │       ├── chat.py             # POST /v1/chat
│   │       ├── auth.py             # POST /auth/login, /auth/me
│   │       ├── reference.py        # GET /reference/* (districts, streams)
│   │       ├── admin_courses.py
│   │       ├── admin_aliases.py
│   │       ├── admin_ingestions.py
│   │       └── admin_requirements.py
│   └── worker/
│       └── jobs/
│           ├── ingest_zscores.py       # Load cutoff CSV into DB
│           ├── extract_pdf.py          # OCR on uploaded handbook PDF
│           └── index_factsheets.py     # Embed factsheets into pgvector
│
├── core/                           # Shared domain logic (no HTTP, no UI)
│   ├── eligibility/
│   │   ├── engine.py               # Deterministic SQL eligibility checker
│   │   ├── subject_requirements.py
│   │   └── arts_basket.py          # Arts-stream merit rules
│   ├── scoring/
│   │   ├── engine.py               # Pure-Python weighted scorer
│   │   ├── service.py              # Orchestrates scorer + LLM explanations
│   │   └── config.py               # Weight configuration loader
│   ├── rag/
│   │   └── retrieval.py            # Hybrid pgvector + FTS + RRF
│   ├── chat/
│   │   ├── orchestrator.py         # Gemini agentic loop (5 tools, 6 turns)
│   │   └── tools.py                # Tool implementations (find_course, etc.)
│   ├── models/                     # SQLAlchemy ORM models
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── config.py                   # pydantic-settings config
│   ├── db.py                       # Async engine + session factory
│   └── security.py                 # JWT creation/verification
│
├── web/                            # Next.js 14 frontend
│   └── src/
│       ├── app/
│       │   ├── (student)/          # Public student flow
│       │   ├── admin/              # Admin panel (auth-gated)
│       │   └── api/
│       │       ├── bff/            # Authenticated BFF proxy → FastAPI
│       │       ├── public/         # Open proxy (student endpoints)
│       │       └── auth/           # NextAuth route handler
│       └── components/
│           ├── student/
│           │   ├── guidance-flow.tsx   # Multi-step eligibility form
│           │   ├── results-view.tsx    # Ranked course cards
│           │   └── chat-panel.tsx      # Floating AI advisor
│           └── admin/
│               └── sidebar.tsx
│
├── alembic/                        # Database migration history (32 migrations)
│   └── versions/
│
├── content/
│   └── factsheets/                 # 50 curated degree factsheets (Markdown)
│       ├── 001.md                  # Medicine
│       ├── 008.md                  # Engineering
│       ├── 012.md                  # Computer Science
│       └── ...                     # 47 more
│
├── data/
│   ├── raw_handbooks/              # UGC PDFs (2021, 2023, 2024, 2025)
│   ├── cutoffs_extracted/          # CSV output from PDF extractor
│   └── seeds/                      # Static seed data (courses, streams, etc.)
│
├── scripts/
│   └── native_pdf_extractor/       # PDF → CSV pipeline
│
├── tests/
│   ├── unit/                       # Pure-Python unit tests
│   └── integration/                # Tests against a real test database
│
├── ops/
│   └── docker-compose.yml          # Redis only (Postgres runs natively)
│
├── docs/
│   ├── MASTERPLAN_v4.md            # Full architectural specification
│   └── DATABASE_REFERENCE.md       # Schema reference
│
└── pyproject.toml                  # Python dependencies (uv-managed)
```

---

## Data Pipeline

### Cutoff ingestion (run once per new handbook)

```
UGC Handbook PDF (data/raw_handbooks/)
        │
        ▼
  pdfplumber extractor
  (scripts/native_pdf_extractor/extract_cutoffs.py)
        │  Locates Section 9, extracts 261 × 25 table,
        │  normalises districts, handles NQC cells
        ▼
  CSV  (data/cutoffs_extracted/zscores_YYYY.csv)
        │
        ▼
  Arq worker: ingest_zscores
  (validates, deduplicates, bulk-inserts)
        │
        ▼
  PostgreSQL: z_score_cutoffs table
        │
        └─── Eligibility engine reads at query time
```

### Factsheet indexing (run once; re-run when factsheets change)

```
Markdown factsheets (content/factsheets/*.md)
        │
        ▼
  Arq worker: index_factsheets
    1. Chunk each factsheet (~300 tokens, 50-token overlap)
    2. Embed each chunk with Gemini text-embedding-004 (768 dims)
    3. Store in rag_sources + rag_chunks + rag_embeddings tables
        │
        ▼
  PostgreSQL + pgvector (HNSW index on embedding column)
        │
        └─── Hybrid RAG retrieval at chat query time
```

---

## The AI Advisor (Chatbot)

The chatbot is built on a **manual Gemini function-calling loop** in `core/chat/orchestrator.py`. On each student message:

1. A **dynamic system prompt** is built. It includes the student's Z-score, district, stream, A/L subjects, interests, and the full verified eligible course list as a markdown table with safety margins. The model always knows what the student can actually get into.

2. The model is called with all 5 tool declarations. It may call a tool, receive the result, and call another — up to 6 turns per message.

3. The final text response is returned alongside a list of tools used, which appear as badges under the assistant message in the UI.

### How hallucination is prevented

| Risk | Prevention |
|---|---|
| Stating a wrong cutoff | System prompt forbids guessing Z-scores. Model must call `lookup_course` or `get_cutoff_trend` first. |
| Not finding a course by nickname | `find_course` is called before any course question. 20+ abbreviation expansions. 3-strategy DB fallback. Model is told: "The DB has all 261 courses — never say you can't find it without trying find_course first." |
| Recommending an unreachable course | Eligible course list is in every system prompt. Model instructed: "Never recommend a course not in this table." |
| Trusting unreliable web sources | `search_web` scores results by domain trust. Only authoritative .ac.lk, .gov.lk, and established global sources are surfaced as `[Trusted source]`. |

---

## The Eligibility Engine

`core/eligibility/engine.py` — the most critical component. Key properties:

- **Deterministic** — same input always produces the same output
- **SQL-only** — a single parameterized query joins 4 tables; no LLM
- **Three states**: `eligible`, `conditional`, `not_eligible`
- **Confidence tier**: `current` / `previous_year` / `estimated` (based on data age)
- **Marginal flag**: `student_margin ≤ 0.05` triggers a warning
- **Audit log**: every query writes to `eligibility_audit` with a hash of inputs
- **Special provisions**: aptitude-test courses return `conditional`, not `eligible`
- **Arts-basket logic**: Arts stream uses 100% all-island merit (no district quota)
- **Negative Z-scores**: supported; range validated to `[-2.0, +3.0]`
- **NQC cells**: stored as `NULL`; eligibility query skips them cleanly

---

## The Scoring Engine

`core/scoring/engine.py` — pure Python, no I/O. Key properties:

- **Five dimensions**: z\_margin, university, interest, career, industry
- **`tanh` normalisation on z\_margin** — maps `[0, ∞)` to `[0, 1)` smoothly so large margins don't crowd out other signals
- **Weight renormalization** — dimensions with no data (no preferences stated) redistribute their weight across active dimensions; "no preferences → normal safety recommendation" stays honest
- **Three buckets**: Safe (margin ≥ 0.10), Ambitious (margin 0–0.10), Consider (conditional)
- **Configurable weights** — stored in `scoring_config` table; admin can change without redeployment
- **LLM never touches scores** — Gemini only writes a 2-sentence explanation after the rank is finalized

---

## Admin Panel

The admin panel at `/admin` (JWT-gated) provides:

| Section | Path | What it does |
|---|---|---|
| Dashboard | `/admin` | System health, quick stats |
| Courses | `/admin/courses` | Browse all 261 courses |
| Aliases | `/admin/aliases` | Map common names and abbreviations to course codes |
| Requirements | `/admin/requirements` | Per-course subject prerequisites |
| Ingestions | `/admin/ingestions` | View PDF ingestion runs and re-trigger them |

Admin auth: `python scripts/create_admin.py` to create the first user. All admin writes log to `admin_actions`.

---

## Database Schema

The schema has **32 Alembic migrations** (01 → 32, fully sequential). Major tables:

| Table | Purpose |
|---|---|
| `districts` | 25 Sri Lankan districts with `is_disadvantaged` flag |
| `streams` | 6 A/L streams |
| `universities` | 21 state universities and HEIs |
| `courses` | 261 degree programmes with `course_number` + `university_code` |
| `course_aliases` | Alternative names and abbreviations for courses |
| `course_stream_eligibility` | Which streams are eligible for each course |
| `course_requirements` | Per-course subject prerequisites |
| `z_score_cutoffs` | Cutoff Z-scores: course × district × year (~6,500 rows/year) |
| `eligibility_audit` | Every eligibility query logged with input hash |
| `rag_sources` | Factsheet metadata (title, course number, file path) |
| `rag_chunks` | Chunked text from each factsheet (311 chunks total) |
| `rag_embeddings` | 768-dim vectors from Gemini text-embedding-004 (pgvector) |
| `conversations` | Chat session containers (UUID PK, session\_id) |
| `messages` | Chat turns (role CHECK, content TEXT, tool\_calls JSONB) |
| `users` | Admin users (email, bcrypt hash, role) |
| `admin_actions` | Audit trail for all admin writes |
| `scoring_config` | Configurable weights for the scoring engine |
| `ingestion_runs` | PDF ingestion job history (status, errors, row counts) |

**Year convention (critical):** The `year` column on `z_score_cutoffs` is the **A/L exam year**, not the handbook academic year. The 2024/2025 handbook publishes cutoffs from the 2023 A/L exam — stored as `year = 2023`. This matches how students think: "I took my A/Ls in 2023."

---

## Why Ubuntu / WSL2

The entire backend (Python, PostgreSQL, Redis, Arq) runs inside **Ubuntu 22.04 on WSL2** on a Windows 11 machine. Here's why:

### 1. pgvector requires native Linux compilation
pgvector is a PostgreSQL extension that must be compiled against the Postgres installation. On Ubuntu it's `apt install postgresql-16-pgvector` and done. On Windows, compiling Postgres extensions requires MSVC, manual `pg_config` PATH setup, and multiple hours of troubleshooting. It is not the right path for a time-boxed project.

### 2. asyncpg and Python native packages are Linux-first
`asyncpg` (the fastest async Postgres driver for Python) and `psycopg2-binary` have pre-compiled Linux wheels that install in seconds via `uv`. On Windows, `asyncpg` has historically required MSVC build tools and has been a common source of install failures.

### 3. The toolchain is Linux-native
`uv` resolves and installs Python packages significantly faster on Linux due to lower filesystem overhead. `nvm` (Node Version Manager) runs natively on Linux — the Windows equivalent (`nvm-windows`) is a separate project with different behavior. Shell scripts, `Makefile` targets, and cron-style job scheduling all work as expected on Linux.

### 4. Production will be Linux
The deployment target is a Linux VPS (Ubuntu or Debian). Developing on the same OS eliminates "works on my machine" issues. Docker images, Alembic commands, and shell scripts all behave identically in dev and production.

### 5. WSL2 gives the best of both worlds
WSL2 runs a real Linux kernel in a Hyper-V lightweight VM. The developer gets Windows for the browser, VS Code, and Windows Terminal — while all server processes run natively on Linux. The Next.js frontend and FastAPI backend are accessed from Windows Chrome via the WSL2 IP address (or Windows port forwarding via `netsh interface portproxy`).

---

## Environment Setup

### Prerequisites

- Windows 11 with WSL2 + Ubuntu 22.04
- Docker Desktop for Windows (for Redis)
- Node.js via nvm (inside WSL2)
- Python 3.13 via `uv` (inside WSL2)
- PostgreSQL 16 with pgvector (inside WSL2)
- A Google Cloud project with Gemini API enabled (free tier is sufficient)

### One-time WSL2 setup

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install nvm and Node.js 20
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Install PostgreSQL 16 with pgvector
sudo apt update
sudo apt install -y postgresql-16 postgresql-16-pgvector
sudo service postgresql start

# Create the database
sudo -u postgres psql -c "CREATE DATABASE degree_guidance;"
sudo -u postgres psql -c "CREATE USER degree_user WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE degree_guidance TO degree_user;"
sudo -u postgres psql -d degree_guidance -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## Running Locally

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd degree-guidance

# 2. Start Redis
docker compose -f ops/docker-compose.yml up -d redis

# 3. Install Python dependencies
uv sync

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, GEMINI_API_KEY, SECRET_KEY

# 5. Run database migrations
uv run alembic upgrade head

# 6. Create an admin user
uv run python scripts/create_admin.py

# 7. Start the FastAPI backend
uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8077 --reload

# 8. In a separate terminal — start the frontend
cd web
npm install
npm run dev       # development server (port 3000, hot reload)
# or for production:
npm run build && npm run start
```

Access the app at `http://localhost:3000` from your browser.

> **WSL2 note:** If `localhost:3000` is refused in Windows Chrome, use the WSL2 IP directly: `http://<wsl-ip>:3000`. Find the IP with `hostname -I` inside WSL. To set up permanent port forwarding, run this in an **Administrator** PowerShell:
> ```powershell
> netsh interface portproxy add v4tov4 listenport=3000 listenaddress=127.0.0.1 connectport=3000 connectaddress=<wsl-ip>
> netsh interface portproxy add v4tov4 listenport=8077 listenaddress=127.0.0.1 connectport=8077 connectaddress=<wsl-ip>
> ```

---

## Running Tests

```bash
# All tests
uv run pytest

# Unit tests only (no database required)
uv run pytest tests/unit/

# Integration tests only (requires running Postgres)
uv run pytest tests/integration/

# Verbose output
uv run pytest -v

# Single file
uv run pytest tests/integration/test_eligibility_engine.py -v
```

Integration tests use the development database (from `DATABASE_URL`). Each test wraps its writes in a transaction that is rolled back on teardown — no permanent test data.

---

## Alembic Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Show migration history
uv run alembic history --verbose

# Roll back one step
uv run alembic downgrade -1

# Auto-generate a new migration from model changes
uv run alembic revision --autogenerate -m "short description"
```

Migrations are numbered 01–32, with each filename describing what it adds. The naming convention: `{revision_prefix}_{sequence}_{description}.py`.

---

## Environment Variables

Copy `.env.example` to `.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://degree_user:password@localhost:5432/degree_guidance

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-32-byte-hex-secret

# Google Gemini (free tier — https://aistudio.google.com/apikey)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_CHAT_MODEL=models/gemini-3.1-flash-lite
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
GEMINI_EMBEDDING_DIM=768

# Redis
REDIS_URL=redis://localhost:6379

# JWT expiry for admin sessions (minutes)
ADMIN_TOKEN_EXPIRE_MINUTES=480
```

Copy `web/.env.example` to `web/.env.local`:

```env
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
API_BASE_URL=http://localhost:8077
```

---

## Development Roadmap

| Week | Milestone | Status |
|---|---|---|
| 1–2 | Database schema (32 migrations), PDF extractor, seed data for all 261 courses | ✅ Complete |
| 3 | Eligibility engine, scoring engine, recommendations API, admin panel foundation | ✅ Complete |
| 4 | RAG pipeline — 50 factsheets, pgvector, hybrid RRF retrieval, factsheet indexing | ✅ Complete |
| 5 | Agentic chatbot — 5 tools, Gemini free tier, conversation persistence, personalisation | ✅ Complete |
| 6 | Eval harness (100-case eligibility regression suite), OpenTelemetry traces, Sentry, deployment runbook | 🔄 Upcoming |
| 7 | Closed beta with 20–30 real A/L students | 🔄 Upcoming |
| 8 | Demo day + supervisor handover | 🔄 Upcoming |

---

## Acknowledgements

- **UGC Sri Lanka** — for publishing the Z-score handbooks that form the factual backbone of this platform
- **Google Gemini** — free-tier generative AI and embedding API
- **DuckDuckGo** (`ddgs`) — free, key-free web search usable from a background thread
- **pgvector** — making vector similarity search a native PostgreSQL feature

---

*This platform is a decision aid, not a guarantee. Z-score cutoffs change every year based on the number of applicants and available seats. Always verify with the official UGC handbook before making university application decisions.*
