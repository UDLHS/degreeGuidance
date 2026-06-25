# Degree Guidance — Complete Project Internals Guide

> This document is a deep technical reference of every folder, file, technology choice, and core concept in this project. It is written to give a developer a complete, ground-up understanding of how the entire system works — not just what it does, but **why** it was built the way it was.

---

## Table of Contents

1. [Three Core Principles Behind Every Decision](#1-three-core-principles-behind-every-decision)
2. [How the System Flows (Bird's Eye View)](#2-how-the-system-flows-birds-eye-view)
3. [Technology Map](#3-technology-map)
4. [Root-Level Files](#4-root-level-files)
5. [/core — Shared Business Logic](#5-core--shared-business-logic)
   - [core/config.py](#coreconfigpy)
   - [core/db.py](#coredbpy)
   - [core/security.py](#coresecuritypy)
   - [core/models/](#coremodels)
   - [core/schemas/](#coreschemas)
   - [core/eligibility/](#coreeligibility)
   - [core/scoring/](#corescoring)
   - [core/rag/](#corerag)
   - [core/chat/](#corechat)
6. [/apps/api — FastAPI HTTP Layer](#6-appsapi--fastapi-http-layer)
   - [apps/api/main.py](#appsapimainpy)
   - [apps/api/dependencies.py](#appsapidependenciespy)
   - [apps/api/routers/](#appsapirouters)
   - [apps/api/admin_audit.py](#appsapiadmin_auditpy)
7. [/apps/worker — Background Jobs](#7-appsworker--background-jobs)
8. [/web — Next.js Frontend](#8-web--nextjs-frontend)
   - [App Router Structure](#app-router-structure)
   - [API Routes (BFF Proxy)](#api-routes-bff-proxy)
   - [Auth (NextAuth v5)](#auth-nextauth-v5)
   - [Student Components](#student-components)
   - [Admin Components](#admin-components)
9. [/alembic — Database Migrations](#9-alembic--database-migrations)
10. [/content/factsheets — The Knowledge Base](#10-contentfactsheets--the-knowledge-base)
11. [/data — Raw Data and Seeds](#11-data--raw-data-and-seeds)
12. [/scripts — Utility Scripts](#12-scripts--utility-scripts)
13. [/tests — Test Suite](#13-tests--test-suite)
14. [/ops — Infrastructure](#14-ops--infrastructure)
15. [Complete Request Flow — End to End](#15-complete-request-flow--end-to-end)
16. [Concept Dictionary](#16-concept-dictionary)

---

## 1. Three Core Principles Behind Every Decision

Before reading any file, understand these three principles. Every architecture decision in this project comes back to one of them.

### Principle 1: Separate concerns by trust level

Some data is sacred — Z-score cutoffs from UGC. If the system gives a wrong eligibility answer, a student might apply for a course they cannot get into. This is a real-world consequence.

**Sacred data → deterministic SQL only. No LLM, ever.**

Some data is helpful but soft — career advice, salary ranges, industry trends. If this is slightly off, no harm is done.

**Soft data → LLM with citations and source badges.**

This is why the eligibility engine and the chatbot are completely separate pieces of code with no shared logic.

### Principle 2: One direction, clean handoffs

Data flows in one direction:

```
Student inputs → Eligibility SQL → Scoring engine → Ranked list → Chat advisor
```

Each stage receives a typed Pydantic object, does its work, and returns another typed Pydantic object. Nothing skips stages. The chatbot receives the ranked list as context — it does not re-run eligibility.

### Principle 3: The LLM is a writer, not a decision-maker

The LLM never computes a score. It never determines eligibility. It never invents a Z-score. Every number it quotes must come from a tool result. It reads structured data, then writes natural language on top.

---

## 2. How the System Flows (Bird's Eye View)

```
Student fills form in browser
         │
         │ POST /api/public/recommendations
         ▼
Next.js BFF proxy (no auth, open)
         │
         │ forwards to FastAPI :8077
         ▼
FastAPI → recommendations router
         │
         ├─→ evaluate_eligibility()   ← core SQL query against z_score_cutoffs
         │         └─→ results: list of courses where student qualifies
         │
         ├─→ load_active_config()     ← reads scoring_config table
         │
         ├─→ score_courses()          ← pure Python weighted scoring
         │         └─→ ranked, bucketed list
         │
         └─→ RecommendationResponse  ← typed Pydantic, serialized to JSON
         │
         ▼
Browser receives ranked courses
Student clicks chat bubble
         │
         │ POST /api/public/chat  {message, context{eligible_courses, z_score, ...}}
         ▼
Next.js BFF proxy
         │
         ▼
FastAPI → chat router
         │
         ├─→ load/create conversation in DB
         ├─→ load message history
         │
         └─→ run_chat()   ← Gemini agentic loop
                  │
                  ├─ Turn 1: Gemini calls find_course("ECS")
                  │          → tools.py → SQL → "119D, Kelaniya"
                  ├─ Turn 2: Gemini calls lookup_course("119")
                  │          → tools.py → SQL → cutoff 1.5140
                  └─ Turn 3: Gemini writes final answer
                  │
                  ▼
         persist messages in DB
         return {reply, tools_used, conversation_id}
         │
         ▼
Browser renders answer + tool badges
```

---

## 3. Technology Map

| Layer | Technology | Purpose |
|---|---|---|
| HTTP API | FastAPI | Route handling, request parsing, response serialization |
| ASGI server | Uvicorn | Runs the FastAPI app, handles concurrent connections |
| Database | PostgreSQL 16 | All structured data, full-text search, vector storage |
| Vector search | pgvector extension | Cosine similarity search over 768-dim embeddings |
| ORM | SQLAlchemy 2.0 (async) | Maps Python classes to DB tables, builds queries |
| Async DB driver | asyncpg | Fastest async Postgres driver, no thread blocking |
| Migrations | Alembic | Versioned, reversible schema changes |
| Background jobs | Arq | Redis-backed async job queue |
| Job broker | Redis 7 | Queue storage for Arq, session caching |
| AI model | Gemini (google-genai) | Text generation, function calling, embeddings |
| Web search | ddgs (DuckDuckGo) | Free, key-free live internet search |
| PDF extraction | pdfplumber | Table extraction from UGC handbook PDFs |
| Auth (backend) | PyJWT + bcrypt | JWT minting and password hashing |
| Auth (frontend) | NextAuth v5 | Session management, credential provider |
| Frontend framework | Next.js 14 | App Router, React Server Components, API routes |
| Language (frontend) | TypeScript 5 | Type-safe frontend code |
| Styling | Tailwind CSS 3.4 | Utility-first CSS |
| UI components | shadcn/ui + Radix | Accessible, unstyled primitives |
| Config | pydantic-settings | Type-safe `.env` parsing |
| Package manager (Python) | uv | Fast dependency resolution and install |
| Linter | ruff | Replaces flake8, isort, black |
| Testing | pytest + pytest-asyncio | Async-compatible test runner |

---

## 4. Root-Level Files

### `pyproject.toml`

The Python project manifest. Think of it as the Python equivalent of `package.json`.

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "google-genai>=1.0.0",
    "ddgs>=9.14.4",
    ...
]

[dependency-groups]
dev = ["pytest>=8.2.0", "ruff>=0.5.0", ...]
```

Managed by **uv** — a Rust-based package manager that is 10–100× faster than pip. `uv sync` reads this file and installs everything. `uv.lock` is the lockfile that pins the exact version of every dependency so the environment is identical on every machine.

**Why uv over pip?** pip resolves and installs packages sequentially. uv parallelises both operations using Rust-native code. For a project with 15+ dependencies, the install goes from ~30 seconds (pip) to ~2 seconds (uv).

**`[tool.pytest.ini_options]`** — `asyncio_mode = "auto"` makes all test functions async-capable automatically without needing `@pytest.mark.asyncio` decorators on every test.

---

### `alembic.ini`

Alembic configuration. Points it to `alembic/env.py` (where migrations run) and to the sync database URL. Alembic needs a synchronous connection (psycopg2) for migrations because its internal tooling predates asyncpg — even though the running app uses asyncpg.

---

### `.env` and `.env.example`

`.env` — actual secrets. Never committed to git (listed in `.gitignore`).

`.env.example` — the shape without real values. Committed so any developer knows what variables to create.

`pydantic-settings` reads `.env` automatically at startup and validates every value. If `DATABASE_URL` is missing, the app fails immediately with a descriptive error — not buried in a runtime crash 5 minutes later.

---

### `schema.sql`

A snapshot of the full database DDL. Not used by migrations — that is Alembic's job. Exists as a reference so you can understand the full schema in one file without reading 32 individual migration files.

---

### `uv.lock`

Auto-generated by uv. Contains the exact resolved version of every package and every transitive dependency. Should be committed to git so builds are reproducible. Never edit manually.

---

## 5. `/core` — Shared Business Logic

`core/` is the heart of the application. It contains no HTTP code, no UI code, and no framework-specific code. It is pure Python domain logic.

Both `apps/api/` and `apps/worker/` import from `core/`. This is what makes the architecture a **modular monolith** — one codebase, shared logic, two running processes.

---

### `core/config.py`

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = Field(...)               # required
    jwt_secret_key: str = Field(...)             # required
    gemini_api_key: str = Field(default="")      # optional default
    gemini_chat_model: str = Field(default="models/gemini-3.1-flash-lite")
    gemini_embedding_dim: int = Field(default=768)
    ...

settings = Settings()  # created once at import time
```

**Technology: pydantic-settings**
Pydantic is a data validation library. `pydantic-settings` extends it to automatically read from `.env` files and OS environment variables. Every field is typed — if someone puts a string where an `int` is expected, the app crashes at startup with a clear message.

**The singleton pattern:** `settings = Settings()` creates one instance at module import time. Every other file does `from core.config import settings`. There is never a second `Settings()` call. This is the standard Python configuration pattern — one source of truth.

---

### `core/db.py`

```python
class Base(DeclarativeBase):
    """Every ORM model inherits from this."""

engine = create_async_engine(
    settings.database_url,
    echo=False,          # don't log every SQL statement in production
    pool_pre_ping=True,  # verify connection is alive before using it
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # don't invalidate objects after commit
)
```

**Concept: Connection Pool**
Creating a database connection is expensive — it involves a TCP handshake, authentication, and SSL setup. A connection pool maintains a fixed number of pre-created connections and lends them to requests as needed. `create_async_engine` creates and manages this pool. Each HTTP request borrows a connection, uses it, and returns it.

**Concept: Async Database Access**
Traditional database drivers (psycopg2, sqlite3) block the calling thread while waiting for the database to respond. If your server handles 100 concurrent requests with a synchronous driver, you need 100 threads — expensive.

Async drivers (asyncpg) never block the thread. While waiting for the database, the Python event loop can process other requests. One thread handles hundreds of concurrent connections. This is why every database operation in this codebase uses `await`.

**`pool_pre_ping=True`:** Before using a borrowed connection, send a lightweight `SELECT 1` to verify the connection is still alive. Without this, you'd get cryptic errors if the database restarted while the app was running.

**`expire_on_commit=False`:** After a `session.commit()`, SQLAlchemy by default marks every loaded Python object as "expired" — you'd need to re-query the database to read any attribute. In async code, this would require an `await` in contexts where that's not possible (like serializing a response). This setting disables expiration.

**`Base = DeclarativeBase()`:** SQLAlchemy's ORM requires a common base class. Every model inherits from `Base`. SQLAlchemy uses this to track all tables, build relationships, and check for schema drift.

---

### `core/security.py`

```python
def hash_password(plain: str) -> str:
    pw = plain.encode("utf-8")[:72]  # bcrypt silently truncates at 72 bytes
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))

def create_access_token(subject: str, role: str) -> str:
    payload = {
        "sub": subject,   # user UUID
        "role": role,     # "admin" or "superadmin"
        "type": "access",
        "iat": now,       # issued at
        "exp": expire,    # expiry timestamp
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    # raises jwt.PyJWTError if signature is invalid or token is expired
```

**Concept: bcrypt**
bcrypt is a password hashing algorithm specifically designed to be slow. MD5 or SHA-256 are fast — an attacker with a GPU can try billions of passwords per second. bcrypt has a configurable "cost factor" — by default it takes ~100ms to hash one password. That makes brute-force attacks 10,000× harder. `gensalt()` generates a random 16-byte salt — even if two admins have the same password, their stored hashes are completely different.

Never store plain text passwords. Never use MD5 or SHA for passwords. Always use bcrypt (or argon2, scrypt).

**Concept: JWT (JSON Web Token)**
Instead of storing session state in a database (which requires a DB lookup on every request), JWTs encode the session as a signed JSON object that the client stores.

Structure: `base64(header).base64(payload).signature`

Payload example:
```json
{"sub": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "role": "admin", "exp": 1719000000}
```

The server signs this with `jwt_secret_key` using HMAC-SHA256 (HS256). When the admin makes a request, they send this token as `Authorization: Bearer <token>`. FastAPI verifies the signature — if valid, the claims are trusted without any database lookup.

**Why HS256 and not RS256?** HS256 uses a single shared secret to both sign and verify. RS256 uses a private key to sign and a public key to verify — useful when different services need to verify tokens without sharing the secret. We have one service, so HS256 is simpler and faster.

---

### `core/models/`

ORM (Object-Relational Mapping) models. Each file defines Python classes that map to database tables. SQLAlchemy translates between Python objects and SQL rows.

**What ORM means in practice:**
- Without ORM: `cursor.execute("INSERT INTO users (email, role) VALUES (%s, %s)", (email, role))`
- With ORM: `session.add(User(email=email, role=role))` — then `await session.commit()`

ORM gives you type checking, Python object semantics, and query composition. But for performance-critical queries (the eligibility SQL), we bypass the ORM and write raw SQL using `text()`.

---

#### `core/models/course.py`
Maps to the `courses` table. A `Course` object has `.course_code` (e.g. "008B"), `.course_number` (e.g. "008"), `.name_en` (e.g. "Engineering"), `.university_id`, `.is_active`, `.requires_aptitude_test`, `.selection_basis`.

---

#### `core/models/cutoffs.py`
Maps to `z_score_cutoffs`. A `ZScoreCutoff` has `.z_score` (e.g. 1.7364), `.district_id`, `.year` (the A/L exam year, not the academic year), `.course_code`.

**Year convention:** The `year` field stores the A/L exam year. The 2024/2025 academic year handbook publishes cutoffs from students who sat A/Ls in 2023 — stored as `year = 2023`. This matches how students think: "I sat my A/Ls in 2023."

---

#### `core/models/auth.py`

Three models:

**`User`** — Admin users.
```python
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'admin', 'superadmin')"),
        Index("idx_users_role", "role", postgresql_where=text("role != 'student'")),
    )
    user_id: UUID primary key
    email: str (unique)
    password_hash: str (bcrypt)
    role: str  # student | admin | superadmin
    is_active: bool
```

The partial index `WHERE role != 'student'` means queries for admin users hit a tiny index (only admin/superadmin rows) instead of the full users table.

**`AdminAction`** — Append-only audit trail of every admin mutation.
```python
class AdminAction(Base):
    action_type: str       # "course_edit", "alias_create", etc.
    target_table: str      # "courses", "course_aliases"
    target_id: str         # the row's primary key
    before_value: JSONB    # state before the change
    after_value: JSONB     # state after the change
    ip_hash: str           # SHA-256 of the admin's IP
```
Every time an admin edits a course name, adds an alias, or changes a requirement, a row is written here. If something goes wrong, you can reconstruct exactly what happened and when.

**`AuthEvent`** — Every login/logout attempt, success and failure.
```python
class AuthEvent(Base):
    event_type: str  # login_success | login_failure | logout
    email: str       # recorded even on failure (invalid user attempt)
    user_id: UUID    # NULL on failure (user didn't exist)
```
`user_id` is nullable with `ON DELETE SET NULL` — deleting an admin user preserves their login history for audit purposes.

---

#### `core/models/rag.py`

Two models for the RAG knowledge base:

**`DocumentSource`** — One row per factsheet file.
```python
class DocumentSource(Base):
    source_id: int (auto PK)
    course_number: str     # "008" for Engineering
    title: str             # "Engineering"
    file_path: str         # "content/factsheets/008.md"
    content_hash: str      # SHA-256 of file contents
```
The `content_hash` is the idempotency key — if the factsheet hasn't changed, re-running the indexer skips it.

**`Chunk`** — One row per text section within a factsheet.
```python
class Chunk(Base):
    source_id: FK → DocumentSource
    chunk_index: int         # position within the file (0, 1, 2...)
    heading: str             # the H2 heading ("Career Paths", "Curriculum")
    content: str             # the actual text
    embedding: Vector(768)   # the 768-dim Gemini embedding (pgvector type)
```
The `Vector(768)` type is from the `pgvector` Python package. It maps to a `vector(768)` column in PostgreSQL and enables the `<=>` cosine distance operator.

---

#### `core/models/chat.py`

**`Conversation`** — A chat session.
```python
class Conversation(Base):
    conversation_id: UUID (auto-generated by Postgres gen_random_uuid())
    session_id: str(64)  # anonymous browser identifier
    messages: relationship → list[Message]
```

**`Message`** — One turn in a conversation.
```python
class Message(Base):
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')"),
    )
    message_id: BigInt (auto-increment PK)
    conversation_id: UUID (FK → Conversation, ON DELETE CASCADE)
    role: str          # "user" or "assistant"
    content: str       # the message text
    tool_calls: JSONB  # e.g. ["find_course", "lookup_course"]
```

**`CheckConstraint`** on role means the database itself enforces that only valid role values can be inserted — not just the application code. This is defense in depth.

**`CASCADE` delete** — If a conversation is deleted, all its messages are deleted automatically. No orphaned message rows.

**`JSONB` for tool_calls** — JSON binary format in PostgreSQL. More efficient than TEXT for JSON because it's stored in a parsed binary form, enabling JSON operators for queries. We store the list of tools used per assistant message here so the UI can render tool badges.

---

### `core/schemas/`

Pydantic schemas define the shape of HTTP request bodies and response bodies. These are separate from ORM models because the API shape and the database shape are often different.

**`core/schemas/eligibility.py`**

```python
class EligibilityRequest(BaseModel):
    z_score: float = Field(..., ge=-2.0, le=3.0)  # ge=greater_equal, le=less_equal
    district_code: str
    stream_code: str
    subjects: list[SubjectInput] = Field(default_factory=list)
    exam_year: int | None = Field(default=None)

class EligibilityResponse(BaseModel):
    exam_year_used: int
    confidence_tier: str       # current | previous_year | estimated
    confidence_message: str | None
    eligible_count: int
    conditional_count: int
    total_count: int
    results: list[EligibilityResultItem]
```

When FastAPI receives a request, it automatically validates the body against `EligibilityRequest`. If `z_score` is missing, or if it's outside [-2.0, 3.0], FastAPI returns HTTP 422 (Unprocessable Entity) with a detailed error message — zero manual validation code needed.

**`core/schemas/recommendation.py`**

Extends eligibility with scoring fields:
```python
class ScoredRecommendation(EligibilityResultItem):
    total_score: float             # 0..1 weighted score
    bucket: str                    # safe | ambitious | consider
    breakdown: list[DimensionBreakdownItem]  # per-dimension contribution
```

**`core/schemas/auth.py`** — Login request/response shapes.

**`core/schemas/admin.py`** — Admin mutation request shapes.

---

### `core/eligibility/`

The most critical package in the codebase.

---

#### `core/eligibility/engine.py`

The eligibility engine. Pure SQL, no LLM, deterministic.

**The core query:**

```sql
SELECT
  zc.z_score      AS cutoff_z_score,
  c.course_code,
  c.name_en       AS course_name,
  c.requires_aptitude_test,
  c.selection_basis,
  u.name_en       AS university_name,
  ARRAY(
    SELECT m.code FROM course_mediums cm
    JOIN mediums m ON m.medium_id = cm.medium_id
    WHERE cm.course_code = c.course_code
  ) AS available_mediums
FROM z_score_cutoffs zc
JOIN courses      c ON c.course_code  = zc.course_code
JOIN universities u ON u.university_id = c.university_id
WHERE zc.year        = :exam_year
  AND zc.district_id = :district_id
  AND zc.z_score IS NOT NULL
  AND zc.z_score    <= :student_z_score   -- student's score must meet/exceed cutoff
  AND c.is_active   = TRUE
  AND EXISTS (
    SELECT 1 FROM course_stream_eligibility cse
    WHERE cse.course_code = c.course_code
      AND cse.stream_id   = :student_stream_id  -- student's stream is accepted
  )
ORDER BY zc.z_score DESC
```

**Breaking this down:**

- `:exam_year`, `:district_id`, `:student_z_score`, `:student_stream_id` are **bound parameters** — the values are passed separately from the SQL string. This prevents SQL injection.
- `JOIN courses` — we need the course name and flags
- `JOIN universities` — we need the university name
- `WHERE zc.z_score <= :student_z_score` — only courses where the cutoff is at or below the student's score (they qualify)
- `AND EXISTS (SELECT 1 FROM course_stream_eligibility ...)` — the course must accept the student's A/L stream
- `ARRAY(SELECT m.code ...)` — a correlated subquery that builds an array of language codes (S/T/E) for each course's available teaching mediums
- `ORDER BY zc.z_score DESC` — most competitive courses first

This is **one query**. Not a loop. Not multiple queries. The database executes this once and returns all eligible courses in one result set.

**Three-state classification:**
```python
conditional = bool(r["requires_aptitude_test"])
status = "conditional" if conditional else "eligible"
```
- `eligible` — student qualifies, no aptitude test
- `conditional` — student qualifies on Z-score, but must also pass an aptitude test (Architecture, Music, Dance, Visual Arts, etc.)
- `not_eligible` — filtered out by the SQL `WHERE` clause; never returned

**Marginal flag:**
```python
margin = round(req.z_score - cutoff, 4)
is_marginal = margin <= MARGINAL_THRESHOLD  # 0.05
```
A margin of 0.05 means the cutoff could shift by 0.05 next year (which is common) and this student would no longer qualify. The UI shows a warning badge on these results.

**Confidence tier:**
```python
gap = max_year_in_db - used_year
tier = "current"       if gap == 0 else
       "previous_year" if gap == 1 else
       "estimated"
```
Honest communication to the student about how recent the data is.

**Audit log:**
```python
raw = f"{z_score}|{district_id}|{stream_id}|{used_year}"
request_hash = hashlib.sha256(raw.encode()).hexdigest()
session.add(EligibilityAudit(request_hash=request_hash, result_payload=response.model_dump()))
await session.commit()
```
Every single eligibility query is persisted with its inputs, outputs, and latency. If a student claims the system gave them wrong information, you can retrieve the exact query and result from the audit log.

---

#### `core/eligibility/subject_requirements.py`

Some courses require specific A/L subjects. Engineering requires Combined Mathematics. Medicine requires at least one science subject. This module evaluates whether a student's submitted subjects satisfy a JSON rule tree.

Rule tree example for Engineering:
```json
{"type": "requires_any", "subjects": ["Combined Mathematics", "Pure Mathematics"]}
```

The evaluator recursively walks the tree and returns True/False.

---

#### `core/eligibility/arts_basket.py`

Arts stream students are selected on 100% all-island merit (no district quota). This module implements the special eligibility logic for Arts-stream courses, which follows different rules from the standard district-quota calculation used by all other streams.

---

### `core/scoring/`

---

#### `core/scoring/engine.py`

Pure Python — no database, no LLM, no I/O. Takes eligible courses and a student profile, returns ranked courses with score breakdowns.

**The five dimensions:**
```python
DIMENSIONS = [
    ("z_margin",   _z_margin),    # how safely above the cutoff
    ("university", _university),  # whether it's at a preferred university
    ("interest",   _inert),       # interest alignment (reserved)
    ("career",     _inert),       # career goal alignment (reserved)
    ("industry",   _inert),       # industry outlook (reserved)
]
```

`_inert` returns `None` — meaning this dimension has no data and will not contribute to the score. Its weight is redistributed to active dimensions.

**z_margin — why tanh:**
```python
def _z_margin(course, profile, th):
    scale = float(th.get("z_margin_tanh_scale", 4.0))
    return (tanh(course.student_margin * scale) + 1.0) / 2.0
```

`tanh` is an S-curve (sigmoid-shaped). At margin = 0 (exactly at cutoff), it returns 0. At large margins, it approaches 1 but never exceeds it. Divided by 2, shifted, it maps to [0, 1].

Without tanh: a student 1.5 above the cutoff would score 3× higher than a student 0.5 above. With tanh: both score near 1.0, but the 1.5 student scores marginally higher. Large margins don't dominate the total score.

**Weight renormalization:**
```python
active_weight = sum(d.weight for d in breakdown) or 1.0
renorm_contribution = (d.weight / active_weight) * d.raw_score
```

Suppose interest, career, industry are all inert (no data). Their combined weight is 0.6. Only z_margin (0.3) and university (0.1) are active — total 0.4. Dividing by 0.4 scales the active dimensions back to fill the full 0–1 range. The principle: "no preferences → honest safety recommendation."

**Three buckets:**
- **Safe** — total_score ≥ threshold AND margin ≥ threshold
- **Ambitious** — right at the edge of the cutoff
- **Consider** — conditional courses (require aptitude test)

---

#### `core/scoring/config.py`

Loads the active scoring configuration from the `scoring_config` table:
```python
async def load_active_config(session):
    rows = await session.execute(text("SELECT key, value FROM scoring_config WHERE is_active = TRUE"))
    return {"weights": {...}, "thresholds": {...}}
```

The weights are stored in the database, not hardcoded. An admin can change the weight of `z_margin` vs `university` without touching code. The engine reads whatever is in the database each request.

---

#### `core/scoring/service.py`

Orchestrates everything for one recommendation request:

1. Calls `evaluate_eligibility()` — gets the full eligible course list
2. Calls `load_active_config()` — loads current weights from DB
3. Builds a `ScoringProfile` from the request
4. Calls `score_courses()` — pure Python scoring engine
5. Queries `course_stream_eligibility` for eligible stream codes (bulk, one query)
6. Queries for "also offered" courses (stream-eligible but no cutoff data in this district)
7. Assembles and returns the `RecommendationResponse`

**"Also offered" courses** are courses the student's stream is accepted for, but which have no cutoff data in their district. Maybe the university didn't offer this course in their district last year. These are shown separately in the UI as "may be worth investigating" rather than as ranked recommendations.

---

### `core/rag/`

---

#### `core/rag/retrieval.py`

Implements hybrid search over the 50 factsheets.

**Step 1 — Embed the query:**
```python
def _embed_query(client: genai.Client, query: str) -> list[float]:
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=query,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",       # optimised for search queries
            output_dimensionality=768,
        ),
    )
    return result.embeddings[0].values         # list of 768 floats
```

`task_type="RETRIEVAL_QUERY"` tells Gemini this embedding is for a search query (as opposed to a document being indexed). The embedding model uses this to apply query-specific optimisations.

**Step 2 — Vector search:**
```python
sql = text(
    "SELECT chunk_id, embedding <=> :vec AS dist "
    "FROM chunks WHERE embedding IS NOT NULL "
    "ORDER BY dist LIMIT :n"
)
```

`<=>` is the pgvector cosine distance operator. Lower distance = more similar meaning. This returns the 20 chunks whose meaning is closest to the query.

**Step 3 — Full-text search:**
```python
sql = text(
    "SELECT chunk_id, ts_rank(fts_vector, plainto_tsquery('english', :q)) AS rank "
    "FROM chunks WHERE fts_vector @@ plainto_tsquery('english', :q) "
    "ORDER BY rank DESC LIMIT :n"
)
```

`tsvector` — a PostgreSQL data type that stores a pre-processed, stemmed version of text for fast full-text searching. The `@@` operator checks if a document matches a query.

`plainto_tsquery` converts a natural language query ("what does an engineer earn?") into a search expression that handles stemming: "earn" matches "earning", "earnings", "earned".

`ts_rank` scores the quality of the match based on term frequency and position.

**Step 4 — RRF Fusion:**
```python
def _rrf(vector_hits, fts_hits, k=60):
    scores = {}
    for rank, (chunk_id, _) in enumerate(vector_hits, 1):
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    for rank, (chunk_id, _) in enumerate(fts_hits, 1):
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**Reciprocal Rank Fusion formula:** `score = Σ 1 / (k + rank_i)`

The constant `k=60` prevents top-ranked items from completely dominating. A chunk ranked #1 in both lists gets `1/61 + 1/61 = 0.0328`. A chunk ranked #1 in one list and not in the other gets `1/61 = 0.0164`. The #1 chunk in both lists wins, but a chunk appearing at #3 in both lists beats a chunk appearing at #1 in only one list.

**Why hybrid?**
- Pure semantic search misses exact matches: course code "119D", Z-score "1.5140", proper noun "IESL"
- Pure keyword search misses paraphrases: "how much can I earn" does not match "graduate salary"
- RRF captures both types at zero additional cost

---

### `core/chat/`

---

#### `core/chat/orchestrator.py`

The Gemini agentic loop.

**`FUNCTION_DECLARATIONS`** — 5 tool descriptions sent to Gemini. The model reads these and decides when to call each:

```python
FUNCTION_DECLARATIONS = [
    types.FunctionDeclaration(
        name="find_course",
        description="Search the database for degree programmes by name or abbreviation...",
        parameters=types.Schema(type="OBJECT", properties={
            "name_query": types.Schema(type="STRING", description="Course name or abbreviation")
        }, required=["name_query"])
    ),
    # ... lookup_course, get_cutoff_trend, search_knowledge, search_web
]
```

The description field is what the LLM reads to understand when to use each tool. Writing good tool descriptions is the primary way to guide the model's behavior.

**`_build_system_prompt(context)`** — Builds a per-request system prompt:

```python
def _build_system_prompt(context):
    prompt = f"""You are a senior academic advisor...

## Your tools and when to use them
- find_course: FIRST when student mentions a course by name/abbreviation
- lookup_course: to get Z-score cutoffs for a specific course number
- get_cutoff_trend: when student asks if cutoffs are rising or falling
- search_knowledge: for curriculum, career paths in factsheets
- search_web: for salary, job market, professional body requirements

## MANDATORY RULE: never say you don't have data without calling find_course first
"""
    if context:
        # Inject student profile
        prompt += f"- Z-score: {context['z_score']}\n"
        prompt += f"- District: {context['district_code']}\n"
        # Inject eligible courses table
        prompt += "| Course | Code | University | Cutoff | Margin |\n"
        for c in context.get('eligible_courses', []):
            prompt += f"| {c['course_name']} | {c['course_code']} | ... |\n"
```

This is the key personalisation mechanism. The model receives the student's verified eligible list in every message. When the student asks "I like robotics, what should I choose?", the model scans this table — it never recommends a course not in it.

**The loop:**
```python
async def chat(session, gen_client, embed_client, history, new_message, context):
    system_prompt = _build_system_prompt(context)
    contents = [build_contents_from_history...]
    contents.append(user_message)

    for turn in range(MAX_TOOL_TURNS):   # max 6 turns
        response = gen_client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=contents,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[types.Tool(function_declarations=FUNCTION_DECLARATIONS)]
            )
        )

        # Check if model called a tool
        fc_part = next((p for p in response.parts if p.function_call), None)

        if fc_part:
            # Execute the tool
            tool_result = await _execute_tool(session, embed_client, fc.name, fc.args)
            # Add the function call + result to the conversation history
            contents.append(model_function_call_content)
            contents.append(function_response_content)
            # Loop again — model now has the tool result
        else:
            # No function call — model produced a final text answer
            return response.text, tools_used
```

**Why `MAX_TOOL_TURNS = 6`?** Without a limit, a confused model could loop forever. 6 is enough for the most complex question: `find_course → lookup_course → get_cutoff_trend → search_knowledge → search_web → answer`.

---

#### `core/chat/tools.py`

Implementations of the 5 tools.

**`find_course(session, name_query)`**

Searches the courses table by name or abbreviation. Three-strategy fallback:

```python
# Abbreviation map — expands before searching
_ABBREV_MAP = {
    "ECS": "Electronics Computer Science",
    "ICT": "Information Communication Technology",
    "QS": "Quantity Surveying",
    "BST": "Biosystems Technology",
    "SE": "Software Engineering",
    # ... 20+ entries
}

async def find_course(session, name_query):
    # 1. Expand abbreviation if known
    expanded = _ABBREV_MAP.get(name_query.upper(), name_query)
    terms = expanded.split()

    # Strategy 1: ALL terms must match
    rows = await _course_search(session, terms, require_all=True)

    # Strategy 2: Try dropping one term at a time
    if not rows:
        for skip in range(len(terms)):
            subset = [t for i, t in enumerate(terms) if i != skip]
            rows = await _course_search(session, subset, require_all=True)

    # Strategy 3: Any single meaningful word
    if not rows:
        for term in [t for t in terms if len(t) > 3]:
            rows = await _course_search(session, [term])
            if rows: break
```

The search uses `ILIKE '%term%'` — case-insensitive substring match. "Electronics" matches "Electronics and Computer Science".

**`search_web(query)`**

```python
async def search_web(query: str) -> str:
    # Ensure Sri Lanka context
    if "sri lanka" not in query.lower():
        search_query = f"{query} Sri Lanka"

    # DuckDuckGo is synchronous — run in thread pool to avoid blocking event loop
    def _fetch():
        with DDGS() as ddgs:
            return list(ddgs.text(search_query, max_results=10))

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _fetch)

    # Score and sort by source trustworthiness
    scored = sorted(raw, key=lambda r: _trust_score(r.get("href", "")), reverse=True)
    return format_results(scored[:6])
```

**`run_in_executor`** — The DuckDuckGo library is synchronous (it blocks). If called directly in an `async def`, it would block the entire event loop — all other requests would freeze while waiting for the web search. `run_in_executor(None, _fetch)` runs it in the default thread pool executor, freeing the event loop to handle other requests in parallel.

**Trust scoring:**
```python
_TRUSTED_DOMAINS = {
    "ugc.ac.lk", "moe.gov.lk",           # government
    "cmb.ac.lk", "pdn.ac.lk", "mrt.ac.lk", # universities
    "iesl.lk", "slmc.lk", "icasl.lk",    # professional bodies
    "worldbank.org", "ilo.org",            # international orgs
    "accaglobal.com", "cimaglobal.com",   # finance bodies
    ...
}

def _trust_score(url: str) -> int:
    host = urlparse(url).netloc.lower()
    if host in _TRUSTED_DOMAINS or any(host.endswith("." + d) for d in _TRUSTED_DOMAINS):
        return 2   # highest — authoritative source
    if host.endswith(".lk") or host.endswith(".ac"):
        return 1   # local source
    return 0       # unknown
```

Results are sorted by trust score before being sent to the model. The model only sees the top 6 results, which are the most trustworthy.

---

## 6. `/apps/api` — FastAPI HTTP Layer

---

### `apps/api/main.py`

```python
app = FastAPI(title="Degree Guidance API", version="0.7.0")

app.include_router(chat.router)
app.include_router(eligibility.router)
app.include_router(recommendations.router)
app.include_router(reference.router)
app.include_router(auth.router)
app.include_router(admin_aliases.router)
app.include_router(admin_courses.router)
app.include_router(admin_ingestions.router)
app.include_router(admin_requirements.router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

FastAPI is the HTTP framework. It handles:
- Route registration (mapping URLs to Python functions)
- Request body parsing and validation against Pydantic schemas
- Response serialisation (Python objects → JSON)
- Automatic OpenAPI documentation at `/docs`
- Error handling (Pydantic validation errors → HTTP 422)

`include_router` mounts each router module. Each router is a self-contained file that handles one domain.

The `/health` endpoint exists so monitoring services (Docker healthchecks, Railway, etc.) can verify the app is running without hitting a real endpoint.

---

### `apps/api/dependencies.py`

FastAPI's dependency injection system.

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        # session.close() is called automatically after the route handler returns
```

When a route function declares `db: AsyncSession = Depends(get_db)`, FastAPI:
1. Calls `get_db()` before the route handler runs
2. Passes the yielded session to the route handler
3. Runs cleanup code (closing the session) after the handler returns

This is the **dependency injection** pattern — routes declare what they need; FastAPI provides it. Routes never create sessions directly.

```python
async def get_current_admin(
    credentials = Depends(_bearer),   # reads Authorization header
    db = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(401, "Missing bearer token")

    payload = decode_access_token(credentials.credentials)  # verify JWT

    if payload.get("role") not in ("admin", "superadmin"):
        raise HTTPException(403, "Admin privileges required")

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(401, "User not found or inactive")

    return user
```

Any admin route declares `admin: User = Depends(get_current_admin)` — FastAPI automatically verifies the JWT and returns the user object, or raises 401/403.

---

### `apps/api/routers/`

Each router is a thin HTTP layer. Business logic lives in `core/`. Routers just:
1. Declare the endpoint URL and HTTP method
2. Receive the validated request
3. Call the core function
4. Map domain exceptions to HTTP errors

**`eligibility.py`**
```python
@router.post("/api/v1/eligibility", response_model=EligibilityResponse)
async def check_eligibility(req: EligibilityRequest, db = Depends(get_db)):
    try:
        return await evaluate_eligibility(db, req)
    except EligibilityInputError as exc:
        raise HTTPException(422, detail=str(exc))
```

**`recommendations.py`**
```python
@router.post("/api/v1/recommendations", response_model=RecommendationResponse)
async def post_recommendations(payload: RecommendationRequest, db = Depends(get_db)):
    try:
        return await recommend(db, payload)
    except EligibilityInputError as exc:
        raise HTTPException(422, str(exc))
```

**`chat.py`** — Most complex router. Responsibilities:
- Resolve or create `Conversation` in DB
- Load existing `Message` history using `selectinload` (avoids N+1)
- Module-level Gemini client singletons (created once, reused)
- Call `run_chat()` agentic loop
- Persist new messages with `tool_calls` JSONB
- Return `{conversation_id, reply, tools_used}`

```python
# Module-level singletons — created once, reused across all requests
_gen_client: genai.Client | None = None

def _get_clients():
    global _gen_client
    if _gen_client is None:
        _gen_client = genai.Client(api_key=settings.gemini_api_key)
    return _gen_client
```

**`auth.py`** — Two endpoints:
- `POST /auth/login` — verifies email/password, returns JWT
- `GET /auth/me` — returns the current user (requires valid JWT)

**`reference.py`** — Read-only endpoints:
- `GET /api/v1/reference` — returns all districts, streams, universities for dropdown population

**`admin_courses.py`** — CRUD for courses. All routes require `get_current_admin`.
**`admin_aliases.py`** — CRUD for course aliases (alternative names).
**`admin_requirements.py`** — CRUD for course subject requirements.
**`admin_ingestions.py`** — Triggers and monitors PDF ingestion jobs via Arq.

---

### `apps/api/admin_audit.py`

Helper function used by admin routers to log every mutation:
```python
async def log_action(session, admin_user_id, action_type, target_table, target_id, before, after):
    session.add(AdminAction(
        admin_user_id=admin_user_id,
        action_type=action_type,     # "course_edit"
        target_table=target_table,   # "courses"
        target_id=str(target_id),    # "008B"
        before_value=before,         # {"name_en": "Old Name"}
        after_value=after,           # {"name_en": "New Name"}
    ))
```

Every admin write (edit course name, add alias, change requirement) calls this.

---

## 7. `/apps/worker` — Background Jobs

---

### `apps/worker/jobs/index_factsheets.py`

Runs once to index all factsheets. Re-running is safe (idempotent).

**Flow:**
```
For each .md file in content/factsheets/:
    1. Compute SHA-256 hash of file contents
    2. If hash matches an existing document_sources row → skip
    3. Split by H2 headers → list of (heading, text) chunks
    4. For each chunk:
       a. Call Gemini text-embedding-004 → 768-dim vector
       b. Sleep 0.7 seconds (rate limit: 85 req/min under free tier 100 limit)
       c. Insert into chunks table with embedding
    5. Commit to database
```

**Why chunk by H2 section?**
Each H2 section in a factsheet is a semantic unit: "Career Paths", "Curriculum", "Entry Requirements". If we chunk by fixed token count (300 tokens), a chunk might start mid-sentence in one section and end mid-sentence in another. The model would receive incoherent context. By splitting on headings, each chunk is a complete, topically consistent unit.

**SHA-256 idempotency:**
```python
content_hash = hashlib.sha256(raw.encode()).hexdigest()
existing = await session.scalar(
    select(DocumentSource).where(DocumentSource.content_hash == content_hash)
)
if existing and not force:
    return 0, True  # unchanged — skip
```

If the factsheet hasn't changed, the hash is identical to the stored one and the file is skipped entirely. Re-run the indexer at any time with zero risk.

---

### `apps/worker/jobs/ingest_zscores.py`

Reads a cutoff CSV and bulk-inserts into `z_score_cutoffs`.

- Validates each row (Z-score within [-2.0, 3.0], valid district code, valid course code)
- Handles NQC cells (stored as NULL `z_score`)
- Upserts on `(course_code, district_id, year)` — running twice for the same year is safe
- Writes an `ingestion_runs` row with status (success/failure), row counts, any errors

---

### `apps/worker/jobs/extract_pdf.py`

Triggered when an admin uploads a handbook PDF. Uses `pdfplumber` to:
1. Open the PDF
2. Locate Section 9 (by scanning for the section heading text)
3. Iterate over pages, extract each table
4. Normalise column headers (district names vary slightly between handbook editions)
5. Write structured rows to a CSV in `data/cutoffs_extracted/`

---

## 8. `/web` — Next.js Frontend

---

### App Router Structure

Next.js 14 uses the **App Router** — a file-based routing system.

```
web/src/app/
├── layout.tsx                      # root layout (HTML, fonts, global CSS)
├── globals.css                     # Tailwind base styles
├── favicon.ico
│
├── (student)/
│   ├── layout.tsx                  # student layout wrapper
│   └── page.tsx                    # / → student homepage, renders GuidanceFlow
│
├── admin/
│   ├── login/page.tsx              # /admin/login → login form
│   └── (panel)/
│       ├── layout.tsx              # admin sidebar + auth check
│       ├── page.tsx                # /admin → dashboard
│       ├── courses/page.tsx        # /admin/courses
│       ├── aliases/page.tsx        # /admin/aliases
│       ├── requirements/page.tsx   # /admin/requirements
│       └── ingestions/
│           ├── page.tsx            # /admin/ingestions → list
│           └── [runId]/page.tsx    # /admin/ingestions/:id → detail
│
└── api/
    ├── auth/[...nextauth]/route.ts # NextAuth handler (login, session, etc.)
    ├── public/[...path]/route.ts   # open proxy → FastAPI (no auth)
    └── bff/[...path]/route.ts      # auth-gated proxy → FastAPI (admin)
```

**Route groups** — `(student)` and `(panel)` are route groups. The parentheses make the folder name invisible in the URL. They exist to apply a shared `layout.tsx` to a set of pages without affecting the URL structure.

**`[runId]`** — a dynamic route segment. `/admin/ingestions/abc123` maps to `page.tsx` with `params.runId = "abc123"`.

**`[...nextauth]`** — a catch-all dynamic route. `/api/auth/anything/here` all go to this handler. NextAuth uses multiple sub-paths internally.

**`[...path]`** — catch-all for the BFF proxy. One file handles any path under `/api/public/`.

---

### API Routes (BFF Proxy)

**`web/src/app/api/public/[...path]/route.ts`**

```typescript
const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";

async function proxy(req: NextRequest, ctx) {
    const path = ctx.params.path.join("/");
    const url = `${API}/api/v1/${path}${req.nextUrl.search}`;

    const upstream = await fetch(url, {
        method: req.method,
        headers: { "content-type": req.headers.get("content-type") },
        body: req.body,
    });

    return new Response(upstream.body, { status: upstream.status });
}

export const GET = proxy;
export const POST = proxy;
```

The browser calls `/api/public/eligibility`. Next.js forwards to `http://localhost:8077/api/v1/eligibility`. The browser never knows the FastAPI URL or port.

**Why proxy through Next.js?**
- FastAPI never needs CORS configuration (cross-origin requests come from Next.js server, not the browser)
- The FastAPI port (8077) is never exposed to the internet
- Auth tokens can be attached server-side before forwarding
- One file handles all student-facing endpoints

**`web/src/app/api/bff/[...path]/route.ts`**

```typescript
async function proxy(req: NextRequest, ctx) {
    // Read the encrypted NextAuth session cookie
    const token = await getToken({ req, secret: process.env.AUTH_SECRET });
    const accessToken = token?.accessToken;   // the FastAPI JWT
    const role = token?.role;

    if (!accessToken || !ADMIN_ROLES.has(role)) {
        return Response.json({ detail: "Not authenticated" }, { status: 401 });
    }

    // Attach the FastAPI JWT as a Bearer header
    const headers = new Headers();
    headers.set("authorization", `Bearer ${accessToken}`);

    const upstream = await fetch(`${API}/api/${path}`, { headers, method: req.method, body: req.body });
    return new Response(upstream.body, { status: upstream.status });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
```

The FastAPI access token is stored in the encrypted NextAuth JWT cookie. The browser never sees it — it lives server-side only. The BFF reads it and attaches it as a Bearer header when forwarding to FastAPI. This is the security model described in masterplan §11.B.

---

### Auth (NextAuth v5)

**`web/src/auth.config.ts`** — Edge-safe configuration.

```typescript
callbacks: {
    jwt({ token, user }) {
        if (user) {
            token.accessToken = user.accessToken;  // store FastAPI JWT in NextAuth JWT
            token.role = user.role;
        }
        return token;
    },
    session({ session, token }) {
        session.user.role = token.role;  // make role available to server components
        // accessToken is NOT copied to session — stays encrypted in JWT only
        return session;
    },
    authorized({ auth, request }) {
        const role = auth?.user?.role;
        const isAdmin = role === "admin" || role === "superadmin";
        if (request.nextUrl.pathname.startsWith("/admin")) return isAdmin;
        return true;
    },
}
```

The `jwt` callback runs when a token is created/refreshed. It stores the FastAPI `accessToken` in the NextAuth JWT. The `session` callback controls what data is available via `auth()` / `useSession()` — the access token is deliberately NOT included so it never reaches the browser.

The `authorized` callback is what the middleware uses to gate `/admin/*` routes.

**`web/src/middleware.ts`**

```typescript
export default NextAuth(authConfig).auth;
export const config = { matcher: ["/admin", "/admin/:path*"] };
```

This runs at the **Edge** — before any server component or API route handler. If the user hits `/admin/courses` without a valid session, they're redirected to `/admin/login` before any page code runs. This is the outermost layer of auth protection.

**`web/src/auth.ts`** — Full auth config with the Credentials provider.

```typescript
providers: [
    Credentials({
        async authorize(credentials) {
            const res = await fetch(`${API}/auth/login`, {
                method: "POST",
                body: JSON.stringify(credentials),
            });
            if (!res.ok) return null;
            const data = await res.json();
            return { id: data.user_id, email: data.email, role: data.role, accessToken: data.access_token };
        }
    })
]
```

When an admin submits the login form, NextAuth calls `authorize()`. It forwards the credentials to FastAPI's `/auth/login`, which verifies the password with bcrypt and returns a JWT. `authorize()` returns the user object, which NextAuth stores in its encrypted session cookie.

---

### Student Components

**`web/src/components/student/guidance-flow.tsx`**

The entire student experience in one component. A multi-step wizard:

```typescript
const [step, setStep] = useState(0);              // 0–4
const [zScore, setZScore] = useState(1.5);
const [districtCode, setDistrictCode] = useState<string | null>(null);
const [streamCode, setStreamCode] = useState<string | null>(null);
const [subjects, setSubjects] = useState([null, null, null]);
const [interests, setInterests] = useState("");
const [results, setResults] = useState<RecommendationResponse | null>(null);
```

Steps:
- 0 → Z-score slider
- 1 → District dropdown (populated from `/api/public/reference`)
- 2 → Stream picker (6 cards with inline SVG icons)
- 3 → Subjects: 3 rows of (subject name + grade selector)
- 4 → Preferences: preferred universities + free text interests

On submit:
```typescript
const res = await fetch("/api/public/recommendations", {
    method: "POST",
    body: JSON.stringify({ z_score, district_code, stream_code, subjects, interests, ... })
});
const data = await res.json();
setResults(data);
setView("results");
```

After receiving results, it passes them to both `ResultsView` and `ChatPanel`:
```typescript
<ChatPanel context={{
    z_score: zScore,
    district_code: districtCode,
    stream_code: streamCode,
    subjects: subjects.filter(s => s !== null),
    eligible_courses: results.recommendations.map(r => ({
        course_code: r.course_code,
        course_name: r.course_name,
        university: r.university_name,
        cutoff: r.cutoff_z_score,
        margin: r.student_margin,
        bucket: r.bucket,
    }))
}} />
```

This context is what gets injected into the chatbot's system prompt. The chatbot knows exactly which courses the student can get into.

---

**`web/src/components/student/results-view.tsx`**

Renders the ranked course cards. Groups courses by bucket (Safe / Ambitious / Consider). Each card shows:
- Course name and university
- Cutoff Z-score and student margin
- Safety bucket badge (colour-coded)
- Score breakdown bar (which dimensions contributed)
- Available teaching mediums (Sinhala / Tamil / English)
- Marginal warning if margin ≤ 0.05

---

**`web/src/components/student/chat-panel.tsx`**

Floating chat bubble that expands into a full chat interface.

```typescript
const [conversationId, setConversationId] = useState<string | null>(null);

async function sendMessage(text: string) {
    const res = await fetch("/api/public/chat", {
        method: "POST",
        body: JSON.stringify({
            session_id: sessionId,          // anonymous browser identifier
            conversation_id: conversationId, // null on first message
            message: text,
            context: context,               // student profile + eligible courses
        })
    });
    const data = await res.json();
    setConversationId(data.conversation_id);  // save for multi-turn continuity
    addMessage({ role: "assistant", content: data.reply, tools: data.tools_used });
}
```

First message: `conversation_id` is null. Backend creates a new conversation and returns its UUID. Second message onward: the UUID is sent back, backend loads the history and continues the conversation.

Tool badges — `data.tools_used` is an array of tool names. Rendered as small coloured chips under each assistant message so the student can see what the advisor actually looked up:
```typescript
{message.tools?.map(tool => (
    <span className="badge">{tool}</span>
))}
```

---

### Admin Components

**`web/src/app/admin/(panel)/layout.tsx`** — Admin shell with sidebar navigation. Checks the session for role. If not admin, shows an error (middleware should have caught this first, but defence in depth).

**`web/src/components/admin/sidebar.tsx`** — Navigation links for Ingestions, Aliases, Courses, Requirements.

**`web/src/app/admin/login/page.tsx`** — Login form. Calls NextAuth's `signIn("credentials", {...})` on submit.

**`web/src/app/admin/(panel)/courses/page.tsx`** — Fetches from `/api/bff/admin/courses` (auth-gated). Renders a table of all 261 courses with edit functionality.

---

## 9. `/alembic` — Database Migrations

Alembic tracks every change to the database schema as a numbered migration file. Run `alembic upgrade head` to apply all pending migrations.

**Why migrations instead of just writing SQL?**
- Every change is version-controlled alongside the code
- Every change is reversible (`alembic downgrade -1`)
- Multiple developers can apply the same changes in the same order
- You know exactly what version of the schema is deployed in production

**Migration sequence (32 total):**

| # | File | What it does |
|---|---|---|
| 01 | `01_districts` | CREATE TABLE districts — 25 Sri Lankan districts with is_disadvantaged flag |
| 02 | `02_streams` | CREATE TABLE streams — 6 A/L exam streams |
| 03 | `03_subjects` | CREATE TABLE subjects — all A/L subjects |
| 04 | `04_stream_subjects` | CREATE TABLE stream_subjects — which subjects belong to which stream |
| 05 | `05_mediums` | CREATE TABLE mediums — Sinhala, Tamil, English |
| 06 | `06_universities` | CREATE TABLE universities — 21 state HEIs, seeded from CSV |
| 07 | `07_faculties` | CREATE TABLE faculties |
| 08 | `08_special_provision` | CREATE TABLE special_provision_categories |
| 09 | `09_courses` | CREATE TABLE courses — 261 degree programmes, seeded from courses.csv |
| 10 | `10_course_markers` | ADD requires_aptitude_test, selection_basis columns to courses |
| 11 | `11_name_cleanup` | Fix course names — normalise Unicode encoding issues from CSV import |
| 12 | `12_stream_eligibility` | CREATE TABLE course_stream_eligibility — seeded from CSV |
| 13 | `13_aliases` | CREATE TABLE course_aliases — alternative names for courses |
| 14 | `14_z_score_cutoffs` | CREATE TABLE z_score_cutoffs — ~6500 rows, 2023 handbook |
| 15 | `15_ingestion_runs` | CREATE TABLE ingestion_runs — tracks PDF ingestion job history |
| 16 | `16_missing_courses` | INSERT 4 courses missed in initial seed |
| 17 | `17_unicode_aliases` | Normalise Unicode in alias table |
| 18 | `18_eligibility_tables` | CREATE TABLE eligibility_audit — every eligibility query logged |
| 19 | `19_auth` | CREATE TABLE users + admin_actions — admin auth foundation |
| 20 | `20_auth_events` | CREATE TABLE auth_events — login/logout audit trail |
| 21 | `21_fix_006k` | Data fix: 007K was misread as 006K by PDF extractor, corrected |
| 22 | `22_scoring_config` | CREATE TABLE scoring_config — 5 configurable weights, seeded |
| 24 | `24_course_requirements` | CREATE TABLE course_requirements — per-course subject rules |
| 25 | `25_seed_requirements` | INSERT subject rules for ~50 courses from handbook §2.2 |
| 26 | `26_cross_stream_fix` | Fix cross-stream eligibility misclassifications |
| 27 | `27_arts_law_subjects` | Complete Arts and Law subject requirement entries |
| 28 | `28_more_cross_stream` | Fix additional cross-stream edge cases |
| 29 | `29_tighten_rules` | Tighten subject rules for borderline courses |
| 30 | `30_seed_specials` | INSERT requirements for aptitude-test courses |
| 31 | `31_rag_tables` | CREATE TABLE document_sources, chunks — with pgvector column |
| 32 | `32_chat_tables` | CREATE TABLE conversations, messages |

---

## 10. `/content/factsheets` — The Knowledge Base

50 hand-written Markdown files. One per degree programme. Each follows the same structure:

```markdown
# Engineering (008)

## Overview
Sri Lanka trains engineers through a 4-year BEng Honours programme...

## Curriculum
Year 1-2: Mathematics, Engineering Fundamentals, Materials Science...
Year 3-4: Specialisation — Civil, Electrical, Mechanical, Chemical...

## Career Paths
Civil: structural engineering, project management, government public works
Electrical: power generation, telecommunications, electronics industry
...

## Entry Requirements
Physical Science stream with Combined Mathematics is required...

## Graduate Outcomes
Government service starting salary: LKR 55,000–80,000
Private sector starting salary: LKR 80,000–150,000
...
```

The indexer splits by `## ` headings and embeds each section separately. When the chatbot calls `search_knowledge("engineering career paths")`, it retrieves specifically the Career Paths section — not the entire file.

This means the 311 chunks in the database each represent one complete, topically coherent unit of knowledge. Retrieval is precise.

---

## 11. `/data` — Raw Data and Seeds

**`data/raw_handbooks/`**
Four UGC handbook PDFs (2021, 2023, 2024, 2025). These are the source of truth for all Z-score data. Never modified — only read by the PDF extractor.

**`data/cutoffs_extracted/zscores_2023.csv`**
Output of the PDF extractor. ~6,500 rows. Columns: `course_code, district_code, z_score, notes`.

**`data/seeds/courses.csv`**
All 261 degree programmes with codes, names, university codes, durations. Used in migration 09. Format: `course_code, course_number, university_code, name_en, name_si, name_ta, duration_years, ...`

**`data/seeds/course_stream_eligibility.csv`**
Which A/L streams each course accepts. Used in migration 12. Format: `course_code, stream_code`.

**`data/seeds/course_requirements_data.py`**
Python data (not CSV) for complex subject requirements. Used in migration 25. Stored as Python because the rule trees are nested JSON structures that are easier to write and review in Python syntax.

**`data/test/sample_zscores_2023.csv`**
A small subset of the cutoffs CSV used in integration tests. Tests don't use the full 6,500-row dataset.

---

## 12. `/scripts` — Utility Scripts

**`scripts/create_admin.py`**

Interactive script to create the first admin user:
```python
email = input("Email: ")
password = getpass.getpass("Password: ")
hashed = hash_password(password)
session.add(User(email=email, password_hash=hashed, role="admin"))
await session.commit()
```

Run once on a fresh deployment: `uv run python scripts/create_admin.py`

**`scripts/native_pdf_extractor/extract_cutoffs.py`**

Uses pdfplumber to extract Section 9 tables from UGC handbook PDFs:
1. Opens the PDF with pdfplumber
2. Scans each page for "Section 9" heading text
3. Extracts the table from each Section 9 page
4. Normalises column headers (district names vary between editions)
5. Handles "NQC" cells (No Qualified Candidates → None)
6. Validates Z-scores are within [-2.0, 3.0]
7. Writes to `data/cutoffs_extracted/zscores_YYYY.csv`

**`scripts/native_pdf_extractor/verify_codes.py`**

After extraction, cross-checks every course code in the CSV against the `courses` table in the database. If an extracted code doesn't match a known course, it's flagged. This caught the 007K → 006K misread (migration 21).

**`scripts/native_pdf_extractor/make_readable_csv.py`**

Converts the raw extracted CSV (course codes × district codes) into a human-readable format with full course names and district names for manual verification.

---

## 13. `/tests` — Test Suite

**`tests/unit/`** — Pure Python. No database needed. Run instantly.

- `test_scoring_engine.py` — Tests the scoring formula, tanh normalisation, weight renormalization, bucket assignment
- `test_subject_requirements.py` — Tests the subject rule evaluator against known pass/fail cases
- `test_arts_basket.py` — Tests Arts stream special eligibility logic

**`tests/integration/`** — Hit the real database (configured via `.env`). Each test runs in a transaction that is rolled back at the end — no permanent test data.

- `test_eligibility_engine.py` — Runs the full eligibility engine against known inputs and verifies outputs
- `test_eligibility_api.py` — Full HTTP round-trip: POST to FastAPI → engine → database → response
- `test_recommendations.py` — Verifies scoring and ranking behaviour
- `test_auth.py` — Login, JWT verification, protected route access
- `test_cutoff_coverage.py` — Data integrity: verifies no districts have zero cutoffs for common courses
- `test_admin_courses.py`, `test_admin_aliases.py`, `test_admin_ingestions.py` — Admin API CRUD

**`tests/fixtures/eligibility_cases.yaml`**

Declarative test cases in YAML — no code:
```yaml
- z_score: 1.8
  district: COLOMBO
  stream: PHYSICAL_SCIENCE
  subjects:
    - subject: Physics
      grade: A
    - subject: Combined Mathematics
      grade: B
  expected_includes:
    - "008B"   # Engineering at Moratuwa
    - "012T"   # Computer Science at UCSC
  expected_excludes:
    - "001A"   # Medicine at CMB — cutoff is ~1.95
```

The test runner reads all cases, runs the eligibility engine for each, and asserts the expected courses appear (or don't appear) in the results.

---

## 14. `/ops` — Infrastructure

**`ops/docker-compose.yml`**

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: degree-redis
    ports:
      - "6379:6379"
    command: ["redis-server", "--appendonly", "yes"]   # persist data to disk
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
```

Redis 7 in Alpine Linux (minimal image). `--appendonly yes` enables AOF persistence — every write is appended to a log file so data survives container restarts.

PostgreSQL runs natively in WSL (not in Docker) because pgvector requires native compilation against the Postgres installation and is simplest to set up as a native Ubuntu package.

---

## 15. Complete Request Flow — End to End

Here is a single student question traced through every layer of the system.

**The question:** "What is the cutoff for ECS?"

```
1. BROWSER
   User types "What is the cutoff for ECS?" in chat-panel.tsx
   sendMessage() calls fetch("/api/public/chat", {
       method: "POST",
       body: {
           session_id: "anon-abc123",
           conversation_id: "3fa85f64-...",  // from previous message
           message: "What is the cutoff for ECS?",
           context: {
               z_score: 1.5,
               district_code: "COLOMBO",
               stream_code: "PHYSICAL_SCIENCE",
               eligible_courses: [{course_code: "008C", ...}, ...]
           }
       }
   })

2. NEXT.JS PROXY
   /api/public/[...path]/route.ts receives the request
   Strips /api/public prefix → /api/v1/chat
   Forwards to http://localhost:8077/api/v1/chat

3. FASTAPI: chat.py
   Validates ChatRequest with Pydantic
   get_db() creates AsyncSession from the connection pool
   Resolves conversation from UUID → loads message history with selectinload

4. FASTAPI: chat.py → orchestrator.py
   Calls run_chat(session, gen_client, embed_client, history, message, context)

5. ORCHESTRATOR: builds system prompt
   - Student profile section: "Z-score: 1.5, District: COLOMBO, ..."
   - Eligible courses table with 008C, 012T, 090A, etc.
   - Rules: "never guess cutoffs", "call find_course first", etc.

6. ORCHESTRATOR: Turn 1
   Calls Gemini with message + 5 tool declarations
   Gemini reads: "What is the cutoff for ECS?"
   Gemini decides: I don't know what ECS is. Call find_course.
   Returns: FunctionCall(name="find_course", args={"name_query": "ECS"})

7. TOOLS: find_course("ECS")
   _ABBREV_MAP["ECS"] = "Electronics Computer Science"
   terms = ["Electronics", "Computer", "Science"]
   SQL: SELECT course_code, name_en FROM courses
        WHERE name_en ILIKE '%Electronics%'
          AND name_en ILIKE '%Computer%'
          AND name_en ILIKE '%Science%'
   Result: "119D — Electronics and Computer Science, University of Kelaniya"
   Returns formatted result string to orchestrator

8. ORCHESTRATOR: Turn 2
   Appends function call + result to contents
   Calls Gemini again
   Gemini reads: "found 119D at Kelaniya, course number 119"
   Gemini decides: I need the actual cutoff. Call lookup_course.
   Returns: FunctionCall(name="lookup_course", args={"course_number": "119"})

9. TOOLS: lookup_course("119")
   SQL query on z_score_cutoffs WHERE course_number = '119' AND year = 2023
   Joins with districts to filter for COLOMBO district
   Result: "Cutoff for Colombo district 2023: 1.5140
            Course: Electronics and Computer Science
            University: University of Kelaniya
            Duration: 3 years"
   Returns formatted result string

10. ORCHESTRATOR: Turn 3
    Appends function call + result to contents
    Calls Gemini again
    Gemini reads: "cutoff is 1.5140, student's score is 1.5"
    Gemini decides: I have enough data. Writes final answer.
    Returns text: "Electronics and Computer Science (119D) at the University of
    Kelaniya has a 2023 cutoff of 1.5140 for the Colombo district. Your Z-score
    of 1.5 is 0.0140 below this cutoff, meaning you would not have qualified in
    2023. However, cutoffs shift by 0.05–0.10 each year..."

11. ORCHESTRATOR returns
    (reply="Electronics and Computer Science...", tools_used=["find_course","lookup_course"])

12. FASTAPI: chat.py
    INSERT INTO messages (role='user', content='What is the cutoff for ECS?', conversation_id=...)
    INSERT INTO messages (role='assistant', content='Electronics and...', tool_calls='["find_course","lookup_course"]')
    await session.commit()
    Returns ChatResponse(conversation_id="3fa85f64-...", reply="...", tools_used=[...])

13. NEXT.JS PROXY
    Forwards the JSON response to the browser

14. BROWSER: chat-panel.tsx
    data = await res.json()
    setConversationId(data.conversation_id)  // persisted for next message
    addMessage({
        role: "assistant",
        content: data.reply,
        tools: data.tools_used  // ["find_course", "lookup_course"]
    })
    Renders the message with tool badges: [find_course] [lookup_course]
```

---

## 16. Concept Dictionary

Every technical concept used in this project, explained plainly.

| Concept | What it means | Where in this project |
|---|---|---|
| **Async/await** | A way to write code that can pause and let other code run while waiting (for a DB query, a web request, etc.) — without using multiple threads. `async def` declares an async function. `await` pauses execution until the awaited thing completes. | Every `async def` function in FastAPI, SQLAlchemy, the orchestrator |
| **Event loop** | Python's internal scheduler for async code. Runs coroutines, switches between them when one is waiting, resumes them when ready. One thread, many concurrent operations. | The Uvicorn ASGI server runs the event loop |
| **Connection pool** | A fixed set of pre-created database connections reused across requests — opening a connection is expensive, so we share them. | `create_async_engine` in `core/db.py` |
| **ORM** | Object-Relational Mapping — maps Python classes to DB tables. `session.add(user)` instead of `INSERT INTO users...`. | `core/models/` — all the SQLAlchemy model classes |
| **Pydantic** | Python library for data validation using type annotations. Used to validate API request bodies and serialize responses. | `core/schemas/` — all the schema classes |
| **Dependency injection** | FastAPI's system for providing dependencies (DB sessions, auth checks) to route handlers declaratively via `Depends(...)`. | `apps/api/dependencies.py` — `get_db`, `get_current_admin` |
| **JWT** | JSON Web Token — a signed, base64-encoded JSON payload used as a stateless auth token. The server never needs to look up sessions in the database. | `core/security.py` — `create_access_token`, `decode_access_token` |
| **bcrypt** | A deliberately slow password hashing algorithm. Makes brute-force attacks computationally expensive. | `core/security.py` — `hash_password`, `verify_password` |
| **Alembic migration** | A versioned script that changes the database schema. Tracked in version control. Reversible. | `alembic/versions/` — 32 numbered migration files |
| **Bound parameters** | Placeholders (`:param`) in SQL queries where the value is passed separately from the SQL string, preventing SQL injection. | Every `text(...)` query in `core/eligibility/engine.py` |
| **pgvector** | A PostgreSQL extension that adds a `vector` column type and the `<=>` cosine distance operator for nearest-neighbour search. | `chunks.embedding` column in `core/models/rag.py` |
| **Embedding** | A numerical representation of text as a high-dimensional vector (768 numbers). Semantically similar texts have vectors that are close together in vector space. | Gemini `text-embedding-004` → stored in pgvector |
| **Cosine similarity** | A measure of how similar two vectors are based on the angle between them. 1.0 = identical direction, 0.0 = perpendicular, -1.0 = opposite. | `<=>` operator in vector search SQL |
| **Full-text search (FTS)** | PostgreSQL's built-in keyword search using `tsvector` — preprocessed, stemmed text that enables fast `@@` matching. | `chunks.fts_vector`, `plainto_tsquery` in `core/rag/retrieval.py` |
| **RRF (Reciprocal Rank Fusion)** | A formula that merges two ranked lists: `score = Σ 1 / (k + rank)`. Used to combine semantic and keyword search results without needing a trained re-ranker. | `_rrf()` in `core/rag/retrieval.py` |
| **Agentic loop** | A pattern where an LLM iterates: decide → call a tool → observe the result → decide again. Continues until the model produces a final text answer. | `chat()` in `core/chat/orchestrator.py` |
| **Function calling** | A Gemini API feature that lets the model request structured tool calls (`FunctionCall`) instead of producing text. The app executes the tool and feeds the result back to the model. | `FUNCTION_DECLARATIONS` in `core/chat/orchestrator.py` |
| **System prompt** | A set of instructions given to the LLM at the start of every conversation. Controls the model's persona, tool usage rules, and knowledge context. | `_build_system_prompt()` in `core/chat/orchestrator.py` |
| **BFF (Backend For Frontend)** | A server-side proxy layer between the browser and the backend API. Handles auth, hides internal URLs, adds headers. | `/api/public/` and `/api/bff/` routes in Next.js |
| **App Router** | Next.js 14's file-based routing system. Folders map to URL segments. Files named `page.tsx` are pages, `layout.tsx` are shared wrappers, `route.ts` are API handlers. | `web/src/app/` structure |
| **Route groups** | Folders in Next.js whose names are in parentheses — `(student)`. Invisible in the URL. Used to apply a shared layout to a set of pages. | `(student)/`, `(panel)/` in the app directory |
| **Catch-all route** | `[...path]` in Next.js — matches any path segment, however deep. Used for the BFF proxy to forward any endpoint. | `/api/public/[...path]/route.ts` |
| **tanh normalisation** | Mapping a value through the hyperbolic tangent function to squeeze it into a [0, 1] range with diminishing returns. Prevents very large values from dominating. | `_z_margin()` in `core/scoring/engine.py` |
| **Weight renormalization** | When some scoring dimensions have no data, redistributing their weight proportionally to active dimensions so scores still sum correctly. | `score_courses()` in `core/scoring/engine.py` |
| **Idempotency** | An operation that produces the same result whether run once or 100 times. "Run again safely." | SHA-256 hash check in `index_factsheets.py`; upsert in `ingest_zscores.py` |
| **JSONB** | PostgreSQL's binary JSON column type. More efficient than TEXT-stored JSON because it's parsed and stored in a binary format that enables JSON operators. | `tool_calls` in `messages`, `before_value`/`after_value` in `admin_actions` |
| **run_in_executor** | Python asyncio function that runs a blocking (synchronous) function in a thread pool so it doesn't block the event loop. | `search_web()` in `core/chat/tools.py` |
| **Cascade delete** | A database relationship where deleting a parent row automatically deletes all child rows. `Conversation DELETE → all Messages DELETE`. | `ForeignKey("conversations.conversation_id", ondelete="CASCADE")` |
| **CheckConstraint** | A database-level constraint that enforces a condition on column values. `role IN ('user', 'assistant', 'system')` — the DB refuses any other value. | `messages.role`, `users.role`, `auth_events.event_type` |
| **Partial index** | A database index that only indexes rows matching a condition. `WHERE role != 'student'` means the index only covers admin users — tiny and fast. | `idx_users_role` in `core/models/auth.py` |
| **selectinload** | SQLAlchemy loading strategy that fetches related objects with a second `IN` query, avoiding N+1 queries. | Loading `Conversation.messages` in `apps/api/routers/chat.py` |
| **Confidence tier** | A label (current / previous\_year / estimated) indicating how old the cutoff data is relative to the most recent data in the database. | `_confidence()` in `core/eligibility/engine.py` |
| **Marginal flag** | A boolean set when a student's Z-score margin above the cutoff is ≤ 0.05 — warning that a small cutoff shift could flip their eligibility. | `is_marginal` in `EligibilityResultItem` |
| **Audit log** | An append-only record of every eligibility query or admin action. Used for debugging, accountability, and reproducibility. | `eligibility_audit`, `admin_actions`, `auth_events` tables |
