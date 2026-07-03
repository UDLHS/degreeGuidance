# Admin Handbook Pipeline — Design (v1)

Status: **draft for review** · Author: Udula Harith · Scope: admin panel only

---

## 0. Context

A new UGC handbook is published **~once a year**. An admin must update the
platform's data from it — cutoffs, courses, requirements — and feed the chat
knowledge base. The handbook's layout **changes between years** (2024 identified
courses by Uni-Code `001A`; 2025 dropped the codes and uses *course name +
university name* instead). The data is **high-stakes** — students choose degrees
based on cutoff z-scores.

Two facts drive every decision in this design:

1. **It runs once a year, with a human present.** → optimise for **correctness,
   simplicity, and human control**, not autonomy. A complex autonomous system
   that sits idle 11 months and must be trusted blind on the 12th is the wrong
   tool.
2. **The numbers are life-decisions.** → a z-score is **never** produced by an
   LLM. Hard data is deterministic + human-verified.

### Goals
- Ingest a new handbook → surface exactly what changed → apply with human sign-off.
- Feed two consumers: the **recommendation engine** (hard data) and the
  **chat/RAG agent** (soft data).
- Be robust to layout changes *without* a human having to re-code the parser.

### Non-goals (explicit scope guards)
- ❌ **Not** changing the student side. The RAG-powered chat agent
  (`core/chat/*`, `core/rag/*`) is working and stays untouched; this pipeline
  only *writes to* its knowledge base (`document_sources`/`chunks`).
- ❌ **Not** a swarm of autonomous agents. One assistive AI step (enrichment).
- ❌ **Not** LLM-generated cutoffs, codes, or requirements.

---

## 1. Core principles

| Principle | Meaning |
|---|---|
| **Hard vs soft split** | Hard data (cutoffs, codes, requirements) = deterministic + human-verified. Soft data (descriptions, careers, context) = AI + web → RAG. |
| **Human gate every stage** | Nothing reaches students unreviewed. |
| **Match the machine to the cadence** | Once-a-year → a good review UI beats an autonomous agent. |
| **AI assists, never decides** | On hard data the AI may *suggest* (e.g. column→course guesses); the admin confirms. |
| **Additive & reversible** | New migrations only add; removed courses go `is_active=false` (retained), never deleted; cutoffs are year-versioned. |

---

## 2. Architecture overview

```
          upload handbook.pdf + exam_year
                      │
        ┌─────────────▼──────────────┐
        │  STAGE 1 · READ            │  deterministic grid + whole-PDF scan
        │  page-range (auto|manual)  │
        └─────────────┬──────────────┘
                🧑 gate 1: confirm pages + raw grid
        ┌─────────────▼──────────────┐
        │  STAGE 2 · MATCH & DIFF    │  columns→courses, added/removed/changed
        └─────────────┬──────────────┘
                🧑 gate 2: review change-set
        ┌─────────────▼──────────────┐
        │  STAGE 3 · ENRICH          │  AI + web → soft data (new/changed only)
        └─────────────┬──────────────┘
                🧑 gate 3: review enrichment
        ┌─────────────▼──────────────┐
        │  STAGE 4 · COMMIT & INDEX  │  hard→DB (versioned) · soft→RAG chunks
        └────────────────────────────┘
```

Runs on the existing async ingestion rig: upload endpoint
(`apps/api/routers/admin_ingestions.py`) → Arq worker
(`apps/worker/jobs/extract_pdf.py`) → Postgres/Supabase.

---

## 3. Stage details

### Stage 1 · READ

**Purpose:** get the raw cutoff grid + a whole-book understanding — no decisions yet.

**Pass A — targeted cutoff extraction (deterministic, precise):**
1. Auto-detect cutoff pages (existing `is_cutoff_page` in `extract_cutoffs.py`).
2. **Confidence check:**
   - Confident (labels found, cells > 0) → show detected range to confirm.
   - Low-confidence (e.g. 2025: pages found, 0 columns parsed) → **show a
     manual page-range input** (`cutoff pages: [start]–[end]`).
3. Admin can always **override** the range.
4. Extract the raw grid from the chosen pages → `districts × columns` of
   z-scores/`NQC`, plus whatever column labels exist (codes *or* names).

**Pass B — whole-PDF scan (LLM, structural):**
- The LLM reads the entire PDF and lists every course it can see (name +
  university, code if present) and flags non-cutoff sections (course
  descriptions, requirement text). This is **detection only** — it feeds Stage 2
  matching and Stage 3 enrichment. It never produces numbers.

**🧑 Gate 1:** admin confirms the page range and eyeballs the raw grid beside the PDF.

**Failure handling:** if Pass A yields 0 cells even with a manual range, the run
is marked `failed` with the reason (as today); Pass B can still succeed
independently.

---

### Stage 2 · MATCH & DIFF

**Purpose:** turn the raw grid + scan into a reviewable change-set — **format-proof**.

**Column → course mapping (the 2025 fix):**
- Each extracted column has a label (2024: `001A`; 2025: `MEDICINE (University
  of Colombo)`).
- Resolve label → `courses.course_code`:
  1. Exact match via `course_aliases` (alias_text → course_code).
  2. Fuzzy/name-similarity **suggestion** for the rest (name + university).
- Present an **editable mapping table beside the PDF**; admin confirms/corrects
  every column. New confirmed aliases are written back to `course_aliases` so
  next year is easier.

**Diff (deterministic):** compare the mapped course set + cutoffs against the DB:
- `course_added` — mapped course with no DB row.
- `course_removed` — active DB course absent from the mapped set **AND** absent
  from Pass B's whole-book scan (the **coverage safeguard** that fixes today's
  false-positive removals).
- `cutoff_changed` — z-score delta vs the latest prior year.
- `requirement_changed` — (later) subject-rule changes.

Records land in `handbook_changes` (migration 35, already built), reusing the
existing statuses `pending|approved|rejected|applied`.

**🧑 Gate 2:** the change-set review UI (`change-set-review.tsx`, already built,
extended for the mapping step).

---

### Stage 3 · ENRICH (soft data only)

**Purpose:** enrich new/changed courses for the chat/RAG — the one place AI earns its keep.

- For each new/changed course, one assistive step gathers **descriptions,
  career outlook, university context** from: (a) the handbook's prose sections
  (Pass B), and (b) optional **web search** by course + university name.
- Produces candidate **chunks** (with a source + heading + content).
- **Never touches cutoffs / codes / requirements.**

**🧑 Gate 3:** admin reviews generated blurbs before they're stored.

---

### Stage 4 · COMMIT & INDEX

**Hard data → DB (via existing apply path, extended):**
- `course_removed` (approved) → `is_active=false` (retained for chat/history).
- `course_added` (approved) → course row created from the confirmed mapping.
- cutoffs → promoted per year via the Step-4 loader (existing `ingest_zscores`),
  year-versioned in `z_score_cutoffs` (old years retained → enables year-over-year
  chat comparison).
- every mutation writes `admin_actions` (existing audit).

**Soft data → RAG:**
- approved chunks → `document_sources` + `chunks` (pgvector 768-dim), embedded
  with the existing Gemini embedding path (`core/rag/*`). `content_hash` dedupes.
- The student chat agent picks these up automatically — no chat code changes.

---

## 4. Data model

**Reuse (no change):** `courses`, `z_score_cutoffs`, `course_requirements`,
`course_aliases`, `ingestion_runs`, `parse_errors`, `handbook_changes`,
`document_sources`, `chunks`, `admin_actions`, `scoring_config`.

**New/changed (all additive migrations):**
- `ingestion_runs`: add `cutoff_page_start`, `cutoff_page_end` (the confirmed
  range) for auditability + re-runs.
- A place to persist the **raw extracted grid + column mapping** for a run so
  Gate 1/2 are re-openable — either a new `extraction_columns` table
  (run_id, column_index, raw_label, mapped_course_code, confidence, confirmed) or
  a JSONB artifact on the run. *(decide in Phase 1)*
- `handbook_changes`: possibly add `requirement_changed` to the type check (later).

---

## 5. Infrastructure (prerequisites for production)

Local dev already runs all of this. Production (`degreeGuidance` Render web
service only) needs:

| Need | Plan |
|---|---|
| **Redis** (job queue) | Upstash free tier → set `REDIS_URL` |
| **Worker** (runs extraction) | Render Background Worker (`arq apps.worker.settings.WorkerSettings`) — ~$7/mo, or a free host |
| **Upload path** (Vercel caps bodies at ~4.5 MB) | Upload PDF straight to **Supabase Storage**, backend reads it from there |
| **Reproducibility** | commit a `render.yaml` blueprint (web + worker) |

---

## 6. Build phases

- **Phase 1 — Robust extraction** *(start here; testable locally today)*
  page-range input (auto + manual + override) · raw-grid extraction ·
  column→course mapping UI · coverage safeguard. **Fixes the trust bug.**
- **Phase 2 — Staged review UI** — the 4 human gates end-to-end.
- **Phase 3 — Enrich + RAG** — the assistive AI/web step → chunks.
- **Phase 4 — Admin ops** — multi-admin management + full DB browser/editor.
- **Phase 0 — Prod infra** — Redis + worker + Supabase-Storage upload +
  `render.yaml` (do when ready to go live; independent of building).

---

## 7. Cost & maintenance

- AI cost only in Stage 3 (enrichment) + Stage 1 Pass B (one structural read) —
  small, and on the Gemini stack already in use. Zero AI on the hard-data path.
- A review UI does not rot between yearly runs; there is no idle autonomous
  system to babysit.

---

## 8. Open decisions
1. **Numbers:** deterministic-only extraction with human column-mapping
   (recommended) vs LLM-assisted column ID. *(Design assumes: deterministic grid
   + human-confirmed mapping, LLM only suggests.)*
2. Persist the grid/mapping as a **table** vs **JSONB artifact** on the run.
3. Worker hosting for prod: **paid Render worker** vs **free alternative**.
