# degree-guidance — Handoff Prompt (v2)

**Purpose of this document.** You are continuing work on an existing, working backend project. This is a full state transfer so you start grounded instead of re-deriving anything. Read it fully before acting. The authoritative spec is `MASTERPLAN_v4.md` (1238 lines, organized **by weeks**); re-read the relevant section of it cold before each new piece of work. This handoff is the *state*; the masterplan is the *truth*.

---

## 0. What this project actually is (read this carefully)

This is a **university DEGREE-GUIDANCE platform**, not an eligibility checker. It guides a Sri Lankan A/L student toward the **degree programmes that fit them**, based on their **Z-score, district, and stream PLUS their personal preferences** (interests, career direction, location, university, etc.).

- **Eligibility is only the hard filter / the floor** — "what am I allowed to apply for given my Z-score, district, and stream."
- **The actual product is the guidance layer on top**: preference-driven **recommendation scoring** that ranks eligible degrees against what the student wants, and (later) a **RAG chat advisor** that reasons over factsheets to advise them.
- What's built so far (eligibility engine + admin data surface) is the **foundation**. The part that makes it *guidance* — the recommendation scoring (Week 3) and chat (Weeks 4–5) — is **still ahead**. Do not describe this project as merely an "admissions/eligibility" tool; that undersells its entire point.

---

## 0b. At-a-glance scoreboard (done vs to-do)

**Reference files to load with this handoff:** `MASTERPLAN_v4.md` (the spec — essential), `schema.sql`, `DATABASE_REFERENCE.md`, the seed CSVs, and the student handbook PDF. This handoff is *state*; the masterplan is *truth*.

### ✅ DONE (verified, 161 tests green, head = `2ccafb3d723e`)
- **Week 1** — project skeleton + seed reference data (courses, aliases, stream-eligibility, districts, universities, streams).
- **Data ingestion** — extraction (Steps 1–3 + the user's better-than-OCR method) and the Step 4 loader (`ingest_zscores.py`); 6,525 cutoffs loaded (exam year 2023).
- **Eligibility engine (Week 2)** — `POST /api/v1/eligibility`; deterministic §8.1 query; eligible/conditional classification; confidence tier; audit logging. Two real correctness fixes (`ENGINEERING_TECH` typo; float→Decimal cutoff boundary).
- **Eligibility test harness (§16.1)** — 116 cases, independent reference oracle, all 9 categories.
- **Admin Slice 1 — Auth (A1/A2)** — `users`/`admin_actions`/`auth_events` tables; deferred FK closed; credentials login + HS256 JWT; `require_admin`; `create_admin` bootstrap (one superadmin exists).
- **Admin Slice 1 — API (B1/B2)** — aliases CRUD + courses list/create/edit; all role-gated + audited (before/after JSONB).

### 🔜 TO DO (in rough masterplan order)
- **Part C — ingestion endpoints (Week 2 remainder).** C1: load a reviewed CSV via existing Step 4 (no new infra). C2: PDF→extraction as an Arq background job (needs Arq + Redis).
- **Part D — admin frontend (Week 2 remainder).** Next.js 14 (App Router) + Auth.js over the existing API (greenfield, no `web/` yet).
- **Week 3 — recommendation scoring.** ⭐ The actual guidance core: rank eligible degrees by Z-score **+ student preferences**. Fully specified in masterplan §9 — five weighted dimensions: interest alignment 0.30 (embedding similarity), career alignment 0.25 (tag overlap), Z-score margin 0.15, university preference 0.15, future-industry alignment 0.15; buckets Safe / Ambitious / Hidden-opportunity; the LLM writes 15–30 word explanations only and never touches the score. Untouched so far.
- **Week 4 — RAG + factsheets + pgvector.**
- **Week 5 — chat advisor layer; `student_profiles`/`conversations`.**
- **Deployment** + the deferred hardening (2FA, IP allowlist, least-privilege DB role, HTTPS, rate limiting).

(Details for each: §5 built · §6 masterplan mapping · §7 the C/D/Week-3 fork · §8 deferred ledger.)

---

## 1. Stack, environment, conventions

- **Backend:** FastAPI + async SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped[...] / mapped_column(...)`) + PostgreSQL 16 + asyncpg + Alembic. Python 3.13. Managed with **`uv`** (`.venv`, `source .venv/bin/activate`, `uv run pytest`, `uv add`).
- **OS:** WSL2 / Ubuntu. User edits in VS Code. Downloads land at `/mnt/c/Users/MSI/Downloads`.
- **Project root:** `~/project/degree-guidance`.
- **Database:** `degree_guidance`, user `degree_app`, password `123456`, localhost. Connect: `PGPASSWORD='123456' psql -h localhost -U degree_app -d degree_guidance`.
- **`.env` keys:** `DATABASE_URL` (asyncpg DSN), `DATABASE_URL_SYNC` (psycopg2, for Alembic), `ENVIRONMENT`, `LOG_LEVEL`, `PYTHONPATH`, `JWT_SECRET_KEY` (64-hex, generated locally), `JWT_ALGORITHM=HS256`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60`.
- **Config:** `core/config.py` → pydantic-settings `Settings` (singleton `settings`), `SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")`. `jwt_secret_key` is a **required** field.
- **Integration seams:** `from core.db import Base, AsyncSessionLocal, engine`; `from core.config import settings`. `core/models/__init__.py` imports each model with an explicit `__all__` so Alembic's `from core import models` sees them.

### Working discipline (the user is strict about this — honor it)
- **"DON'T ASSUME ANYTHING. CHECK EVERYTHING. Consider the changed ones."** Verify against real files / live DB / the masterplan before building. Never infer a file's contents or a schema — read it.
- **Per-phase pattern:** (1) re-read the relevant masterplan section cold → (2) pre-phase verification (queries + file reads) → (3) build → (4) validate (syntax + logic) → (5) gated, step-by-step A→Z walkthrough with explicit STOP gates. The user runs each step and pastes output before proceeding.
- The user wants **complete working deliverables with verification**, and **honest critique over reassurance**. Surface inconsistencies and your own mistakes openly.
- In Claude Code you can read/edit files and run `alembic`/`pytest`/`psql` directly — do so, but keep the verify-first, show-your-checks discipline.

---

## 2. Key decisions already made (do not relitigate without reason)

1. **Masterplan is organized by WEEKS, not phases.** The "Phase 1–6" numbering came from a prior handoff and only described the ingestion→eligibility build.
2. **Seed CSVs are FROZEN ("Option 1")** at `data/seeds/` = 261 courses / 261 aliases / 611 stream-eligibility rows (2024/25 Section-5 snapshot). **All deltas are owned by migrations, never by editing the CSVs.** This avoids rebuild PK-collisions.
3. **`year` = the A/L exam year = handbook-title-year − 1.** The 2024/2025 handbook's Section 9 data is exam year **2023**. Only 2023 is loaded.
4. **FastAPI owns the JWT.** The masterplan says "Auth.js + JWT," but there is no frontend yet, so FastAPI is the JWT authority now (HS256, credentials auth). When the Next.js frontend lands, Auth.js becomes a thin client that calls `/api/auth/login` and carries the token. Forward-compatible.
5. **Auth mechanism = credentials** (email + bcrypt password hash in `users.password_hash`). Not OAuth.
6. **`users` table is created in Week 2** (minimal + `role`), and **extended** in Week 5 (student_profiles etc.) — not recreated. (Resolves a masterplan §17 Week 2 vs Week 5 inconsistency.)
7. **The extraction pipeline ALREADY EXISTS — do NOT rebuild it.** Masterplan §7.1 lists Steps 1–3 (`step1_extract_images.py` HSV crop, `step2_course_names_to_csv.py` EasyOCR, `step3_zscores_to_csv.py` EasyOCR + grid clustering) as "your existing Steps 1–3, Works." NOTE: the masterplan documents only the **EasyOCR** approach; the user has also built a **better-than-OCR extraction method** that is NOT reflected in the masterplan (exact nature/location UNCONFIRMED — ask the user; needed for Part C2). The masterplan is not wrong here, it just predates that improvement.
8. **Step 4 loader = `apps/worker/jobs/ingest_zscores.py`** (already built; loaded the 6,525 cutoff rows).
9. **Migrations are hand-written, not autogenerated.** Use the clean pattern: `alembic revision -m "..."` to make a stub, then auto-inject hashes by reading `revision`/`down_revision` from the stub into the prepared body (placeholders `REPLACE_WITH_GENERATED_HASH` / `REPLACE_WITH_DOWN_REVISION`), then GATE before upgrading: grep the hashes, `grep -c REPLACE_WITH` must be `0`, `alembic heads` must show a single head. Never hand-edit `alembic_version` except to repair a desync.
10. **Course/alias tables are accessed via raw SQL (`text()`)** in the code we wrote (eligibility engine + admin endpoints), consistent with each other. The masterplan §7.2 Step 4 code imports ORM models named `District, Course, CourseAlias, ZScoreCutoff, IngestionRun, ParseError` from `core.models` — so those model classes very likely exist (the working `ingest_zscores.py` imports them). Verify their presence/exact fields in the repo before relying on them. Auth models (`User`, `AdminAction`, `AuthEvent`) and eligibility models (`CourseMedium`, `EligibilityAudit`) are confirmed and used as ORM.

---

## 3. Migration chain (exact, all applied; head = `2ccafb3d723e`)

| # | hash | what it did |
|---|------|-------------|
| 16 | `65a2d08989b1` | 5 missing courses; fixed `ENG_TECH`→`ENGINEERING_TECH` typo (was silently inserting 0 eligibility rows) + FK pre-validation |
| 17 | `f7a8b457dce3` | 266 unicode self-aliases, `source='unicode_self_alias_2024'`, `ON CONFLICT (alias_text, course_code) DO NOTHING` |
| 18 | `707b571ec8c2` | `course_mediums` + `eligibility_audit` (user_id left FK-less, deferred) |
| 19 | `70cacf08afcc` | `users` (+ role CHECK + partial idx), `admin_actions` (exact §5 DDL), **closed** the `eligibility_audit.user_id` FK → users ON DELETE SET NULL |
| 20 | `2ccafb3d723e` | `auth_events` (append-only; event_type CHECK; FK→users SET NULL; 2 DESC indexes) — **HEAD** |

Chain is linear and clean. `alembic current` → `2ccafb3d723e (head)`.

---

## 4. Live database state (verified)

- **Counts:** 266 courses · 532 course_aliases (all `is_verified=true`, 0 unverified) · 6,525 z_score_cutoffs (all `year=2023`) · 626 course_stream_eligibility · 25 districts · 21 universities · 7 streams. `admin_actions`/`auth_events` empty apart from cleaned test rows. `course_mediums` empty.
- **Streams (codes):** `ARTS`, `COMMERCE`, `BIO_SCIENCE`, `PHYSICAL_SCIENCE`, `ENGINEERING_TECH`, `BIOSYSTEMS_TECH`, `ICT`.
- **One superadmin user exists** (created via `scripts/create_admin.py`).

### Real data anchors (used in tests; trustworthy)
- **001A Medicine cutoffs (2023):** COLOMBO 2.3700, GAMPAHA 2.3700, JAFFNA 2.3703, VAVUNIYA 2.8227 (disadvantaged, highest), **MULLAITIVU = NULL (NQC)**. 001A is `BIO_SCIENCE`, `district_quota`, active.
- **All-island-merit** courses store one uniform cutoff replicated across all 25 districts (e.g., 019A Arts = 1.6698 everywhere).
- **Aptitude courses** (`requires_aptitude_test=true`, `district_quota`, per-district varying, some negative): 023G Architecture, 024G Design, 034G Fashion, 068C Music, 069Z Dance, 070E Art&Design (down to −0.6634), 085Z Visual Arts, 100D Film&TV.
- **NQC** = NULL `z_score` (1,048 cells in 2023) → always excluded from eligibility results.

### Schema facts (from `schema.sql`)
- **courses:** `course_code` PK (varchar 15); `university_id` NOT NULL FK→universities ON DELETE RESTRICT; `faculty_id` FK→faculties ON DELETE SET NULL; `name_en` NOT NULL; `name_si/name_ta`; `course_number`; `degree_type`; `duration_years numeric(3,1)`; `selection_basis` CHECK in (`district_quota`,`all_island_merit`) default `district_quota` (`ck_courses_selection_basis`); `requires_aptitude_test` bool; `description`; `career_outlook`; `is_active` bool default true; `first_intake_year`; `metadata jsonb default '{}'`; `created_at`/`updated_at` (**no update trigger — PATCH must set `updated_at = now()` explicitly**).
- **course_aliases:** `alias_id` serial PK; `course_code` FK→courses ON DELETE CASCADE; `alias_text` text; `source` varchar(50); `confidence numeric(3,2)`; `is_verified` bool default false; `created_at`. **UNIQUE (alias_text, course_code) = `uq_alias_per_course`** (duplicate → handle 409). GIN index on `alias_text`.
- **universities:** `university_id` PK; `code`; `name_en`; `name_si/ta`; `short_name`; `district_id`; `website_url`; `established`; `is_active`.
- **faculties:** `faculty_id` PK; `university_id` NOT NULL; `name_en`; `short_name`; `website_url`.
- **ingestion_runs** and **parse_errors** tables EXIST.
- **z_score_cutoffs:** `(year, course_code, district_id, z_score nullable, notes)`, conflict key `(year, course_code, district_id)`.

---

## 5. What is built (file inventory) — 161 tests passing

**core/**
- `config.py` (DB + JWT settings), `db.py` (Base, async engine, AsyncSessionLocal), `security.py` (bcrypt `hash_password`/`verify_password`, PyJWT `create_access_token`/`decode_access_token`).
- `models/`: `eligibility.py` (`CourseMedium`, `EligibilityAudit` — user_id now has FK), `auth.py` (`User`, `AdminAction`, `AuthEvent`), `__init__.py` (registers all). (Pre-existing course/university/etc. models exist but their class names were never confirmed — code uses raw SQL for those tables.)
- `schemas/`: `eligibility.py`, `auth.py` (`LoginRequest`, `TokenResponse`, `CurrentUser`), `admin.py` (alias schemas), `admin_course.py` (course schemas).
- `eligibility/engine.py` (deterministic §8.1 query; classifies eligible/conditional; confidence tier; writes audit row; z bound as `Decimal(str(z))` for exact boundary).

**apps/api/**
- `main.py` (mounts routers + `/health`), `dependencies.py` (`get_db`, `get_current_admin` → 401/403), `admin_audit.py` (`log_admin_action`, `json_safe_row`, `hash_ip`).
- `routers/`: `eligibility.py` (`POST /api/v1/eligibility`), `auth.py` (`POST /api/auth/login`, `GET /api/auth/me`), `admin_aliases.py` (GET/POST/PATCH/DELETE `/api/admin/aliases`), `admin_courses.py` (GET/PATCH/POST `/api/admin/courses`).

**apps/worker/**
- `jobs/ingest_zscores.py` (Step 4 loader). `ocr/__init__.py` is empty (the existing Steps 1–3 / better-than-OCR extraction live elsewhere — confirm with user).

**scripts/** `create_admin.py` (first-admin bootstrap; interactive password).

**tests/** `conftest.py` (per-test NullPool engine bound to current loop — avoids async loop-scope bugs; `db_session`, `client` with `get_db` override, autouse `_isolate_audit`), `fixtures/eligibility_cases.yaml` (116 cases), `integration/`: `test_eligibility_engine.py` (116 parametrized + independent reference oracle + invariants + 001A anchors), `test_eligibility_api.py`, `test_auth_foundation.py`, `test_auth.py`, `test_admin_aliases.py`, `test_admin_courses.py`. **Total: 161 passing.**

### Endpoints live
`POST /api/v1/eligibility` · `GET /health` · `POST /api/auth/login` · `GET /api/auth/me` · `GET/POST/PATCH/DELETE /api/admin/aliases[/{alias_id}]` · `GET/PATCH/POST /api/admin/courses[/{course_code}]`. Every `/api/admin/*` route is gated by `require_admin` (role in admin/superadmin) and every mutation writes an `admin_actions` row (before/after JSONB via `log_admin_action`).

### Conventions for new admin work
- Raw SQL via `text()` for course/alias/cutoff tables. `AdminAction` ORM only for audit rows.
- `log_admin_action(db, admin=..., action_type="<resource>.<verb>", target_table=..., target_id=..., before=..., after=..., request=...)`; dotted action_type (`alias.create`, `course.update`, …); `json_safe_row` converts datetime/Decimal/UUID before JSONB.
- Test cleanup ordering matters: `admin_actions.admin_user_id` is **ON DELETE RESTRICT**, so delete a test admin's `admin_actions` *before* deleting the test user. Mark test rows (e.g. alias_text `ZZTEST_%`, course_code `ZZ%`, emails `authtest-%`).

---

## 6. Where this sits on the masterplan

- **Week 1** (skeleton + seed reference data): done.
- **Week 2**: eligibility engine ✓ · §16.1 test set ✓ · Admin Slice 1 — login/role-check ✓, aliases ✓, courses ✓. **Remaining in Week 2: Part C (ingestion endpoints) and Part D (admin frontend).**
- **Weeks 3–5 + deploy: untouched.**

---

## 7. The fork — what to build next (user decides)

- **Part C — ingestion endpoints (backend).**
  - **C1** = `POST /api/admin/ingestions` accepts a *reviewed* merged CSV + `exam_year`, calls the existing `ingest_zscores` Step 4 loader, returns the `ingestion_runs` summary + `parse_errors`; plus `GET /api/admin/ingestions` and `GET /api/admin/ingestions/{run_id}`. Role-gated + audited. **No new infrastructure** — reuses existing loader + existing tables. The masterplan §7.2 gives the exact interface to call (don't reimplement): `ingest_zscores(csv_path, exam_year, triggered_by) -> {run_id, processed, failed, status}`, with an Arq wrapper `ingest_zscores_job(ctx, csv_path, exam_year, admin_user_id)`. **Read the actual `apps/worker/jobs/ingest_zscores.py` to confirm the signature matches before wiring.**
  - **C2** = `POST /api/admin/ingestions` PDF upload → runs the extraction (the user's better-than-OCR method) as a **background job**. Needs **Arq + Redis** (the one genuinely-missing infra). §7 says extraction is multi-minute and must not run in an HTTP handler. **Confirm with the user what the better-than-OCR extraction is and where it lives before wrapping it.**
- **Part D — admin frontend.** Next.js 14 (App Router) + Auth.js admin app under `web/` (greenfield, no app yet). Auth.js Credentials provider → calls `/api/auth/login`, carries the JWT. Pages per §14.4. **Best done in Claude Code.**
- **Week 3 — recommendation scoring (the actual product core).** Preference-driven ranking of eligible degrees by Z-score + student preferences. **Still untouched; this is what makes it "guidance."** Read masterplan §9 cold and pin down the preference dimensions with the user before building.

---

## 8. Deferred ledger (intentional, tracked, not bugs)

1. `course_mediums` empty → `available_mediums` returns `[]` until populated.
2. **Year-fallback not implemented** — only 2023 loaded, so confidence tier is always `current`; the missing-year test asserts current (empty) behavior. Revisit when a 2nd exam year is ingested (and update that test case).
3. **Full cold rebuild (`downgrade base` → `upgrade head` → re-run cutoff ingestion) never executed end-to-end.** Logic is sound (the `ENGINEERING_TECH` fix + frozen CSVs), but unverified. Heavy due to 6,525-row re-ingestion.
4. **422 deprecation:** new code uses `HTTP_422_UNPROCESSABLE_CONTENT`; `eligibility.py` + `admin_aliases.py` may still use the deprecated `..._ENTITY` unless the optional swap was applied. Cosmetic only (both = HTTP 422).
5. **2FA + IP-allowlist** admin hardening (§15.1) deferred to deployment.

---

## 9. Open questions to resolve with the user

1. **The better-than-OCR extraction:** what is it, where does it live, what's its interface? (Needed for C2.)
2. **Week 3 preference dimensions:** beyond Z-score/district/stream, what does the guidance weigh — career interest, field, location, university, others? (Needed for scoring.)
3. **ORM model classes:** the masterplan §7.2 names them `District / Course / CourseAlias / ZScoreCutoff / IngestionRun / ParseError` in `core.models`. Confirm they exist in the repo with those names/fields (the code we wrote used raw SQL to avoid depending on this; verify before switching to ORM).
4. **`eligibility_audit` column parity:** confirm the columns our migration 18 created match the §5.1 item 4 DDL (`request_hash`, `cutoff_year_used`, `result_payload` JSONB, `latency_ms`, etc.). The engine + audit are tested and working, but a field-by-field diff against §5.1 is worth one check.

---

## 10. First moves in the new session

1. `cd ~/project/degree-guidance && source .venv/bin/activate`
2. Verify the baseline: `alembic current` (expect `2ccafb3d723e (head)`), `uv run pytest tests/ -q` (expect 161 passed), `git status`.
3. Run the **pre-build check** in §11 below.
4. Confirm with the user which fork (C / D / Week 3) to take.
5. Re-read the relevant masterplan section cold, run pre-phase verification, then build with gated steps.

---

## 11. Pre-build verification + security review (run BEFORE C or D, report findings to the user)

**Do this as an explicit pass and report what you find — do not skip it, and do not claim the codebase is "secure." Security review reduces risk; it does not certify safety. Distinguish (a) confirmed issues, (b) things to watch, (c) things you checked and they're fine.**

### A. Consistency / correctness (everything must reconcile)
- `alembic current` = `2ccafb3d723e (head)`; `alembic history` is a single linear chain, no branches.
- `uv run pytest tests/ -q` → 161 passed (note any warnings).
- Models vs DB agree: spot-check that `core/models/*` reflect the live schema (esp. the `eligibility_audit.user_id` FK and the auth tables). A dry `alembic revision --autogenerate` into a throwaway file should produce ~no schema diffs (then delete it — do not apply autogenerated migrations; migrations here are hand-written).
- The **untested claim** on the ledger: the full cold rebuild (`downgrade base` → `upgrade head` → re-ingest cutoffs) has never run end-to-end. If the user wants certainty, do it against a scratch database, not the dev DB.

### B. Security review (this is a student-facing app holding real data — take it seriously)
Review, and run tooling rather than eyeballing where possible:
- **Dependency CVEs:** `uv run pip-audit` (or `uvx pip-audit`). Report any vulnerable packages.
- **Static analysis:** `uvx bandit -r core apps scripts` and `uvx ruff check`. Triage real findings vs noise.
- **Secrets:** confirm `.env` is git-ignored and **no secret (esp. `JWT_SECRET_KEY`, DB password) is committed** — `git log -p` / `git grep` for `123456`, `JWT_SECRET`, etc. The dev DB password `123456` is fine for local only; it must NOT ship to any deployed environment.
- **Auth surface:** JWT verification rejects tampered/expired/wrong-secret tokens (already unit-tested); `require_admin` correctly returns 401 (no/invalid token) and 403 (valid token, non-admin); the login route returns the **same** message for unknown-email and wrong-password (no account enumeration — already implemented). Confirm token expiry is enforced and there's no path that trusts an unverified claim.
- **Input handling / SQL:** the codebase uses parameterized `text()` queries — confirm **no f-string interpolation of user input into SQL**. The one place SQL is built dynamically (PATCH `SET` clauses) takes keys **only** from a fixed `_UPDATABLE`/`_COLS` allowlist, never raw user keys — keep it that way for any new endpoint.
- **Authorization on every admin route:** every `/api/admin/*` route must depend on `require_admin`; every mutation must write an `admin_actions` row. Verify no new route forgets either.
- **For Part C specifically:** file upload (PDF/CSV) needs size limits, content-type/extension validation, and safe temp-file handling; never pass an uploaded filename into a shell or a path without sanitizing; the extraction job must run out-of-band (Arq), not in the request.
- **For Part D specifically:** store the JWT safely (httpOnly cookie preferred over localStorage), enforce CORS to known origins, and never expose the JWT secret or DB credentials to the browser bundle.
- **Deferred hardening still owed before production (§15.1):** 2FA, IP allowlist on `/admin/*`, a least-privilege DB role separate from `degree_app`-as-owner, HTTPS/secure cookies, rate limiting.

Report findings to the user as a short triaged list. If something is a genuine vulnerability, say so plainly; if you couldn't fully verify something, say that too.

*The masterplan (`MASTERPLAN_v4.md`), `schema.sql`, `DATABASE_REFERENCE.md`, and the seed CSVs are the reference inputs. This handoff is state; the masterplan is truth.*
