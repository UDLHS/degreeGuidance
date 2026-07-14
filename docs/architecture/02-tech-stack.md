# Technology Stack & Why Each Choice

## What this is / why it exists

This is the complete inventory of every technology the platform runs on, each
with a one-line *what it is* and a genuine *why it was chosen* — plus the
deliberate **non-choices** (the popular tools this project intentionally does
*not* use). Versions are the real constraints from `pyproject.toml` (backend)
and `web/package.json` (frontend).

The guiding bias throughout: **fewest moving parts that still do the job
correctly.** One database, two processes, no framework it does not need.

---

## Backend (Python)

Source of truth: `pyproject.toml`. Python `>=3.11` (runs on 3.13 in prod),
package/venv managed by **uv**.

| Technology | Version | What it is | Why it was chosen |
| --- | --- | --- | --- |
| **FastAPI** | ≥0.115 | Async web framework | Async-native (matches asyncpg), automatic OpenAPI docs, first-class Pydantic integration. |
| **Uvicorn** | ≥0.32 (`[standard]`) | ASGI server that runs FastAPI | Production-grade, supports graceful shutdown (needed so the worker's SIGTERM handling is clean). |
| **SQLAlchemy** | ≥2.0.30 (`[asyncio]`) | ORM / SQL toolkit | 2.0's typed, fully-async API; lets `core/` talk about rows as Python objects while still dropping to raw `text()` SQL on hot paths (the eligibility query, admin routers). |
| **asyncpg** | ≥0.29 | Async PostgreSQL driver | The fastest async Postgres driver for Python; the whole app is `async` so one process serves many concurrent requests. |
| **psycopg2-binary** | ≥2.9.9 | Sync Postgres driver | Only for Alembic's migration runner (`database_url_sync`), which is synchronous. |
| **Alembic** | ≥1.13 | Schema migration tool | The standard for SQLAlchemy; 43 additive migrations form the schema history. |
| **Pydantic** | ≥2.7 | Data validation / serialisation | Validates every request/response body; v2 is fast (Rust core) and integrates with FastAPI. |
| **pydantic-settings** | ≥2.3 | Typed config from env | `core/config.py` — one `Settings` class, all env vars typed and validated at boot; a missing required var fails fast and loud. |
| **pgvector** | ≥0.3 | Vector similarity in Postgres | The reason there is **no separate vector database**: embeddings live in a `vector(768)` column and cosine search is the `<=>` operator. See `07-rag-knowledge.md`. |
| **arq** | ≥0.28 | Async job queue on Redis | Runs the background worker (PDF extraction, factsheet/article indexing). Asyncio-native and lightweight — no Celery result-backend ceremony. See `12-infrastructure-deployment.md`. |
| **pdfplumber** | ≥0.11.9 | PDF text/table extraction | Accurate access to character positions and rotation, which the handbook's rotated cutoff grids require. See `04-ingestion-pipeline.md`. |
| **pikepdf** | (ad-hoc) | Lossless PDF rewriter | Not a pinned dependency — installed manually for the PDF-normalisation ops step that fixes pathologically slow books (war story 2.3 in `16-design-decisions.md`). |
| **google-genai** | ≥1.0 | Google Gemini SDK | The LLM + embeddings provider. Chat model `gemini-3.1-flash-lite`, embeddings `gemini-embedding-001` at 768 dims. Free/cheap tier; bounded by a daily budget. |
| **ddgs** | ≥9.14.4 | DuckDuckGo search client | The agent's `search_web` tool — free, no API key, callable from an async executor. Results are trust-ranked in code. |
| **PyJWT** | ≥2.13 | JSON Web Tokens | Admin auth: HS256 access tokens, 12-hour expiry. See `13-auth-security.md`. |
| **bcrypt** | ≥5.0 | Password hashing | Admin passwords are bcrypt-hashed, never stored or logged in plaintext. |
| **python-multipart** | ≥0.0.12 | Multipart form parsing | Needed by FastAPI to accept file uploads (handbook PDFs, reviewed CSVs). |
| **python-dotenv** | ≥1.0 | `.env` loading | Loads local env in dev; the worker jobs call `load_dotenv()` at import. |

### Backend dev tooling (`[dependency-groups].dev`)

| Tool | Version | Role |
| --- | --- | --- |
| **ruff** | ≥0.5 | Linter + formatter (replaces flake8 + isort + black) |
| **mypy** | ≥1.10 | Static type checker |
| **pytest** + **pytest-asyncio** | ≥8.2 / ≥0.23 | Test runner; `asyncio_mode = "auto"` so `async def` tests just work |
| **pyyaml** | ≥6.0.3 | Loads the YAML eligibility test-case fixtures |
| **httpx** | ≥0.28.1 | Async HTTP client used by the FastAPI test client |

---

## Frontend (TypeScript / Next.js)

Source of truth: `web/package.json`.

| Technology | Version | What it is | Why it was chosen |
| --- | --- | --- | --- |
| **Next.js** | 14.2.35 | React framework (App Router) | Server components + built-in route handlers, which host the **BFF** proxy layer (`/api/bff`, `/api/public`) that fronts FastAPI. See `11-student-frontend.md`. |
| **React** | 18 | UI library | Component model for the student flow and admin panel. |
| **TypeScript** | 5 | Typed JavaScript | End-to-end type safety; `web/src/lib/guidance-types.ts` mirrors the backend Pydantic schemas exactly. |
| **next-auth (Auth.js)** | 5.0-beta | Auth / session management | Google sign-in for students, credentials for admins; crucially, it stores the FastAPI token **server-side** so it never reaches the browser. See `13-auth-security.md`. |
| **Tailwind CSS** | 3.4 | Utility-first CSS | Fast to build, consistent, no separate stylesheet sprawl. |
| **Radix UI** | 1.x | Unstyled accessible primitives | `@radix-ui/react-dialog`, `-select`, `-label`, `-slot` — accessibility (keyboard, ARIA) for free, no design lock-in. |
| **shadcn/ui pattern** | (v3 CLI) | Component recipes over Radix | Copy-in components (Button, Dialog, Select, Table) rather than a heavyweight library. |
| **class-variance-authority** + **clsx** + **tailwind-merge** | — | Class composition | Variant-driven component styling without conflicts. |
| **lucide-react** | 1.18 | Icon set | Tree-shakeable, consistent icons. |
| **sonner** | 2.0 | Toast notifications | Lightweight, accessible. |
| **next-themes** | 0.4 | Light/dark theming | Theme switching for the UI. |
| **tailwindcss-animate** | 1.0 | Animation utilities | Small transitions in dialogs/menus. |

Frontend dev tooling: **eslint** + **eslint-config-next** (linting),
**postcss** (Tailwind pipeline), **@types/** packages (type defs).

---

## Data & AI layer

| Component | What it is | Why |
| --- | --- | --- |
| **PostgreSQL** | Relational database | Single source of truth for *everything*: cutoffs, courses, RAG chunks + embeddings, chat history, audit log, ingestion artifacts. ACID, JSON(B), and the pgvector extension in one place. |
| **pgvector** | Postgres extension | Vector column + cosine (`<=>`) search — no second datastore for embeddings. |
| **Redis** | In-memory store | The arq job broker (API enqueues, worker consumes). TLS (`rediss://`) in prod. |
| **Gemini `gemini-3.1-flash-lite`** | Chat LLM | Runs the agent's tool-calling loop cheaply. |
| **Gemini `gemini-embedding-001`** | Embedding model | 768-dim (Matryoshka) vectors for factsheets, articles, and queries. |

---

## Infrastructure (production)

Full topology in `12-infrastructure-deployment.md`. In brief:

| Layer | Provider | Note |
| --- | --- | --- |
| Frontend hosting | **Vercel** | Next.js app + BFF route handlers. |
| API service | **Render (Web Service)** | FastAPI under uvicorn. |
| Worker service | **Render (Background Worker)** | `arq apps.worker.settings.WorkerSettings`. Separate machine from the API. |
| Database | **Supabase** (managed Postgres + pgvector) | Reached via the **Session Pooler** (IPv4) — the direct host is IPv6-only. |
| Job broker | **Upstash** (managed Redis) | `rediss://` TLS. |
| AI | **Google Gemini API** | Chat + embeddings. |

### Local dev environment

- **Ubuntu on WSL2** — pgvector and asyncpg are Linux-first; native compilation
  is trivial on Ubuntu and painful on Windows.
- **Node via nvm** (source it in non-login shells), **Python via uv**.
- **Redis native in WSL** at `localhost:6379` (no Docker needed).

---

## The deliberate non-choices (and why)

This is the most instructive part of the stack. Each avoided tool was a real
option that was consciously rejected — see `16-design-decisions.md` Part 3 for
the longer form.

- **No LangChain / LlamaIndex.** The agent loop (`core/chat/orchestrator.py`)
  and the RAG retrieval (`core/rag/retrieval.py`) are hand-written — together a
  few hundred readable lines with zero hidden prompts or version churn. For a
  5-tool agent and a small corpus, a framework adds abstraction, not value.
- **No Pinecone / Weaviate.** `pgvector` keeps embeddings in the same Postgres
  as everything else: one backup, one connection pool, one failure mode. The
  corpus (hundreds of chunks) fits trivially.
- **No Celery.** `arq` is asyncio-native and matches the async codebase; no
  separate result backend or worker-pool complexity.
- **No OpenAI / Anthropic in production.** Gemini's free/cheap tier keeps the
  cost per student at ~zero, bounded further by a daily budget guard that
  degrades politely (a 429, never a bill shock). *(A future upgrade to a
  stronger model is planned — it needs a small provider abstraction in the
  agent loop, since the loop is currently Gemini-specific.)*
- **No Google Custom Search API.** `ddgs` is free and key-free; the trust
  ranking that matters is applied in our own code, not bought from the API.
- **No microservices.** A modular monolith (`core/` shared by two processes)
  is simpler to reason about, deploy, and hand over for a single-author
  project with a cohesive domain.

---

## Related docs

- `01-system-overview.md` — how these pieces are wired together.
- `07-rag-knowledge.md` — pgvector + FTS + RRF in depth.
- `08-ai-agent.md` — the framework-free agent loop.
- `12-infrastructure-deployment.md` — the production topology.
- `16-design-decisions.md` — the full reasoning behind the non-choices.
