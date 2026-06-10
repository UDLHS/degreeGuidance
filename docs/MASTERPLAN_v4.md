# AI Degree Guidance Platform — Final Masterplan (v4)

**Project:** Student-facing AI guidance platform for Sri Lankan university admissions
**Owner:** Udula (developer) and supervising team
**Deadline:** Supervisor handover in 2 months (8 weeks)
**Document status:** Definitive. Supersedes v1, v2, v3. Built from verified handbook content, schema review, OCR script analysis, admin requirements clarification, and production-readiness confirmation.

---

## 1. What changed since v3

This version adds three pieces of context that emerged after v3:

- **Admin surface is now first-class.** The platform has an administrator — the supervisor or you — who uploads handbooks, manages course data, edits factsheets, monitors conversations, and audits eligibility queries. v3 mentioned admin routes in passing; v4 dedicates §14 to the full admin workflow with a three-slice rollout.
- **Production-readiness is named explicitly (§13).** The architecture has always been built for ten-year operation, but v3 left this implicit. v4 documents which choices encode updatability so anyone reviewing the plan can verify the foundation isn't a throwaway.
- **Schema gets two more additions** to support admin work: `users.role` for access control, `admin_actions` for audit trail. Plus Step 4 becomes callable from a background job, not only the CLI.

Everything else — modular monolith, Postgres + pgvector + Redis, FastAPI + Arq, four-tool chatbot, deterministic eligibility, three-category table population, the year-as-A/L-exam-year convention — stands.

---

## 2. What this system is (locked-in scope)

A **student decision aid** for Sri Lankan A/L students choosing university courses. It does not replace UGC. It does not apply on a student's behalf. It does not predict the future. It does three things:

1. **Eligibility check** — given Z-score, district, and stream, return courses where the student would have qualified based on the most recent published cutoffs. Pure rule-based SQL. No LLM.
2. **Personalized ranking** — score eligible courses against the student's interests, career goals, and preferences using a transparent weighted function. Five dimensions, configurable weights. LLM generates short explanations only.
3. **Conversational follow-up** — answer detailed questions about courses, careers, and universities using grounded retrieval over curated knowledge. Four tools. Citations on every claim. Refuses gracefully when out-of-scope.

User experience has two parts plus an admin surface:

- **Part 1 (the form):** student fills inputs → sees ranked eligible courses with score breakdowns.
- **Part 2 (the chat):** student asks deeper questions → gets cited answers backed by structured data and curated factsheets.
- **Admin (the management UI):** an authorized user uploads handbooks, edits course data, manages factsheets, audits the system, monitors conversations.

---

## 3. Ground truth from the handbooks

Every design decision below traces back to facts verified from both handbooks. Anyone reviewing this plan can check the originals.

**The two handbooks span four years.** `HANDBOOK_ENGLISH.pdf` is the 2020/2021 academic year handbook, publishing cutoffs from the 2019/2020 admission cycle (A/L 2019 exam under "New Syllabus"). `student_handbook_english.pdf` is the 2024/2025 handbook, publishing 2023/2024 cutoffs (A/L 2023 exam).

**Year convention — locked in.** The `year` column on `z_score_cutoffs` is **the academic year of the A/L exam that produced the cutoff**. Cutoffs from the 2024/2025 handbook are stored as `year = 2023`; cutoffs from the 2020/2021 handbook are stored as `year = 2019`. This matches how students think ("I took my A/Ls in 2023"). Documented in code comments, schema comments, and the ingestion CLI argument.

**Scale.** 261 Uni-Codes. ~87,776 applicants in 2023/2024, ~42,280 selected. 25 districts × 261 courses ≈ 6,500 cutoff cells per handbook year. Five years of historical data ≈ 32,500 rows — Postgres handles this comfortably with one well-chosen index.

**Six A/L streams** (not seven). Per Section 2.1 of the 2024/2025 handbook: Arts, Commerce, Biological Science, Physical Science, Engineering Technology, Biosystems Technology. The schema includes ICT as a navigation category mapping to courses accepting ICT/SFT/ET/BST subjects (the actual A/L exam streams).

**25 districts, with 16 marked educationally disadvantaged.** Disadvantaged: Nuwara Eliya, Hambantota, Jaffna, Kilinochchi, Mannar, Mullaitivu, Vavuniya, Trincomalee, Batticaloa, Ampara, Puttalam, Anuradhapura, Polonnaruwa, Badulla, Monaragala, Ratnapura. Non-disadvantaged: Colombo, Gampaha, Kalutara, Kandy, Matale, Galle, Matara, Kurunegala, Kegalle.

**21 universities and HEIs.** From the 2024/2025 abbreviations table: CMB, PDN, SJP, KLN, MRT, UJA, RUH, EUSL, SEUSL, RUSL, SUSL, WUSL, UWU, UVPA, GWUIM, UOV, OUSL, SP, TRINCO, UCSC, SVIAS. UOV is new in 2024 (promoted from a Jaffna campus). The schema's `is_active` flag handles this kind of change.

**Selection basis.** Most courses use district quota (40% all-island merit + 55% district + 5% disadvantaged-district). Arts courses (Section 2.1 items 1–10, minus six aesthetic-arts exceptions: Music, Dance, Drama & Theatre, Visual Arts, Visual & Technological Arts, Art & Design) use 100% all-island merit. Marked with `*` next to the column header in Section 9.

**Aptitude-test courses** marked with `#` in Section 9. Music, Dance, Drama & Theatre, Visual Arts, Visual & Technological Arts, Art & Design, plus Architecture, Landscape Architecture, Design. A sufficient Z-score is necessary but not sufficient — the student must also pass the practical/aptitude test. These return as `conditional`, not `eligible`.

**Negative Z-scores are real.** Page 181 of the 2024/2025 handbook shows arts/practical courses with cutoffs as low as −0.6634. Validator must accept negatives. Observed empirical range: approximately **[-0.7, +2.9]**. Safe validator range: **[-2.0, +3.0]**.

**NQC ("No Qualified Candidates")** appears as a cell value with three possible meanings per the handbook footer. The engine treats NQC as `z_score IS NULL` with a `notes` field flagging the cell. Eligibility queries skip NULL rows.

**Medium of instruction is a real eligibility constraint.** Handbook footer: *"Certain courses of study are not conducted in all 3 languages. Therefore some students may not get selected to such courses of study in some universities, even though they have obtained the minimum Z-score required to get selected."* The `course_mediums` table is essential. Eligibility responses tag each course with available mediums.

**Section 9 cutoff tables span 10 PDF pages** in the 2024/2025 handbook (PDF pages 179–188). The OCR pipeline (your existing Steps 1–3) processes all 10.

**Section 2.2 prerequisite grammar has at least five distinct shapes** (flat list, split grades, head-plus-tail, count-plus-qualifier, alternative combinations). A parser covering all of them is a multi-week effort. **For MVP, §2.2 is deferred.** Stream-level eligibility from `course_stream_eligibility` is sufficient for the eligibility check.

---

## 4. Architecture

### 4.1 Style

**Modular monolith** — one codebase, two app processes (`api`, `worker`), shared domain code in a `core/` package, single Postgres, single Redis. Not microservices. Not Kubernetes.

| Process | Purpose | Stack |
|---|---|---|
| `api` | HTTP API: eligibility, chat, courses, admin | FastAPI + Uvicorn |
| `worker` | Background jobs: OCR ingestion, vector indexing, scheduled crawls, admin-triggered tasks | Arq (Redis-backed) |
| `postgres` | Source of truth: structured data + pgvector chunks | PostgreSQL 16 + pgvector extension |
| `redis` | Cache, sessions, rate limits, Arq broker | Redis 7 |
| `frontend` | Student web UI + admin pages | Next.js 14 (App Router) |

### 4.2 Why two processes for one monolith

OCR is multi-minute and CPU-heavy. It cannot run inside an HTTP request handler. Embedding generation is bursty. Splitting `api` and `worker` into separate processes (same image, different `command:` directives in `docker-compose.yml`) is the minimum operational discipline. Not microservices — they share a database, a deployment unit, and a domain model.

### 4.3 Why not the alternatives

- **No LangChain.** Direct Anthropic SDK calls; clearer, faster, easier to debug.
- **No separate vector database.** pgvector handles your scale. Eliminates a second DB, second backup target, second credentials surface.
- **No Kubernetes.** Single VM with Docker Compose runs MVP and the first six months.
- **No serverless.** Long-running OCR and bursty embedding work fit poorly into cold-start economics.

### 4.4 Deployment topology (MVP)

One Linux VM (Ubuntu 24.04 LTS, 8 vCPU / 16GB RAM / 200GB SSD) running `docker-compose` with `api`, `worker`, `postgres`, `redis`, `nginx` (TLS via Let's Encrypt). Frontend on Vercel free tier with custom domain. Nightly `pg_dump` to S3-compatible storage. UptimeRobot health checks. Sentry for error reporting. Total cost: ~USD 30–60/month.

---

## 5. Database schema (final corrections committed)

The schema in `SCHEMA_v2.md` is largely correct. Below are the **specific corrections and additions**. Everything else in the schema doc stands.

### 5.1 Additions

**1. `course_number VARCHAR(5)` on `courses`.**
The Uni-Code "001A" identifies (Medicine, Colombo). The course-of-study number "001" identifies "Medicine" across all 12 universities offering it. The chatbot's `lookup_course` tool and aggregation queries need this column.

```sql
ALTER TABLE courses ADD COLUMN course_number VARCHAR(5);
UPDATE courses SET course_number = LEFT(course_code, 3);
CREATE INDEX idx_courses_number ON courses(course_number);
```

**2. `prompt_version VARCHAR(20)` on `messages` and `roadmaps`.**
Tags every persisted LLM artifact with the prompt version that produced it. Without it, you cannot debug a regression by re-running the same conversation.

**3. Embedding dimension change.**
Schema specifies `VECTOR(768)`. Change to `VECTOR(1536)` to match `text-embedding-3-large` or `gemini-embedding-001`. Decision: pick one provider, stick with it for the year, record `embedding_model` on every chunk.

**4. `eligibility_audit` table.**
Every eligibility query gets logged for forensic investigation.

```sql
CREATE TABLE eligibility_audit (
  audit_id          BIGSERIAL PRIMARY KEY,
  request_hash      VARCHAR(64) NOT NULL,
  user_id           UUID REFERENCES users(user_id) ON DELETE SET NULL,
  z_score           NUMERIC(6,4) NOT NULL,
  district_id       INT NOT NULL REFERENCES districts(district_id),
  stream_id         INT NOT NULL REFERENCES streams(stream_id),
  cutoff_year_used  INT NOT NULL,
  eligible_count    INT NOT NULL,
  conditional_count INT NOT NULL,
  confidence_tier   VARCHAR(20) NOT NULL,
  result_payload    JSONB NOT NULL,
  latency_ms        INT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_eligibility_audit_user ON eligibility_audit(user_id, created_at DESC);
CREATE INDEX idx_eligibility_audit_hash ON eligibility_audit(request_hash);
```

**5. `users.role` column.** Required for admin access control. Add when creating the `users` table in Week 5:

```sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student'
  CHECK (role IN ('student', 'admin', 'superadmin'));
CREATE INDEX idx_users_role ON users(role) WHERE role != 'student';
```

**6. `admin_actions` table.** Every administrator change is logged here, append-only.

```sql
CREATE TABLE admin_actions (
  action_id       BIGSERIAL PRIMARY KEY,
  admin_user_id   UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
  action_type     VARCHAR(50) NOT NULL,
    -- 'upload_handbook' | 'edit_cutoff' | 'verify_alias' | 'edit_course'
    -- 'create_factsheet' | 'edit_factsheet' | 'promote_admin' | etc.
  target_table    VARCHAR(50),
  target_id       VARCHAR(100),
  before_value    JSONB,
  after_value     JSONB,
  notes           TEXT,
  ip_hash         VARCHAR(64),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_admin_actions_admin ON admin_actions(admin_user_id, created_at DESC);
CREATE INDEX idx_admin_actions_target ON admin_actions(target_table, target_id);
CREATE INDEX idx_admin_actions_type ON admin_actions(action_type, created_at DESC);
```

**7. Optional but recommended: `syllabus_version` tracking.**
The 2019 A/L exam was the first under "New Syllabus." Z-scores across syllabus revisions aren't strictly comparable. Either add a column on `z_score_cutoffs` or maintain a small `exam_years` lookup table. Surface this in trend charts.

### 5.2 Schema annotations (comments in migrations)

```sql
COMMENT ON COLUMN z_score_cutoffs.year IS
  'Academic year of the A/L examination that produced these cutoffs. NOT the handbook publication year. The 2024/2025 handbook contains year=2023 cutoffs (from A/L 2023).';

COMMENT ON COLUMN z_score_cutoffs.z_score IS
  'Z-score range observed in handbook data: approximately [-0.7, +2.9]. Validator range: [-2.0, +3.0]. Aptitude-test arts courses regularly publish negative cutoffs. NULL = NQC (No Qualified Candidates).';

COMMENT ON COLUMN courses.selection_basis IS
  'Set via manual seed from handbook Section 1.1 and Section 9 markers. Not derived from cutoff CSV data — OCR does not capture the * marker.';

COMMENT ON COLUMN courses.requires_aptitude_test IS
  'Set via manual seed from handbook Section 9 # markers. Not derived from cutoff CSV data.';
```

### 5.3 What stays from the existing schema

- `course_code` as the natural primary key on `courses`.
- The `UNIQUE (year, course_code, district_id)` on `z_score_cutoffs`.
- `idx_zscore_district_lookup` partial index — correct hot-path optimization.
- `selection_basis`, `requires_aptitude_test`, `is_disadvantaged` modeling.
- `tool_calls` audit table.
- `course_aliases` — the bridge between OCR labels and course_codes.
- `ingestion_runs` and `parse_errors` — the provenance layer.
- pgvector with HNSW index.
- Phase mapping for build order.

---

## 6. The three categories of table population

### Category 1: Hand-seeded reference data

Static. Change only when UGC publishes structural changes. Populated **inside Alembic migration files**.

| Table | Rows | Source |
|---|---|---|
| `districts` | 25 | Section 1.1 of any handbook + administrative geography |
| `streams` | 6 (+1 navigation: ICT) | Section 2.1 of handbook |
| `subjects` | ~25 | A/L subject list |
| `stream_subjects` | ~60 | Which subjects belong to which stream |
| `mediums` | 3 | Sinhala, Tamil, English |
| `universities` | 21 | Handbook abbreviations (page 4 of 2024/2025) |
| `faculties` | optional MVP | Manually from handbook §2.2 narratives |
| `special_provision_categories` | 6 | Handbook Section 6 |

**Total effort: 1 day** for someone reading the handbook carefully.

### Category 2: Hand-curated course metadata

Per-course information not contained in the z-score CSV. Populated by **seed scripts** that read manual annotations.

| Table | Rows | Source |
|---|---|---|
| `courses` | ~261 | Handbook Section 5 (Uni-Code list) + manually annotated `*` and `#` flags |
| `course_stream_eligibility` | ~300–400 | Handbook Section 2.1 |
| `course_mediums` | ~300 | Handbook Section 2.2 narratives |
| `course_aliases` | ~261 | OCR label strings → `course_code` |

**Total effort: 2 days** of focused work with the handbook open.

The most critical of these is `course_aliases`. It is the bridge that makes Step 4 ingestion work. For each `course_code`, you record the exact OCR label your Step 2 pipeline produces.

### Category 3: Auto-populated at runtime/ingestion

These tables grow as the system operates. No human annotation per row.

| Table | Growth pattern | Populated by |
|---|---|---|
| `z_score_cutoffs` | ~6,500 rows per handbook year | Step 4 ingestion script |
| `ingestion_runs` | 1 per ingestion job | Step 4 |
| `parse_errors` | 0 if clean, else count of failures | Step 4 |
| `eligibility_audit` | 1 per eligibility query | Eligibility API endpoint |
| `messages` + `tool_calls` | 1+ per chat turn | Chat orchestrator |
| `admin_actions` | 1 per admin change | Admin endpoints |
| `feedback` | 1 per user submission | Frontend feedback widget |

Step 4's contract: **input a merged z-score CSV + a year argument, output rows in `z_score_cutoffs` joined to existing `courses` via `course_aliases`**. Auto-splits the wide CSV into long-format rows.

What Step 4 does NOT automate:

- **Creating new `courses` rows.** If a CSV contains a course label that doesn't resolve via `course_aliases`, Step 4 logs the unresolved label to `parse_errors` and skips the row. New courses are a human decision (verify in handbook, assign selection_basis and aptitude flag, then re-run).
- **Setting `selection_basis` or `requires_aptitude_test`.** These come from manual annotation in Category 2.
- **Populating reference tables.** Districts must exist before Step 4 can resolve a district name.

Intentional. Auto-creation is silent corruption risk; auto-skip with logging is safe.

---

## 7. OCR pipeline status and the missing Step 4

### 7.1 What you have today

| Script | Function | Status |
|---|---|---|
| `step1_extract_images.py` | HSV color masking, crops green (course names) + pink (z-score grid) regions from each PDF page | Works |
| `step2_course_names_to_csv.py` | EasyOCR on green crops + state-machine pairing of degree+university | Works |
| `step3_zscores_to_csv.py` | EasyOCR on pink crops + spatial grid clustering + horizontal merge across pages | Works (positional merge — see 7.3) |
| `test.py` | Reads one-page merged CSV, writes to wide PostgreSQL table | Prototype only — replace with Step 4 |

The pipeline architecture is sound. Three steps was the right factoring. HSV color separation before OCR is correct because green and pink regions need different rotations. The state-machine pairing in Step 2 handles the handbook's typography correctly. Step 3's grid clustering via row/column centroids is the right technique.

**Output CSVs are 100% human-reviewed before ingestion.** This is a stated workflow guarantee, not an assumption.

### 7.2 Step 4 — the loader

Replaces `test.py`. Takes the human-verified merged CSV and produces normalized database rows. Callable both from CLI (for testing) and as an Arq job (for admin-triggered ingestion).

**Contract:**

- **Input:** Merged CSV (rows = 25 districts, columns = N course labels + leading district column) + `exam_year` (the A/L exam year, e.g., 2023 for 2024/2025 handbook data).
- **Behavior:** For each cell `(district_label, course_label, raw_value)`:
  1. Normalize and resolve `district_label` against `districts.code`. Fail → log to `parse_errors`.
  2. Look up `course_label` in `course_aliases.alias_text` to get `course_code`. Fail → log to `parse_errors`.
  3. Parse `raw_value`: numeric → z_score; "NQC" → NULL with `notes='NQC'`; empty → flag as parse error.
  4. Upsert into `z_score_cutoffs (year, course_code, district_id, z_score, notes)` with `ON CONFLICT (year, course_code, district_id) DO UPDATE`.
- **Output:** `ingestion_runs` row with status, counts. `parse_errors` rows for failures.

**Implementation outline** (lives in `apps/worker/jobs/ingest_zscores.py`):

```python
import argparse
import csv
from datetime import datetime, timezone
from sqlalchemy import select
from core.db import AsyncSessionLocal
from core.models import (
    District, Course, CourseAlias, ZScoreCutoff,
    IngestionRun, ParseError
)

def normalize_district(raw: str) -> str:
    s = raw.strip().upper()
    return s.replace("  ", " ").strip()

def parse_value(raw: str) -> tuple[float | None, str | None]:
    s = str(raw).strip().upper()
    if s == "NQC":
        return None, "NQC"
    if s == "":
        return None, "MISSING"
    try:
        return float(s), None
    except ValueError:
        return None, f"UNPARSEABLE: {raw!r}"

async def ingest_zscores(csv_path: str, exam_year: int, triggered_by: str) -> dict:
    """
    Core ingestion logic. Called from CLI (__main__) AND from Arq jobs.
    Returns a result dict for the admin UI to display.
    """
    async with AsyncSessionLocal() as db:
        # Pre-load reference data
        districts_by_code = {
            d.code: d.district_id
            for d in (await db.scalars(select(District))).all()
        }
        aliases = {
            a.alias_text: a.course_code
            for a in (await db.scalars(select(CourseAlias))).all()
        }

        run = IngestionRun(
            run_type='zscore',
            source_label=f'zscore_csv_year_{exam_year}',
            year=exam_year,
            status='running',
            triggered_by=triggered_by,
        )
        db.add(run)
        await db.flush()

        processed = 0
        failed = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            course_labels = headers[1:]

            for row in reader:
                if not row or not row[0].strip():
                    continue
                district_code = normalize_district(row[0])
                district_id = districts_by_code.get(district_code)
                if district_id is None:
                    db.add(ParseError(
                        run_id=run.run_id,
                        raw_block=row[0],
                        error_type='unknown_district',
                        error_message=f'District {row[0]!r} did not resolve',
                    ))
                    failed += 1
                    continue

                for col_idx, raw_value in enumerate(row[1:]):
                    label = (course_labels[col_idx] or "").strip()
                    if not label:
                        continue
                    course_code = aliases.get(label)
                    if course_code is None:
                        db.add(ParseError(
                            run_id=run.run_id,
                            raw_block=label,
                            error_type='unknown_course_alias',
                            error_message=f'Course label {label!r} not in course_aliases',
                        ))
                        failed += 1
                        continue

                    z_score, note = parse_value(raw_value)
                    existing = (await db.execute(
                        select(ZScoreCutoff).where(
                            ZScoreCutoff.year == exam_year,
                            ZScoreCutoff.course_code == course_code,
                            ZScoreCutoff.district_id == district_id,
                        )
                    )).scalar_one_or_none()

                    if existing:
                        existing.z_score = z_score
                        existing.notes = note
                    else:
                        db.add(ZScoreCutoff(
                            year=exam_year,
                            course_code=course_code,
                            district_id=district_id,
                            z_score=z_score,
                            notes=note,
                        ))
                    processed += 1

        run.status = 'partial' if failed else 'success'
        run.completed_at = datetime.now(timezone.utc)
        run.records_processed = processed
        run.records_failed = failed
        await db.commit()

        return {
            'run_id': str(run.run_id),
            'processed': processed,
            'failed': failed,
            'status': run.status,
        }


# Arq job wrapper — called from admin upload flow
async def ingest_zscores_job(ctx, csv_path: str, exam_year: int, admin_user_id: str):
    return await ingest_zscores(csv_path, exam_year, f'admin:{admin_user_id}')


# CLI entry point — for testing and backfills
if __name__ == '__main__':
    import asyncio
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('--exam-year', type=int, required=True,
                       help='A/L exam year (e.g., 2023 for 2024/2025 handbook data)')
    parser.add_argument('--triggered-by', default='cli')
    args = parser.parse_args()
    result = asyncio.run(ingest_zscores(args.csv, args.exam_year, args.triggered_by))
    print(result)
```

Run from CLI:

```bash
python -m apps.worker.jobs.ingest_zscores \
  --csv data/zscores_2024_handbook_merged.csv \
  --exam-year 2023 \
  --triggered-by 'udula@dev'
```

Or trigger from the admin UI: `POST /api/admin/ingestions` uploads the CSV, enqueues the Arq job, returns the run_id. The admin page polls for completion.

After running, ~6,500 rows in `z_score_cutoffs`, 0 in `parse_errors` if your `course_aliases` is complete.

### 7.3 One Phase-2 fix to Step 3

`step3_zscores_to_csv.py` does horizontal merge by row index position. For human-reviewed CSVs this is fine — you'd catch a row-order mismatch during review. For automated annual re-ingestion (Phase 2), join on the district name instead of positional index. Note in the issues backlog.

### 7.4 The remaining gap: `*` and `#` flags

OCR doesn't capture these. Per the agreed approach, manual annotation. The set is small:

- **All-island merit courses** (Section 2.1 items 1–10, except six aesthetic-arts exceptions): ~10 course numbers, spanning ~40 Uni-Codes.
- **Aptitude-test courses** (handbook Section 9 `#` markers): ~10–15 course numbers, spanning ~20–30 Uni-Codes.

Captured in a seed migration as a static list (see §17 Day 3).

---

## 8. Eligibility engine

### 8.1 The core query (deterministic SQL)

```sql
SELECT
  zc.cutoff_id,
  zc.year,
  zc.z_score AS cutoff_z_score,
  c.course_code,
  c.course_number,
  c.name_en AS course_name,
  c.duration_years,
  c.selection_basis,
  c.requires_aptitude_test,
  u.code  AS university_code,
  u.name_en AS university_name,
  u.district_id AS university_district_id,
  ARRAY(
    SELECT m.code FROM course_mediums cm
    JOIN mediums m ON m.medium_id = cm.medium_id
    WHERE cm.course_code = c.course_code
  ) AS available_mediums
FROM z_score_cutoffs zc
JOIN courses      c ON c.course_code   = zc.course_code
JOIN universities u ON u.university_id = c.university_id
WHERE zc.year         = :exam_year
  AND zc.district_id  = :district_id
  AND zc.z_score IS NOT NULL
  AND zc.z_score      <= :student_z_score
  AND c.is_active     = TRUE
  AND EXISTS (
    SELECT 1 FROM course_stream_eligibility cse
    WHERE cse.course_code = c.course_code
      AND cse.stream_id   = :student_stream_id
  )
ORDER BY zc.z_score DESC;
```

The application layer wraps this with three-state classification, confidence tiering, and `eligibility_audit` logging.

### 8.2 Three return states

| State | Condition | UI surfacing |
|---|---|---|
| `eligible` | Z-score ≥ cutoff, no aptitude test | Standard recommendation |
| `conditional` | Z-score ≥ cutoff, BUT `requires_aptitude_test = TRUE` | Flagged: "Also requires aptitude test" |
| `not_eligible` | Z-score < cutoff OR stream mismatch | Not returned by default |

This is why manual `*` and `#` annotation matters. A student qualifying by Z-score for Architecture without knowing about the aptitude test is misled.

### 8.3 Confidence tiers

| Tier | Condition | UI message |
|---|---|---|
| `current` | Cutoff year is the most recent A/L year | (no caveat) |
| `previous_year` | Most recent cutoff is 1 year old | "Based on last year's cutoffs" |
| `estimated` | Most recent cutoff is 2+ years old | "Based on 3-year trend; current cutoff may differ" |

Within ~0.05 of the cutoff in either direction, surface the marginal-case warning regardless of tier.

### 8.4 What the engine does NOT do

- Does not check §2.2 subject prerequisites. (Phase 2.)
- Does not check special-provision cutoffs. (Phase 2.)
- Does not simulate UGC's selection algorithm.
- Does not predict next year's cutoffs.
- Does not consult an LLM. Ever.

---

## 9. Recommendation scoring (Part 1 ranking)

Pure Python, deterministic, transparent. Every score has a visible breakdown. LLM writes only 1–2 sentence explanations on top of pre-computed scores.

### 9.1 Five dimensions

| Dimension | Default weight | Computation |
|---|---|---|
| Interest alignment | 0.30 | Cosine similarity: embedding(student's interests) vs embedding(`courses.description + courses.name_en`) |
| Career alignment | 0.25 | Fraction of student's career tags matching course's career tags (~50-tag taxonomy) |
| Z-score margin | 0.15 | `tanh((student_z − cutoff_z) × 4)` |
| University preference | 0.15 | 1.0 if course's university in preferred list; 0.5 if district matches; 0.2 otherwise |
| Future industry alignment | 0.15 | Fraction of student's industry tags matching course's industry tags |

Weights in a `scoring_config` table or YAML. Tune without redeploys.

### 9.2 Result buckets

- **Safe** — score ≥ 0.6 AND Z-score margin ≥ 0.10.
- **Ambitious** — score ≥ 0.6 BUT Z-score margin < 0.05.
- **Hidden opportunities** — score ≥ 0.5 AND university not in "top 5 by reputation" AND course matches a niche industry tag.

Thresholds are config.

### 9.3 The explanation step

LLM generates explanations for top 10 only. Receives score breakdown + course metadata. Cannot retrieve, speculate, or add facts. System prompt forces 15–30 words, mentions only components contributing ≥ 0.2. Cached: same inputs → same output → no repeat cost.

---

## 10. RAG architecture (Part 2 knowledge base)

### 10.1 What's in the knowledge base

**Tier 1 — must exist before launch:** ~50 curated course factsheets, 600–1000 words each, for top 50 Uni-Codes. Authored, not scraped.

**Tier 2 — must exist before public launch:** ~10 career pathway documents, 800–1200 words each, Sri Lanka-specific.

**Tier 3 — post-launch:** ~21 university-level descriptions.

**Tier 4 — deferred:** University website crawling.

What is NOT in the KB: cutoff data, §2.2 prerequisite text. Those are structured data queried via SQL tools.

### 10.2 Chunking

Semantic-unit chunking. 200–500 tokens. Metadata per chunk: `source_id`, `section`, `course_code`, `course_number`, `university_id`, `content_type`, `language`.

### 10.3 Embeddings and retrieval

`text-embedding-3-large` (OpenAI) or `gemini-embedding-001` (Google), both 1536d.

Pipeline per `search_knowledge` tool call:

1. Pre-filter by metadata (`course_number`, `content_type`, `university_id`).
2. Hybrid retrieval: BM25 + pgvector cosine in parallel, top 20 each.
3. Reciprocal Rank Fusion (`k=60`), top 20 fused.
4. Cross-encoder rerank with `bge-reranker-base`. Top 5 returned.

### 10.4 Citation generation

Every factual claim cites a tool result. Claims without sources are dropped. Single most important hallucination control.

---

## 11. Chatbot design (Part 2 conversation)

### 11.1 Pattern

Single-turn, tool-equipped LLM call. No multi-step planning. No agent recursion.

### 11.2 The four tools

**`check_eligibility(z_score, district, stream)`** — calls the deterministic eligibility engine. Model MUST call this for eligibility questions.

**`lookup_course(identifier)`** — accepts Uni-Code, course number, or fuzzy name. Returns structured `courses` row + last 3 years of cutoffs + aliases.

**`search_knowledge(query, filters)`** — hybrid search over `chunks`. Returns top 5 chunks with source attribution.

**`get_cutoff_trend(course_code_or_number, years=3)`** — time-series cutoff data across districts. Returns nothing if < 2 data points.

Explicitly NOT included: live web fetch, general-knowledge tool, clarification tool.

### 11.3 System prompt structure (versioned via `prompt_version`)

1. **Role** — "Sri Lankan A/L admissions counselor assistant."
2. **Hard rules** — never invent; use `check_eligibility` for eligibility questions; never predict cutoffs.
3. **Citation requirement** — drop claims without sources.
4. **Refusal pattern** — explicit "I don't have reliable info" + suggest direct contact.
5. **Profile context** — student's z-score/district/stream/interests, marked user-stated.
6. **Conversation history** — last 8 turns.

### 11.4 Conversation memory

Last 8 turns in Redis; persisted to `messages` + `tool_calls`. No semantic memory. No cross-conversation knowledge.

### 11.5 Refusal patterns (templated)

| Trigger | Response |
|---|---|
| Out-of-scope | "I can only help with Sri Lankan state universities under the UGC." |
| No tool returned content | "I don't have reliable information on that. The university's website or an admissions officer may help." |
| Eligibility question, no profile | "I'd need your Z-score, district, and stream to check." |
| Future-cutoff prediction | "I cannot predict next year's cutoffs. Based on the last 3 years, the cutoff for [course] has been [trend]." |

---

## 12. Stack and deployment (final)

### 12.1 Backend

| Concern | Choice | Why |
|---|---|---|
| Web framework | FastAPI | Async, Pydantic v2, OpenAPI free |
| ORM | SQLAlchemy 2.0 async | Mature, Alembic integration |
| Migrations | Alembic | Reproducible schema + seed data |
| Background jobs | Arq (Redis-backed) | Simpler than Celery at this scale |
| Auth | Auth.js on Next.js + JWT to API | Email/Google login; anonymous sessions for first-time |
| HTTP client | httpx async | FastAPI ecosystem fit |
| LLM client | Anthropic SDK direct | No LangChain abstractions |
| Embeddings | `text-embedding-3-large` or `gemini-embedding-001` | 1536-dim |
| Reranker | bge-reranker-base | CPU-runnable |
| Cache | Redis | Eligibility 24h, repeat chat queries 1h |
| Observability | OpenTelemetry traces + structured logs | Trace every chat turn |
| Error reporting | Sentry | Standard |
| Package management | uv | Faster than pip/poetry |

### 12.2 Frontend

Next.js 14 (App Router). React Server Components for static. Client Components for interactive. Tailwind + shadcn/ui. Recharts for cutoff trends. Streaming via Server-Sent Events. Mobile-first; sub-3s TTI on mid-range Android over 4G.

### 12.3 Deployment

Single VM (Ubuntu 24.04 LTS, 8 vCPU, 16GB RAM, 200GB SSD). Docker Compose: `postgres`, `redis`, `api`, `worker`, `nginx`. Frontend on Vercel.

GitHub Actions CI: tests + mypy + ruff + alembic check on every push; deploy to staging on main; manual approval gate to production.

Backups: nightly `pg_dump` to Backblaze B2, 90-day retention. Pre-ingestion snapshot retained for academic year. Quarterly restore drill.

Monitoring: `/health`, `/ready` endpoints. UptimeRobot. Worker heartbeat row in `system_status`. Daily LLM cost aggregation with threshold alert.

---

## 13. Production-readiness (explicit)

The architecture is built for ten-year operation. The properties that make it updatable, maintainable, and trustworthy long-term:

**Schema evolution via Alembic.** Every schema change for the lifetime of this system is a migration file. The `alembic_version` table tracks where the database is. Deploys run `alembic upgrade head`. Rollbacks run `alembic downgrade -1`. This is the standard pattern; it scales from your laptop to a cluster.

**Year-versioned via columns, not per-year tables.** `z_score_cutoffs.year` is a column. Adding a new year is inserting rows, not creating tables. In ten years with fifteen years of cutoffs, the same queries work.

**Natural keys where stable.** `course_code` (Uni-Code) is the primary key on `courses` because it's externally meaningful and stable. Joins to external systems are direct, not surrogate-mediated.

**JSONB for variable-shape data.** `course_requirements.required_subjects`, `student_profiles.career_interests`, several `metadata` fields — all JSONB. New fields don't need migrations. Fields that become important get promoted to columns.

**Versioned LLM artifacts.** `prompt_version` and `model_used` on every `messages` and `roadmaps` row. Old artifacts remain reproducible after prompt or model changes.

**Append-only audit trails.** `admin_actions`, `eligibility_audit`, `tool_calls`, `parse_errors`, `ingestion_runs`. Investigations and compliance both have a path.

**Config from environment, not code.** Settings loaded by `pydantic-settings` from `.env`. Moving between local/staging/production changes config only.

**Dependency management via `pyproject.toml` + `uv.lock`.** Reproducible installs. Pinned versions. Security upgrades are a one-line edit and a CI run.

**Soft delete where appropriate.** `is_active` flags on `courses`, `universities`. Historical cutoff data survives discontinued courses. No data loss from a UGC restructure.

**Separation of concerns at the code level.** `core/` holds shared domain logic. `apps/api/` and `apps/worker/` import from it. If the worker eventually needs to split into a separate service, the surgery is local.

**Backups, restore drills, retention policies.** Operationalized in §12.3.

**What you can extend without redesign:**

- Add a new university or course → seed migration row + data load.
- Add a new factsheet → admin UI write (no code change).
- Add a new chat tool → register in `core/chat/tools.py`, mention in system prompt, version bump.
- Add a new scoring dimension → add a column to `scoring_config`, update the scoring function.
- Add a new admin role → add to enum, gate endpoints.
- Multi-language UI → Next.js i18n, plus populating `name_si`/`name_ta` columns that already exist.
- Mobile app → consumes the existing API; no backend change.

**What requires more substantial work but is supported:**

- New Postgres major version (16 → 17) → one major upgrade per year, tested in staging first.
- Switch embedding provider → re-embed all chunks (Arq job, takes hours, no downtime).
- Migrate from pgvector to a dedicated vector DB → if ever needed (you won't for years), schema for `chunks` translates directly.
- Multi-region → add read replicas via SQLAlchemy `bind` mapping.

The masterplan's deferred items (Kubernetes, microservices, multi-region) are deferred because the **current scale doesn't justify them**, not because the foundation can't support them.

---

## 14. Admin surface

The administrator (you, your supervisor, or a delegated operator) needs to manage the platform without writing code. The admin surface is a set of routes under `/admin/*`, protected by role check, sharing the same Next.js + FastAPI codebase as the student-facing site.

### 14.1 What the administrator does

**Data management:**
- Upload a new handbook PDF; trigger OCR pipeline as background job; review merged CSV; commit to database (calls Step 4).
- Browse and correct ingested cutoffs; edit any cell with audit logging.
- Manage `course_aliases`; verify unverified, add new, correct mappings.
- Manage `courses` directly: add a course, edit a name, flip `is_active`, change `selection_basis` or `requires_aptitude_test`.
- Manage `universities` and `faculties`.

**Knowledge base management:**
- Upload, edit, and tag factsheets (markdown editor). On save, re-chunk + re-embed.
- Browse factsheets, mark stale ones for review, bulk re-embed if embedding model changes.

**Monitoring and operations:**
- Ingestion run history with `parse_errors` drill-down.
- Eligibility audit log, searchable.
- Chat conversation viewer with full tool-call trace.
- Feedback list, filterable by reported_issue.
- System health dashboard: query volume, p50/p95 latency, LLM cost, error rate.

**User management:**
- Create, edit, disable admin accounts (superadmin only).
- Manage abuse (view rate-limited users, ban abusive accounts).

### 14.2 Schema additions (already listed in §5)

- `users.role` column (`student | admin | superadmin`).
- `admin_actions` table — append-only audit trail with before/after JSONB.

### 14.3 API surface (admin namespace)

```
GET    /api/admin/dashboard
GET    /api/admin/ingestions
POST   /api/admin/ingestions               -- upload PDF, kick off OCR job
GET    /api/admin/ingestions/{run_id}      -- detail + parse_errors
POST   /api/admin/ingestions/{run_id}/promote -- commit reviewed CSV via Step 4

GET    /api/admin/cutoffs                  -- search/filter z_score_cutoffs
PATCH  /api/admin/cutoffs/{cutoff_id}      -- edit one cell

GET    /api/admin/aliases
POST   /api/admin/aliases
PATCH  /api/admin/aliases/{alias_id}
DELETE /api/admin/aliases/{alias_id}

GET    /api/admin/courses
PATCH  /api/admin/courses/{course_code}
POST   /api/admin/courses

GET    /api/admin/factsheets
POST   /api/admin/factsheets               -- triggers re-chunk + re-embed
PATCH  /api/admin/factsheets/{source_id}
DELETE /api/admin/factsheets/{source_id}

GET    /api/admin/conversations
GET    /api/admin/conversations/{id}

GET    /api/admin/eligibility-audit
GET    /api/admin/feedback

GET    /api/admin/users
PATCH  /api/admin/users/{user_id}          -- change role (superadmin)

GET    /api/admin/actions                  -- audit log (superadmin)
```

Every endpoint checks JWT for `role IN ('admin', 'superadmin')` via FastAPI dependency. Every mutation writes a row to `admin_actions`.

### 14.4 Frontend pages

Under `web/app/admin/`:

- `/admin` — dashboard
- `/admin/ingestions` and `/admin/ingestions/[runId]`
- `/admin/cutoffs` (with edit modal)
- `/admin/aliases`
- `/admin/courses` and `/admin/courses/[courseCode]`
- `/admin/factsheets` and `/admin/factsheets/[sourceId]` (markdown editor)
- `/admin/conversations` and `/admin/conversations/[id]`
- `/admin/eligibility-audit`
- `/admin/feedback`
- `/admin/users`

All behind `/admin/login`, using Auth.js with role check.

### 14.5 Three-slice rollout

**Slice 1 — Week 2 (essential for ingestion):**
- Admin login + role check
- Ingestion upload + run viewer
- Course aliases page
- Course edit page (read + flag updates)

Without these, every handbook ingestion requires terminal access. Unsustainable past Week 4.

**Slice 2 — Weeks 5–6 (essential for content):**
- Factsheet editor (markdown preview, course tagging, save-and-re-embed)
- Conversation viewer for chatbot debugging
- Feedback list

Without these, every factsheet update requires a developer. Doesn't scale past internal testing.

**Slice 3 — Phase 2:**
- Eligibility audit search UI
- Dashboard with charts
- User role management
- Admin action audit viewer
- Cutoff cell-level editing
- Course add/create form

These can be deferred to after supervisor handover. Document in Phase 2 backlog so they don't fall off.

### 14.6 Build philosophy

Don't reach for a generic admin framework (Django Admin, React Admin, Strapi). Each admin page has a specific workflow; bespoke is better than generic. The 12 pages above are concrete and purposeful. Build them one at a time as the corresponding feature lands.

---

## 15. Security and governance

### 15.1 Threat surface

| Risk | Mitigation |
|---|---|
| Student trusts incorrect eligibility verdict | Confidence tiers; disclaimer; "talk to a counselor" escape hatches |
| Crafted Z-score crashes engine | Pydantic validation with explicit range; district/stream as enums; rate limiting |
| Chat used as LLM proxy / prompt injection | Input length cap; domain-bounded system prompt; tool-call pattern monitoring |
| Scraping | Low-priority (data is public); per-IP rate limit |
| PII leakage in logs | Hash IPs; never log raw Z-scores with identifying timestamps; encrypt Postgres data at rest |
| Admin credentials compromised | 2FA; IP allowlist on `/admin/*`; separate DB role with minimum privileges |
| Admin abuses access | `admin_actions` log makes every change attributable |

### 15.2 Audit logging

- Eligibility queries → `eligibility_audit`
- Chat turns → `messages` + `tool_calls`
- Admin actions → `admin_actions` with before/after JSONB
- Logins → `auth_events`

Append-only. Retention: 18 months for queries/turns; permanent for `admin_actions` (one academic-cycle plus 6 months minimum; never deleted in practice).

### 15.3 Data protection

PII handled: name (optional), email (optional), Z-score, district, stream, exam year, free-text interests.

Encryption at rest (cloud feature). TLS in transit (HSTS). SSL on DB connections. Secrets in env vars. "Delete my data" endpoint cascade-deletes profile + conversations + saved courses.

### 15.4 LLM safety

- Output filtering before display.
- Red-team test set of 50 adversarial prompts run on every deploy. Refusal rate tracked.
- Document Anthropic ToS compliance for supervisor handover.

---

## 16. Testing strategy

### 16.1 Eligibility correctness

**Test set: 100 cases** in `tests/fixtures/eligibility_cases.yaml`. Run on every commit; failures block merge.

Must include: exactly-at-cutoff, 0.01 below cutoff, NQC cells, aptitude-test courses returning `conditional`, all-island-merit courses, disadvantaged-district profiles, stream mismatch, missing-year fallback, negative-cutoff arts courses.

### 16.2 RAG retrieval quality

**Test set: 30 queries** with expected top-K chunk IDs. precision@5 weekly. Below 0.7 → investigate.

### 16.3 Chatbot quality (rubric)

**30 conversations per week** scored 0/1 against: cited sources? refused to invent? right tool? factually accurate? well-formed language? Target ≥ 80% at handover.

### 16.4 Admin endpoint tests

Integration tests for the Slice 1 admin endpoints. JWT role check, ingestion roundtrip, alias verification flow. Run on every PR.

### 16.5 Load testing

Not MVP focus. One pass before public launch (Phase 3+).

### 16.6 "Good enough" at handover

- Eligibility: 100% on 100-case set
- RAG: precision@5 ≥ 0.75
- Chatbot rubric: ≥ 80%
- Admin endpoint integration tests: 100%
- No critical bugs in ingestion
- Docs let someone else deploy from scratch

---

## 17. YOUR steps — day by day

### Week 1 — Foundation

The most important week. Subsequent weeks depend on this foundation being solid.

**Day 1 (Monday): Project skeleton + Alembic.**

The full Day 1 walkthrough (which we've already done together):

1. Create `~/projects/degree-guidance`. `git init`. Create folder skeleton: `apps/api/routers`, `apps/worker/jobs`, `apps/worker/ocr`, `core/{models,schemas,scoring,rag,chat,utils}`, `alembic/versions`, `web/`, `tests/{unit,integration,fixtures}`, `ops/`, `docs/runbooks/`, `data/seeds/`, `content/factsheets/`. Add `.gitignore`.
2. Install Python 3.11+, install `uv`.
3. `uv init --python 3.11`. Configure `pyproject.toml` with dependencies: sqlalchemy[asyncio], alembic, asyncpg, psycopg2-binary, pydantic, pydantic-settings, python-dotenv, pgvector. Run `uv sync`. Activate venv.
4. Install PostgreSQL 16 + pgvector extension. Create database `degree_guidance` and role `degree_app`. `CREATE EXTENSION vector;`.
5. Create `.env` with `DATABASE_URL` (asyncpg) and `DATABASE_URL_SYNC` (psycopg2). Commit `.env.example`, not `.env`.
6. Write `core/config.py` (Settings via pydantic-settings) and `core/db.py` (engine + sessionmaker + Base).
7. `alembic init -t async alembic`. Edit `alembic/env.py` to import settings and Base. Configure `target_metadata = Base.metadata`.
8. Verify Python can import `core/`. Run `alembic upgrade head`. See `alembic_version` table created.

By end of day: empty database with Alembic tracking ready.

**Day 2 (Tuesday): Reference data migrations (Category 1).**

Write Alembic migrations 01–08 with full seed data:

- `01_districts` — all 25 districts with `is_disadvantaged` correctly set. The 16 flagged: Nuwara Eliya, Hambantota, Jaffna, Kilinochchi, Mannar, Mullaitivu, Vavuniya, Trincomalee, Batticaloa, Ampara, Puttalam, Anuradhapura, Polonnaruwa, Badulla, Monaragala, Ratnapura.
- `02_streams` — 6 A/L streams + ICT navigation category. Codes: `ARTS`, `COMMERCE`, `BIO_SCIENCE`, `PHYSICAL_SCIENCE`, `ENGINEERING_TECH`, `BIOSYSTEMS_TECH`, `ICT`.
- `03_subjects` — ~25 A/L subjects.
- `04_stream_subjects` — junction.
- `05_mediums` — SI, TA, EN.
- `06_universities` — all 21 with abbreviations + district FKs.
- `07_faculties` — empty initially; populate as factsheets are written.
- `08_special_provision_categories` — 6 categories from §6.

By end of day: `alembic upgrade head` on a fresh DB produces all reference data. Verify with `SELECT * FROM districts;` → 25 rows, 16 flagged.

**Day 3 (Wednesday): The `courses` table seed (Category 2).**

Open the 2024/2025 handbook to Section 5 (page 143 onward). For each Uni-Code, capture:
- `course_code` — e.g., `001A`
- `course_number` — e.g., `001`
- `university_code` — e.g., `CMB`
- `name_en` — e.g., `Medicine (University of Colombo)`

Save as `data/seeds/courses.csv`. ~3 hours of typing.

Migration `09_courses` reads this CSV, inserts rows with defaults (`selection_basis='district_quota'`, `requires_aptitude_test=FALSE`).

Migration `10_course_markers` overrides for the special cases. Lists to populate by reading Section 5 + Section 9:

```python
ALL_ISLAND_MERIT_COURSE_NUMBERS = [
    "019",  # Arts
    "020",  # Arts (SP) - Mass Media
    "041",  # Arts (SP) - Performing Arts
    "021",  # Arts (SAB)
    # Plus: Communication Studies, Peace and Conflict Resolution, Islamic Studies,
    # Arabic Language, TESL, Social Work, Arts - IT
]

APTITUDE_TEST_COURSE_NUMBERS = [
    # Music, Dance, Drama & Theatre, Visual Arts, Visual & Technological Arts,
    # Art & Design, Architecture, Landscape Architecture, Design
]

def upgrade():
    op.execute(f"""
        UPDATE courses SET selection_basis = 'all_island_merit'
        WHERE course_number IN ({','.join(repr(c) for c in ALL_ISLAND_MERIT_COURSE_NUMBERS)})
    """)
    op.execute(f"""
        UPDATE courses SET requires_aptitude_test = TRUE
        WHERE course_number IN ({','.join(repr(c) for c in APTITUDE_TEST_COURSE_NUMBERS)})
    """)
```

By end of day: `SELECT count(*) FROM courses;` → ~261. `SELECT count(*) FROM courses WHERE selection_basis='all_island_merit';` → ~40.

**Day 4 (Thursday): `course_stream_eligibility` and `course_aliases` seeds.**

`course_stream_eligibility` seed CSV mapping course_number → eligible stream codes, derived from Section 2.1. Cross-stream courses (Section 2.2.8) get multiple rows. Focus on top 50 courses for MVP.

`course_aliases` seed CSV. For each row in your courses CSV, write the exact OCR label string your Step 2 produces, paired with course_code:

```
alias_text,course_code,is_verified,confidence
MEDICINE (University of Colombo),001A,TRUE,1.00
MEDICINE (University of Peradeniya),001B,TRUE,1.00
...
```

By end of day: ~261 aliases verified. Cross-check:

```sql
SELECT count(*) FROM course_aliases ca
LEFT JOIN courses c ON c.course_code = ca.course_code
WHERE c.course_code IS NULL;
-- Must return 0
```

**Day 5 (Friday): Step 4 + end-to-end load.**

Implement `apps/worker/jobs/ingest_zscores.py` (§7.2 of this doc). Wire CLI entry point.

Run against existing CSV:

```bash
python -m apps.worker.jobs.ingest_zscores \
  --csv data/zscores_2024_handbook_merged.csv \
  --exam-year 2023 \
  --triggered-by 'udula@dev'
```

Expected: ~6,500 rows in `z_score_cutoffs`, 0 in `parse_errors`, 1 row in `ingestion_runs` with `status='success'`.

If `parse_errors` rows appear: add missing aliases or fix district normalization. Iterate.

Start factsheet writing tonight. First factsheet: Medicine at Colombo. 600–1000 words covering curriculum, careers, faculty info, mediums. Save to `content/factsheets/001A.md`.

**End of Week 1:**
- Schema recreatable with one command.
- ~261 courses, 21 universities, 25 districts, 6+ICT streams, 6 special-provision categories populated.
- ~261 course aliases verified.
- ~6,500 cutoff rows for `year=2023` loaded.
- Manual eligibility query works in psql.
- One factsheet drafted.

### Week 2 — Eligibility engine + admin Slice 1

**Engineering work:**
- Implement eligibility query as SQLAlchemy 2.0 async function in `core/eligibility/`.
- FastAPI endpoint `POST /api/v1/eligibility` with Pydantic validation.
- Three-state classification logic.
- Confidence tier detection.
- 100-case test set in `tests/fixtures/eligibility_cases.yaml`.
- Hook up `eligibility_audit` logging.

**Admin Slice 1 work:**
- `users` table migration with `role` column.
- Admin login via Auth.js + JWT role claim.
- Role-check FastAPI dependency.
- `/admin/ingestions` page: upload PDF, kick off Arq job, show progress.
- `/admin/aliases` page: list, verify, edit.
- `/admin/courses` page: list, edit names + flags.
- `admin_actions` logging on every admin mutation.

**Continue factsheets:** target 20 done by end of week.

### Week 3 — Scoring + Part 1 UI

- 5-dimension scorer in `core/scoring/engine.py`.
- LLM explanation generation (Anthropic SDK, claude-sonnet-4-5).
- Bucket grouping.
- Next.js form UI: progressive-disclosure inputs.
- Results page: ranked list + score breakdowns + save buttons.
- Connect Part 1 end-to-end.

**Continue factsheets:** target 30 done.

### Week 4 — RAG

- Migrations for `document_sources`, `chunks` with `VECTOR(1536)`.
- Chunking script (semantic units).
- Hybrid retrieval: BM25 + pgvector + RRF + cross-encoder rerank.
- Index 30 completed factsheets.
- Test on 30-query set; tune if precision@5 < 0.7.

**Decide:** auth (email/Google vs anonymous-only); university-level factsheets; special-provision cutoffs.

**Finish factsheets:** target 50 done. Start career pathway docs.

### Week 5 — Chatbot + admin Slice 2

**Engineering work:**
- Migrations for `users`, `student_profiles`, `conversations`, `messages`, `tool_calls`.
- The 4 tools as Python functions via Anthropic tool-use spec.
- Chat orchestration: prompt assembly, tool execution, structured response, citation rendering.
- Chat UI: streaming, message list, citations, sources panel.

**Admin Slice 2 work:**
- `/admin/factsheets` editor: markdown preview, course tagging, save-and-re-embed.
- `/admin/conversations` viewer for debugging.
- `/admin/feedback` list.

**Test 20 archetypal questions.**

### Week 6 — Polish + internal testing

- Eval harness: auto-run eligibility cases on every PR; weekly chat rubric review.
- Telemetry: OpenTelemetry traces, logs to aggregator, Sentry.
- Fix bugs from internal testing.
- Deployment runbook and admin runbooks.

### Week 7 — Closed beta

- 20–30 real students from different districts/streams.
- Watch logs. Daily self-standup: what looks wrong? Fix it.

### Week 8 — Demo + handover

- Demo script: form flow → score breakdown → 5 chat questions → admin alias review → admin ingestion upload.
- Supervisor handover doc: this masterplan + schema diagram + API spec + prompt log + eval results.
- Production deploy or staging-ready-to-flip.

---

## 18. Decision register

### Final IN scope for MVP

| Decision | Rationale |
|---|---|
| Modular monolith (api + worker) | Smallest viable operational surface |
| Postgres + pgvector + Redis | Single source of truth, no second DB |
| Three-category table population | Reference seeded once, metadata seeded once, cutoffs auto-ingested |
| Manual annotation of `*`/`#` markers | OCR doesn't capture them; ~20–25 entries |
| Step 4 ingestion (CLI + Arq job) | Replaces test.py; idempotent upsert |
| Eligibility via deterministic SQL only | Auditability and student safety |
| Three-state eligibility | Aptitude tests change the verdict |
| Confidence tiers | Honest about data freshness |
| 5-dimension weighted scoring | Transparent and tunable |
| 4-tool chatbot, no planning, no web fetch | Bounded surface, auditable |
| pgvector + BM25 + cross-encoder rerank | Right pattern for proper-noun-heavy corpus |
| Curated factsheets (Tier 1 + 2) | Defers scraped-content quality issues |
| Anthropic SDK direct, no LangChain | Less abstraction, fewer surprises |
| Docker Compose single VM + Vercel | Trivial ops |
| English-only UI | Multi-language is its own project |
| 1536-dim embeddings | Match text-embedding-3-large / gemini-embedding-001 |
| Admin Slice 1 in Week 2 | Required to ingest handbooks without terminal access |
| Admin Slice 2 in Weeks 5–6 | Required for content workflow |
| `admin_actions` audit table | Attributable changes; trust foundation |

### Deferred (with reason)

| Item | Why deferred | When |
|---|---|---|
| §2.2 prerequisite parser | Five grammar shapes; multi-week effort | Phase 2 |
| §6 special-provision cutoffs | Small fraction of students | Phase 2 |
| Roadmap generation | Highest LLM cost, hallucination risk | Phase 3 |
| University web crawling | Tier 1+2 covers MVP | Phase 4, when chat logs identify gaps |
| Sinhala/Tamil UI | Project-scale work | Phase 3 minimum |
| Mobile app | PWA serves mobile | Year 2 |
| Voice assistant | Adds modality, latency | Year 2+ |
| Admin Slice 3 | Eligibility audit UI, dashboard, role mgmt UI | Phase 2 |
| Analytics dashboards | Postgres has the data | After 3 months production data |
| Multi-region / autoscaling | No scaling problem exists | When evidence demands |
| Fine-tuned models | No training data; off-the-shelf works | Year 2+ if eval gaps demand |
| Conversation branching | Linear suffices | Only on user demand |

### Conditional (decide Week 4)

| Item | Criterion |
|---|---|
| Email/Google auth vs anonymous-only | Add if testers want saved profiles |
| Special-provision cutoffs in MVP | Add if a beta user requests it |
| University-level factsheets | Top 5 if time permits in Week 6 |

---

## 19. Risks and mitigations

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| `course_aliases` incomplete → Step 4 silently skips rows | High | Medium | `parse_errors` logging; ~6,500 expected cells; manual count reconciliation |
| Year-labelling confusion | High | Low (locked by this doc) | A/L exam year convention in schema, code, CLI |
| Chatbot hallucinates a cutoff | High | Low | Tools + citations + prompt rules; rubric tracking |
| Manual `*`/`#` annotation missed a course | Medium | Medium | Cross-check with Section 9; supervisor spot-check |
| Tier 1 content not ready by Week 4 | High | High | Start Day 5; parallel track; accept 30 instead of 50 |
| Admin surface deferred too long → ops bottleneck | High | Medium | Slice 1 in Week 2 is non-negotiable |
| Supervisor demo fails on edge case | Medium | Medium | 100-case test set + pre-tested supervisor profile |
| LLM cost overrun | Medium | Low | Daily cap with alert; explanation cache; no LLM in eligibility |
| §2.2 parser tempts you off-plan | Medium | Medium | Decision register makes deferral explicit |
| Negative Z-score rejected by sloppy validator | Medium | Low | Documented range; test cases include negatives |
| Multi-year trend misleads across syllabus boundary | Medium | Medium (low for MVP) | `syllabus_version` field; UI marker |
| Step 3 positional merge misaligns on future ingestion | Medium | Low (you review) | Phase 2 fix: join on district name |
| Admin abuses access | Medium | Low | `admin_actions` log; superadmin separation |

---

## 20. The three principles to take away

**1. The eligibility engine is deterministic SQL.**

The moment an LLM touches the code path that decides whether a student qualifies, you have lost the property that makes this system safe. Defend that boundary. The engine is a SQL query. The LLM writes the explanation on top, never reaches into the result, never overrides it.

**2. Three categories of population, in strict order.**

Reference data → Course metadata → Cutoff data. Cannot skip. Cannot reorder. Auto-creation of reference data from ingestion is silent corruption.

**3. Curation is engineering.**

The 50 course factsheets and 10 career pathways that fill your RAG are *the product*, not a side project. Start writing on Day 5 of Week 1. Treat them as deliverables with deadlines.

---

## 21. Companion deliverables

Files to build alongside this document:

1. Alembic migration files with all reference data baked in.
2. `courses` seed CSV with 261 Uni-Codes.
3. `course_aliases` seed CSV.
4. `apps/worker/jobs/ingest_zscores.py` — Step 4.
5. 100-case eligibility test fixture.
6. Factsheet template.
7. Schema diagram (image, dbdiagram.io export).
8. Admin Slice 1 frontend pages (ingestion upload, alias review, course edit).

Each can be a focused deliverable. The next blocker after Step 1 is Day 2's reference data migrations — you can either write them yourself with this masterplan as guide, or I can produce them as a single file (one migration per table, with seed data inline) ready to drop into your `alembic/versions/` folder.
