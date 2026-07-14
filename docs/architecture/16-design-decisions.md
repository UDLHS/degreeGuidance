# Design Decisions & War Stories

## What this is / why it exists

Every other doc in this folder explains *how* a subsystem works. This one
explains *why it is shaped that way* — the deliberate principles, the hard
tradeoffs, and the real production incidents that forced specific designs.
When you (or a future maintainer) look at a piece of code and think "why on
earth is it done like this?", the answer is almost always here.

A cold reader of the codebase cannot reconstruct this — it is the memory of
decisions and the scars of bugs that were fixed *generally* rather than
patched for one case. Read it after the subsystem docs; it ties them
together.

---

## Part 1 — The five principles that recur everywhere

### 1. Deterministic on the critical path — the LLM never decides eligibility

Whether a student *can get into* a course is decided by SQL, not by an AI
model (see `05-eligibility-engine.md`). The reasoning is blunt: if the system
tells a real student they qualify for a course and they do not, they may fill
in the wrong university application form — a life-consequential error. A large
language model that can hallucinate has no place on that path. The AI advisor
sits *beside* the deterministic result and explains it; it never produces it.

### 2. Year-agnostic / data-derived — nothing hardcoded per year

The platform is built to run a new UGC handbook every year forever. So no code
says "2023" or "261 courses" as a constant that a new upload would falsify.
The eligibility query reads `MAX(year)` from the data; the admin dashboards
count from live tables; the AI agent's prompt has `{available_years}`,
`{latest_year}`, `{course_count}`, `{today}` injected at request time
(`core/chat/agent_config.py`). This principle was enforced retroactively —
the original agent prompt *did* hardcode "2019–2023" and "261 courses" and was
already stale before it was fixed.

### 3. Additive-only migrations

The database schema only ever grows; migrations add tables/columns, never
destructively rewrite. This makes every deploy reversible and every prod
migration low-risk. There are 43 Alembic migrations, applied in a strict
chain. In production they are applied by hand-reviewed, version-guarded SQL
scripts rather than `alembic upgrade` directly (see Part 2, "Prod migrations").

### 4. Verification-first — prove it, don't assume it

Nothing consequential is trusted on faith. After the three handbooks were
promoted, every promoted cutoff was cross-checked against the printed PDF
using a *different* PDF engine (poppler) than the ingestion pipeline
(pdfplumber) — an independent second opinion — plus rendered-page spot reads
by eye. The eligibility engine is guarded by a test ORACLE that recomputes
every case with an independent query and demands course-for-course equality
(see `14-testing-quality.md`). The rule, stated by the project owner: *"DON'T
ASSUME ANYTHING."*

### 5. Fix generally, never per-case

When a bug is found, the fix addresses the whole class of problem, not the one
instance. A book that was too slow to parse was not special-cased — the file
format was normalised (Part 2). A crash from one stale browser save became a
versioned-payload gate that kills the entire class of stale-shape crashes.
This keeps the system honest for "future uploads of the handbooks."

---

## Part 2 — War stories: real production incidents and their fixes

These happened while taking the platform from a local prototype to a
three-year production system. Each is: **symptom → root cause → fix → lesson.**

### 2.1 The OOM crash-loop — a 200-page book vs a 512 MB worker

- **Symptom.** The 2024 handbook (5.9 MB) uploaded fine but the extraction job
  crash-looped on the Render worker: pick up job → container restarts ~20 s
  later → arq redelivers → repeat, forever.
- **Root cause (measured, not guessed).** The three whole-book sweeps (grid
  page-detect, whole-book text, Uni-Code section detect) each opened the PDF
  once and touched all ~200 pages. pdfminer (under pdfplumber) accumulates
  per-page memory that `page.flush_cache()` does not release and glibc
  `malloc_trim` cannot reclaim while the handle is open. Peak RSS reached
  **1.25 GB** — far past the free-tier worker's 512 MB, so the OS killed it.
- **Fix.** `core/ingestion/pdf_pages.py::iter_pages_chunked` reads the book in
  40-page chunks, **closing and reopening** the handle between chunks — the one
  thing that reliably releases the accumulation. Peak dropped **1254 MB →
  307 MB**, byte-identical output (262 columns, 913,159 chars, 261 code rows).
- **Lesson.** The problem was an interaction between the file and the runtime,
  not the algorithm. Diagnose with real measurement (`ru_maxrss` + a
  `/proc/self/statm` sampler thread), then fix at the resource boundary. See
  `04-ingestion-pipeline.md`.

### 2.2 The 300-second timeout — a 15 MB book vs arq's default

- **Symptom.** The 2025 handbook (15 MB) extraction failed after exactly
  300.00 s with `TimeoutError` — no crash, no restart (so the memory fix held).
- **Root cause.** arq's default `job_timeout` is 300 s. The 2024 book took
  221 s on the free-tier CPU; a bigger book simply cannot finish inside 300 s.
- **Fix.** `WorkerSettings.job_timeout = settings.worker_job_timeout_seconds`
  (default **3600 s**). Plus a crucial correctness fix: `asyncio.CancelledError`
  is a `BaseException`, so the normal `except Exception` handler never saw a
  timeout and the run stayed orphaned at `running` forever. `extract_pdf_job`
  now catches `CancelledError`, marks the run `failed` on a *fresh* DB session
  inside `asyncio.shield`, and re-raises. No more orphaned runs.
- **Lesson.** Defaults are opinions; size them for the real workload. And a
  cancellation path is a first-class code path, not an afterthought.

### 2.3 The pathological PDF — 43 seconds *per open*

- **Symptom.** Even with the memory fix, the original 2025 file took **1,108 s
  locally / >3,600 s on the throttled prod CPU** — vs 65 s for the 2024 book.
- **Root cause (cProfile-proven).** The file packed its object catalog into
  giant compressed *object streams*; pdfminer re-parses them on **every**
  `pdfplumber.open()` — a ~43 s toll per open (177 M parser calls). Chunked
  reading pays that toll ~19× across the three sweeps. Not the content, not the
  page count (210 vs 208).
- **Fix (the project owner's call: fix the file, not the flow).** Losslessly
  rewrite the PDF with `pikepdf`, object streams disabled:
  ```python
  with pikepdf.open(src) as pdf:
      pdf.save(dst, object_stream_mode=pikepdf.ObjectStreamMode.disable,
               compress_streams=True)
  ```
  0.9 s to rewrite; toll **42.3 s → 0.5 s**; full stage **1,108 s → 79.7 s** at
  330 MB peak. Proven identical: 9,975/9,975 grid cells, 399/399 labels,
  255/255 code rows, matching page-text hashes.
- **Lesson (counter-intuitive).** File size was never the problem — *packing*
  was. The normalised file is 22 MB (bigger) yet 14× faster, because bytes on
  disk and parse cost are unrelated. Battle-tested pipeline code is not bent to
  accommodate one bad encoder; the file is fixed.

### 2.4 The duplicate-year incident — same book under two labels

- **Symptom.** After promoting the "2024" handbook, students saw "2024
  (latest)" with numbers identical to 2023, and the change-review showed only
  2 changed courses — "impossible" for a new book.
- **Root cause.** Prod's original seed (labelled year 2023) came from
  `handbook_2024.pdf`. The 2024 file was then uploaded *again* as year "2024" —
  so the same book existed under two year labels. The change-review truthfully
  found only the 2 cells where the new pipeline read better than the old
  ingest (104A blank↔value, 107L stream split). Verified: 6,500/6,525 cells
  identical. **Not an extraction bug — a labelling bug.**
- **Fix + the convention it forced.** Year = the **A/L examination year** the
  book states in its own header ("Based on the results of the G.C.E. (A/L)
  Examination YYYY"). `handbook_YYYY.pdf` carries exam **YYYY−1** cutoffs. Prod
  was relabelled (old 2023 retired, the higher-quality dataset re-yeared
  2024→2023), local relabelled 2023→2022 and 2024→2023, and the coverage-gap
  test pins re-keyed.
- **Lesson.** When a "new" book shows near-zero changes, suspect a year-label
  duplicate before suspecting extraction. Always upload under the **exam year**
  (file year − 1). See `03-data-model.md`.

### 2.5 The ghost-year crash — a remembered year that vanished

- **Symptom.** After a clean-room reset, a student's browser (which had saved
  "2024" from earlier testing) requested year 2024, the engine found zero rows,
  and served "0 programmes, verified 2024 cutoffs" — an empty platform sitting
  one label away from freshly-promoted data.
- **Root cause.** The engine honoured any requested `exam_year` literally, even
  one with no data. The frontend kept re-sending a stale saved year.
- **Fix (both layers).** The engine now honours a *named* year only if it has
  promoted rows; otherwise it falls back to the freshest year with an honest
  message ("Cutoffs for 2024 aren't published; showing 2022 instead"). The
  frontend validates any restored `examYear` against `/years` and drops it if
  the server no longer offers it, re-running automatically.
- **Lesson.** Client-remembered state must be validated against server truth —
  a real student could hit this the day an admin relabels a dataset. See
  `05-eligibility-engine.md` and `11-student-frontend.md`.

### 2.6 The 405 — the BFF proxy that forgot a verb

- **Symptom.** Saving a factsheet in prod returned HTTP 405 (Method Not
  Allowed).
- **Root cause.** The Next.js BFF proxy (`/api/bff/[...path]/route.ts`)
  exported `GET/POST/PATCH/DELETE` but not `PUT` — and factsheet save is the
  app's only `PUT`.
- **Fix.** One line: `export const PUT = proxy`.
- **Lesson.** A generic proxy must forward every verb it fronts, or an endpoint
  silently disappears. See `13-auth-security.md`.

### 2.7 The Vercel body cap — a 4.5 MB wall vs 6–22 MB books

- **Symptom.** Uploading a handbook through the admin UI returned HTTP 413
  (Content Too Large).
- **Root cause.** The file went through the Vercel BFF, and Vercel hard-caps
  serverless request bodies at 4.5 MB. Handbooks are 6–22 MB, so the proxy
  path can never carry them (proven by probe: a 6 MB body 413'd before our own
  auth ran; a 1 KB body reached our 401).
- **Fix.** The BFF mints a short-lived (10-minute) upload ticket; the browser
  then uploads the file **straight to the Render API** with that token, and the
  API allows it via origin-scoped CORS. Long-lived credentials never reach the
  browser. See `13-auth-security.md`.
- **Lesson.** Know your platform's limits; route around them without weakening
  the auth model.

### 2.8 The split-instance handoff — two machines, separate disks

- **Symptom (structural, caught before it bit a user).** The staged pipeline
  passes files between stages (`{run_id}.pdf`, `grid.json`, `presence.json`,
  `csv`, …). In production the API and the arq worker are **separate Render
  services with separate ephemeral disks** — a file one writes, the other can't
  see, and neither survives a deploy.
- **Fix.** The DB **artifact store**: `ingestion_artifacts` table +
  `core/ingestion/artifact_store.py`. Every stage output is written *through* to
  Postgres and rematerialised on whichever instance needs it next; the local
  work-dir file is just a cache. Verified by tests that wipe the local disk
  between every stage. It doubles as permanent per-year retention of the raw
  handbook and promoted CSV.
- **Lesson.** On ephemeral, horizontally-split infra, the database is the only
  reliable filesystem. See `04-ingestion-pipeline.md` and
  `12-infrastructure-deployment.md`.

### 2.9 The 140P saga — "removed from the book" ≠ "not a real course"

- **Symptom.** Course 140P (Service Management) kept getting suggested for
  "removal" by the handbook diff, and was once deactivated — making it invisible
  to every student.
- **Root cause.** 140P is a real, offered course that simply has **no printed
  cutoff column** in some books (like 103D/104H/105L). The handbook-sync's
  `course_removed` suggestion means "absent from *this* book", not "not real".
- **Fix + rule.** Reactivate it; a course with no cutoffs shows honestly under
  "also offered — no cutoff". Never apply a `course_removed` suggestion
  casually. Coverage-gap test pins encode the expected no-cutoff courses per
  year so a real drop still fails loudly.
- **Lesson.** Absence of data is not deletion of the entity. See
  `06-scoring-recommendations.md`.

### 2.10 The Supabase IPv6 wall

- **Symptom.** Direct connections to the Supabase DB host failed with "Network
  is unreachable" from the WSL dev box and the worker.
- **Root cause.** Supabase's direct host resolves **IPv6-only**; WSL (and the
  environment) had no IPv6 route.
- **Fix.** Use Supabase's **Session Pooler** endpoint (`port 5432`, username
  `postgres.<ref>`), which is IPv4-reachable. Diagnosed with `getent ahosts`
  before changing anything.
- **Lesson.** "Unreachable" is sometimes a routing/address-family problem, not
  a credentials one — check DNS/records first. See
  `12-infrastructure-deployment.md`.

---

## Part 3 — Deliberate technology non-choices

The stack is as notable for what it *avoids* as for what it uses. Full
reasoning is in `02-tech-stack.md`; the short version:

| Avoided | Chosen instead | Why |
| --- | --- | --- |
| LangChain / LlamaIndex | Hand-written Gemini function-calling loop + hand-written RAG | Full control, no framework churn, no hidden prompts; the loop is ~90 lines and fully auditable. |
| Pinecone / Weaviate (vector DB) | `pgvector` inside Postgres | One database, one backup, one connection pool, one failure mode; the corpus fits easily. |
| Celery | `arq` (async-native on Redis) | Lightweight, asyncio-native, no separate result backend ceremony. |
| OpenAI / Anthropic (in prod) | Google Gemini (free/cheap tier) | Zero/low cost per student; embeddings free; bounded by a daily budget guard. |
| Google Custom Search API | `ddgs` (DuckDuckGo) | Free, no API key, callable from an async executor; results trust-ranked in code. |
| Multi-agent orchestration | Single agent with 5 tools | One strong generalist beats several thin specialists for focused Q&A; far simpler and cheaper. See `08-ai-agent.md`. |

---

## Part 4 — Data-integrity decisions

- **Stream-split cutoffs.** A few courses (e.g. 107L Food Business Management)
  print one Uni-Code but have genuinely different cutoffs per A/L stream. These
  go to `course_stream_cutoff_overrides`, and the eligibility query resolves
  them with `COALESCE(override.z_score, base.z_score)` keyed on the student's
  own stream — so every ordinary course is unaffected.
- **Codeless columns.** Some columns carry real z-scores but no Uni-Code in the
  book; they are preserved verbatim in `unmapped_cutoffs` (keyed by printed
  label) and shown as "also offered", never silently dropped.
- **Alias learning.** At mapping-confirm time, the printed label → confirmed
  code mapping is stored in `course_aliases`, so next year's book resolves that
  column automatically. The three-book run grew the alias table to 648 rows.
- **Coverage-gap safeguard.** `cutoff_coverage_gaps(db, year)` lists active
  courses with no cutoff for a year and is pinned per year in tests — the
  tripwire that caught the historical 007K→006K misread and would catch any
  future silent drop.

---

## Related docs

- `01-system-overview.md` — the whole machine and the yearly loop.
- `04-ingestion-pipeline.md` — where most war stories live.
- `05-eligibility-engine.md` — the deterministic core.
- `12-infrastructure-deployment.md` — the split-service topology behind several incidents.
