# Complete File Map — What Every File Does

## What this is / why it exists

A directory-by-directory annotated map of the repository: what lives where and
what each significant file is responsible for. Use it to find the code behind any
behaviour, then jump to the subsystem doc that explains it in depth. Data/seed
directories are marked briefly.

> **Legend.** 🐍 Python · ⚛️ TypeScript/React · 🗄️ migration · 📄 content/data.
> "→ NN" points to the subsystem doc that goes deeper.

---

## Top level

| Path | What it is |
| --- | --- |
| `apps/` | The two runnable processes (API + worker). |
| `core/` | Shared domain logic — no HTTP, no UI. Imported by both processes. |
| `web/` | The Next.js 14 frontend (student + admin). |
| `alembic/` | Database migration history (43 migrations). |
| `content/factsheets/` | 📄 129 per-course markdown factsheets (the RAG seed). |
| `data/` | 📄 Raw handbooks, extracted CSVs, seed CSVs, test data. |
| `scripts/` | Ops + one-off tooling (PDF extractor, prod migrations). |
| `tests/` | Unit + integration suite. → `14-testing-quality.md` |
| `docs/` | This documentation + plan/runbook docs. |
| `pyproject.toml` | 🐍 Python deps (uv-managed) + tool config. → `02-tech-stack.md` |
| `alembic.ini` | Alembic configuration. |

---

## `apps/api/` — the FastAPI web service → `09`, `13`

| File | Responsibility |
| --- | --- |
| `main.py` | 🐍 App factory; registers every router + the rate-limit + CORS middleware. |
| `dependencies.py` | 🐍 `get_db` (session) + `get_current_admin` (the auth gate). |
| `admin_audit.py` | 🐍 `log_admin_action` — the audit-write helper. |
| `guards.py` | 🐍 Per-IP rate limiting + the daily Gemini budget. → `12` |
| `queue.py` | 🐍 arq enqueue helpers (`enqueue_extract_pdf`, `enqueue_index_factsheet`, `enqueue_index_article`). |
| `routers/eligibility.py` | 🐍 `POST /api/v1/eligibility`. → `05` |
| `routers/recommendations.py` | 🐍 `POST /api/v1/recommendations`. → `06` |
| `routers/chat.py` | 🐍 `POST /api/v1/chat` (the agent endpoint). → `08` |
| `routers/reference.py` | 🐍 districts/streams/universities, `/years`, cutoff history. |
| `routers/student.py` | 🐍 Signed-in student conversation history. |
| `routers/auth.py` | 🐍 `POST /api/auth/login`, `GET /api/auth/me`. → `13` |
| `routers/admin_ingestions.py` | 🐍 The full ingestion lifecycle. → `04` |
| `routers/admin_courses.py` | 🐍 Courses + streams editor + onboarding. → `09` |
| `routers/admin_cutoffs.py` | 🐍 Cutoff matrix/export. |
| `routers/admin_factsheets.py` | 🐍 Factsheet list/edit/reindex. → `07` |
| `routers/admin_articles.py` | 🐍 Article CRUD/reindex (Phase 8.6). → `07` |
| `routers/admin_knowledge.py` | 🐍 Indexed-knowledge browser + staleness. → `07` |
| `routers/admin_agent.py` | 🐍 Agent-config CRUD + sandbox. → `08` |
| `routers/admin_conversations.py` | 🐍 Conversation viewer + `/usage`. |
| `routers/admin_users.py` | 🐍 Admin management. |
| `routers/admin_aliases.py` | 🐍 Alias CRUD. |
| `routers/admin_requirements.py` | 🐍 Subject-rule listing. |

## `apps/worker/` — the arq background worker → `04`, `12`

| File | Responsibility |
| --- | --- |
| `settings.py` | 🐍 `WorkerSettings`: registered jobs, Redis, `job_timeout=3600`. |
| `jobs/extract_pdf.py` | 🐍 The PDF extraction job. → `04` |
| `jobs/ingest_zscores.py` | 🐍 The Step-4 CSV loader + overrides/unmapped/coverage. → `04` |
| `jobs/index_factsheets.py` | 🐍 Factsheet chunk + embed + index. → `07` |
| `jobs/index_articles.py` | 🐍 Article indexing (reuses the factsheet machinery). → `07` |

---

## `core/` — shared domain logic

| File / dir | Responsibility |
| --- | --- |
| `config.py` | 🐍 `Settings` — all env-driven config. → `02`, `12` |
| `db.py` | 🐍 Async engine + `AsyncSessionLocal` + `Base`. |
| `security.py` | 🐍 bcrypt + JWT primitives. → `13` |
| `ratelimit.py` | 🐍 Sliding-window limiter + daily budget. → `12` |
| `chat/orchestrator.py` | 🐍 The agentic loop. → `08` |
| `chat/tools.py` | 🐍 The five agent tools. → `08` |
| `chat/agent_config.py` | 🐍 Runtime agent-config resolution + placeholder injection. → `08` |
| `eligibility/engine.py` | 🐍 The deterministic eligibility engine. → `05` |
| `eligibility/subject_requirements.py` | 🐍 JSONB subject-rule evaluator. → `05` |
| `eligibility/arts_basket.py` | 🐍 Arts 4-basket special case. → `05` |
| `scoring/engine.py` | 🐍 The pure scorer + buckets. → `06` |
| `scoring/service.py` | 🐍 Recommendation orchestration + ordering. → `06` |
| `scoring/config.py` | 🐍 Scoring-config loader. → `06` |
| `rag/retrieval.py` | 🐍 Hybrid pgvector + FTS + RRF retrieval. → `07` |
| `ingestion/grid_extractor.py` | 🐍 The rotated-grid extractor. → `04` |
| `ingestion/unicode_section.py` | 🐍 The book's Uni-Code table parser. → `04` |
| `ingestion/book_search.py` | 🐍 Whole-book presence index. → `04` |
| `ingestion/pdf_pages.py` | 🐍 `iter_pages_chunked` (memory-safe). → `04` |
| `ingestion/artifact_store.py` | 🐍 Cross-instance artifact store. → `04`, `12` |
| `ingestion/column_mapper.py` | 🐍 Deterministic mapping suggestions. → `04` |
| `ingestion/stream_tags.py` | 🐍 Stream-variant resolution. → `04` |
| `ingestion/handbook_diff.py` | 🐍 Change-set computation. → `04` |
| `models/*.py` | 🐍 SQLAlchemy ORM models (one module per cluster). → `03` |
| `schemas/*.py` | 🐍 Pydantic request/response contracts, one module per domain (eligibility, recommendation, reference, admin_*). |

---

## `web/` — the Next.js frontend → `10`, `11`

| Path | Responsibility |
| --- | --- |
| `src/app/page.tsx` | ⚛️ The student home / guidance flow entry. |
| `src/app/admin/(panel)/*` | ⚛️ Admin pages (dashboard, ingestions, cutoffs, courses, conversations, agent, factsheets, knowledge, aliases, requirements, admins). → `10` |
| `src/app/admin/login/page.tsx` | ⚛️ Admin login. |
| `src/app/api/public/[...path]/route.ts` | ⚛️ Open BFF proxy → `/api/v1/*`. → `11` |
| `src/app/api/bff/[...path]/route.ts` | ⚛️ Authenticated BFF proxy (token injection). → `13` |
| `src/app/api/auth/[...nextauth]/route.ts` | ⚛️ NextAuth handler. |
| `src/app/api/upload-info/route.ts` | ⚛️ API base URL for direct upload. |
| `src/app/api/student/*` | ⚛️ Signed-in student conversation history proxy. |
| `src/components/student/guidance-flow.tsx` | ⚛️ The 5-step flow. → `11` |
| `src/components/student/results-view.tsx` | ⚛️ The three-tab results view. → `11` |
| `src/components/student/chat-panel.tsx` | ⚛️ The AI advisor UI. → `08`, `11` |
| `src/components/admin/*` | ⚛️ sidebar, usage-cards, column-mapping-review, change-set-review. → `10` |
| `src/components/ui/*` | ⚛️ shadcn/Radix primitives (Button, Dialog, Select, Table…). |
| `src/lib/guidance-types.ts` | ⚛️ Types mirroring the backend schemas. → `11` |
| `src/lib/utils.ts` | ⚛️ `cn()` class helper. |
| `src/auth.ts`, `src/auth.config.ts` | ⚛️ NextAuth config. → `13` |
| `package.json`, `next.config.*`, `tailwind.config.*` | ⚛️ Frontend config. → `02` |

---

## `alembic/`, `content/`, `data/`, `scripts/`, `docs/`

| Path | Responsibility |
| --- | --- |
| `alembic/versions/*.py` | 🗄️ 43 additive migrations (schema history). → `03` |
| `alembic/env.py` | 🗄️ Migration environment. |
| `content/factsheets/*.md` | 📄 129 per-course factsheets (RAG seed). → `07` |
| `data/raw_handbooks/*.pdf` | 📄 The UGC handbooks (incl. `handbook_2025.pdf` normalised). → `04` |
| `data/cutoffs_extracted/`, `data/seeds/`, `data/test/` | 📄 Extracted CSVs, seed CSVs, test fixtures. |
| `scripts/native_pdf_extractor/extract_cutoffs.py` | 🐍 The low-level cutoff-page/rotated-char primitives the grid extractor builds on. → `04` |
| `scripts/apply_prod_migrations.py` | 🐍 The production migration runner. → `12` |
| `scripts/prod_sql/*.sql` | 🗄️ Hand-reviewed, version-guarded prod migration SQL. → `12` |
| `docs/architecture/*.md` | 📄 This documentation set. |
| `docs/PHASE2_STUDENT_ADMIN_PLAN.md` | 📄 The master plan (phases + decisions). |
| `docs/W2_PROD_PARITY_RUNBOOK.md` | 📄 The production bring-up runbook. → `12` |

---

## Related docs

Every "→ NN" above points to the deep-dive. Start at `01-system-overview.md` for
the map, and `16-design-decisions.md` for why it's shaped this way.
