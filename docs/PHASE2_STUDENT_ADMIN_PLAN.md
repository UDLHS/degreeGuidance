# Phase 2 Master Plan — Year-aware student side, agent oversight, content management, hardening

**Status:** approved direction, implementation pending per-phase go
**Decided:** 2026-07-10 (session on branch Admin-Panel)
**Prerequisite state (verified, not assumed):** the yearly update cycle is correct at the API level — promoting a new handbook year flips the student default automatically (2024 served as `current`), previous years are served with honest confidence tiers (`previous_year` / `estimated`), missing years degrade gracefully. 2023 + 2024 books fully ingested: every cutoff column captured across `z_score_cutoffs` (+6,400/yr), `course_stream_cutoff_overrides` (stream splits: 107L, 022R/022W, 021L), and `unmapped_cutoffs` (codeless: Computing & IS 2023).

---

## Locked decisions

| # | Decision |
|---|----------|
| D0 | **Year = A/L examination year** (settled 2026-07-12 after the prod duplicate-year incident). A cutoff dataset is labeled with the exam year the book states: *"Based on the results of the G.C.E. (A/L) Examination YYYY"*. handbook_YYYY.pdf is the book handed to cohort YYYY and carries exam **YYYY−1** cutoffs (2025 book → exam 2024, 2024 book → exam 2023, 2023 book → exam 2022). When uploading, the admin enters the **exam year**, not the file/handbook year. |
| D1 | Year selection lives on the **results view** ("Viewing YYYY cutoffs ▾" switcher). The 5-step flow stays 5 steps; default = latest promoted year. |
| D2 | Previous-year visibility per course = **delta chip + history popover** (no separate compare screen for now). |
| D3 | **Factsheets move to the DB** as source of truth (seeded from the 129 `content/factsheets/*.md`; files remain as the git snapshot). Required for safe editing in prod (ephemeral FS). |
| D4 | Chat stays on **Gemini** for now. Agent config is stored model-agnostic so a later switch (e.g. Claude) is a config change, not a rebuild. |
| D5 | **All admins have equal permissions** (`admin` == `superadmin`, which is already how `get_current_admin` works). New **Admins page** with a create-admin button. |
| D6 | **Weaknesses are fixed after the major tracks** — but every major phase includes the design-ahead hooks below so deferring causes zero rework. |

## Design-ahead hooks (so deferred fixes bolt on cleanly)

- Public endpoints (`/years`, cutoff history) get clean, cacheable response shapes → rate-limit/cache middleware can wrap later without contract change.
- Conversations viewer ships with time-range filters + indexes → the future retention/purge job is a pure addition. A short privacy note ships with the viewer from day one.
- `agent_configs` stores `model_name` + JSONB params → provider-agnostic (D4). Live facts (available years, latest year, course count) are **injected at render time**, never typed into the prompt — this structurally kills the prompt drift found in `orchestrator.py` ("2019–2023", "261 courses", "2023 cutoffs": all stale today).
- Factsheet rows carry `version`, `updated_by`, `content_hash` → audit + staleness logic identical to the current file-hash mechanism.
- Admins are deactivated (`is_active=false`), never deleted; `auth_events` already records every login attempt → future login throttling has its data source.

---

# Major phases (in order)

## Phase 1 — Student year selection + previous years  (size: M)
1.1 **Public `GET /api/v1/years`** — `[{year, is_latest}]` from promoted data. (~30 lines; the engine already accepts `exam_year` end-to-end.)
1.2 **Results-view year switcher** — default latest; switching re-runs the recommendation with `exam_year`; localStorage saves the chosen year. Replace the hardcoded "2023 cutoffs" copy on the Z-score step with the live year. Prominent banner when viewing a non-latest year (*"reference only — cutoffs shift each year"*). **Include here (cheap, same file):** the permanent guidance disclaimer — *"Guidance only; final selection is made by the UGC."*
1.3 **Chat year context** — pass `exam_year_used` into the chat context so the agent talks about the year the student is viewing.
1.4 **Per-course trend** — small public history endpoint (course_code → year→cutoff for the student's district, includes stream-override values); results cards show a delta chip ("↑ 0.03 vs 2023") + popover with the year-by-year numbers.
**Gate:** scripted E2E — promote → `/years` updates → default flips → every prior year selectable returns its verified numbers; full suite at baseline; typecheck clean.

## Phase 2 — Agent oversight part 1: conversations + usage  (size: M)
2.1 **Conversations viewer** — admin API (`GET /api/admin/conversations`, `GET …/{id}`) + pages: list (time, message count, student vs anonymous, search) and detail (full thread, per-reply `tool_calls` badges). Flag-for-review toggle (new nullable column). Privacy note in the UI. Available to all admins (D5).
2.2 **Usage cards on the dashboard** — conversations/day, messages/day, tool-usage mix; plus recommendation-usage stats from the already-populated `eligibility_audit` (queries/day, district/stream mix, latency) — near-free observability.
**Gate:** live conversations visible end-to-end; no student-facing change; suite baseline.

## Phase 3 — Admins management page  (size: S)
- `GET/POST/PATCH /api/admin/users` (admins only listing; create with email + display name + password — bcrypt via existing `core.security.hash_password`; deactivate/reactivate).
- UI: Admins page + **"Add admin"** button (D5); last-login shown from `auth_events`; cannot deactivate yourself; every action audited in `admin_actions`.
**Gate:** create a second admin, log in as them, verify equal access; deactivated admin is rejected at login.

## Phase 4 — Agent oversight part 2: agent config in DB  (size: M/L)
- Migration: `agent_configs` (id, name, system_prompt_template, model_name, web_search_default, max_tool_turns, guardrail notes JSONB, is_active, created_by, created_at) — versioned rows, exactly one active (same pattern as `scoring_config`).
- Orchestrator loads the active config (short TTL cache); **fallback to the current built-in prompt if the table is empty** — zero-risk rollout. Template placeholders (`{available_years}`, `{latest_year}`, `{course_count}`, `{today}`) filled at runtime.
- Admin UI: view active config, edit as a new version, activate/rollback (one click), **sandbox "send a test message"** panel that runs the real loop against a draft config without saving a conversation.
**Gate:** edit prompt → next student chat reflects it; rollback restores previous behavior; injected facts show 2024/265 automatically; suite baseline.

## Phase 5 — Factsheets to DB + manager  (size: L)
5.1 Migration: `factsheets` table (course_number unique, markdown content, version, updated_by, updated_at, content_hash) seeded from the 129 files; `index_factsheets` job reads the DB instead of the directory (same hashing/idempotency).
5.2 Admin **Factsheets page** (replaces the disabled sidebar placeholder): list with **coverage panel** (active course numbers with no factsheet — the existing `check_factsheet_coverage` logic as an endpoint), view rendered markdown, edit with preview, save = new version + audit + **auto-enqueue reindex for that course**.
**Gate:** edit a factsheet → reindex → `search_knowledge` and `lookup_course` return the new text; interest-ranking reflects it; suite baseline.

## Phase 6 — Knowledge-base browser  (size: S/M)
- Admin **Knowledge page**: `document_sources` + chunk counts + `indexed_at` + stale flag (factsheet `content_hash` vs indexed hash); per-course and reindex-all buttons (Arq job, progress via run notes). Read-only chunk inspector.
**Gate:** stale flag appears after an edit and clears after reindex.

## Phase 7 — Yearly-loop hardening (admin)  (size: M)
7.1 Upload form: year **dropdown/validated input showing which years already have data** + explicit confirm when re-promoting an existing year (kills the 2022-typo class).
7.2 **Pre-promote auto-snapshot**: before any promote, automatically export that year's current matrix CSV to the per-year archive — every promote reversible in one step.
7.3 **Per-year archive** (raw PDF + final CSV + overrides/unmapped artifacts) retained permanently — also the file-retention gap flagged for the future year-comparison chat features.
7.4 Post-promote checklist card on the run page: coverage gaps, stream-variant count, codeless count, **"students now see YYYY by default"**.
**Gate:** dry-run a re-promote; snapshot written; checklist correct; suite baseline.

## Phase 8 — New-course onboarding (added 2026-07-11, user request)  (size: M)

**Problem (verified):** when a new handbook year introduces a new course, the
pipeline already creates an inactive stub via change-review, and the Factsheets
page already shows a red "no factsheet" slot once it's active — but there is
**no admin UI/API for stream eligibility at all**, and the eligibility engine
only serves courses with `course_stream_eligibility` rows. A new course can
therefore be approved, activated, promoted, factsheeted… and still be
**invisible to every student, silently**. Onboarding steps are also scattered
across pages with nothing tracking completeness.

**Design principle:** slots = *visible absences derived from live data*, never
auto-created placeholder rows (an empty auto-created factsheet would be
embedded into the KB and quoted by the agent — worse than missing).

8.1 **Stream-eligibility editor** — GET/PUT `/api/admin/courses/{code}/streams`
    (replace-set, validated, audited) + stream checkboxes on the Courses page.
8.2 **Onboarding status** — per new/incomplete course, computed live:
    active? streams set? cutoffs present (latest year)? factsheet exists?
    subject rule exists or consciously ungated? Year-agnostic, so every future
    book surfaces its new courses automatically.
8.3 **UI** — "Needs onboarding" panel on the Courses page with deep links;
    the post-promote checklist gains "new courses: X of Y fully onboarded".
8.4 **Safety warning** — activating a course with zero streams warns
    "students will not see this course until streams are set".
8.5 Factsheet slot: already exists (missing badge + create-from-scratch
    editor); the onboarding panel links straight to it. (AI-drafted factsheet
    stays deferred and human-gated — plan §3.4.)
8.6 **Admin-authored knowledge articles** (added 2026-07-12, user request) —
    knowledge beyond courses: aptitude-test guides, UGC procedures,
    scholarship rules, deadlines. New `articles` concept indexed through the
    SAME chunk→embed→reindex machinery factsheets use (source_type
    'article'); admin Knowledge page gains an Articles tab with a
    title+markdown editor. Complements the factsheet editor (which already
    covers per-course manual knowledge).

**Gate:** simulated lifecycle test — new stub → streams → activate → sentinel
cutoff → course appears in student eligibility; zero-stream activation warns.

**Order note:** built immediately after W2 (it is yearly-loop reliability and
should exist before the next real handbook).

## Phase 9 — Extraction control & recovery (added 2026-07-11, user request)  (size: S/M)

**Order note (user, explicit):** build **AFTER everything else is done** — this
is polish on an already-working pipeline, not a blocker.

**Motivation (from a real incident):** the 2024 handbook extraction OOM-crash-
looped on the free-tier worker (fixed in `8a0e588` by chunked PDF reads,
1.25 GB→313 MB). While stuck, there was **no admin way to stop a running
extraction** — it just retried until arq exhausted its tries and left the run
orphaned at `running` forever, needing a manual DB reset + Redis re-enqueue
(done by hand this session). Both gaps should become first-class admin actions.

9.1 **Cancel a running extraction** — admin action on the run page:
    `POST /api/admin/ingestions/{run_id}/cancel`. Uses arq's `abort_job`
    (needs `allow_abort_jobs=True` on the worker) to signal the job, and marks
    the run `cancelled` (new status in the `chk_run_status` check). The
    long synchronous pdfplumber stage runs in `asyncio.to_thread`, so define
    what cancel actually interrupts (between-stage checkpoints vs. hard abort)
    and make partial artifacts safe to discard.
9.2 **Recover an orphaned run** — admin action to reset a run stuck in
    `running` (no live job) back to a re-runnable state and re-enqueue it,
    reusing the stored PDF artifact (exactly the manual recovery done this
    session — the artifact store already makes it a DB-only operation). Guard
    so it only fires when Redis has no live/queued job for that run.
9.3 **Liveness signal** — surface the arq worker health-check (last-seen
    timestamp, in-progress/queued counts) on the admin dashboard so a hung or
    down worker is visible before a user reports "still running".

**Gate:** cancel a real extraction mid-run → status `cancelled`, no partial
promote possible; orphan-recover a reset run → completes on the fixed worker;
worker-down shows on the dashboard. Never breaks the normal happy-path flow
(the whole pipeline — grid → consolidate → book-text → uni-code → suggest →
columns → artifacts → needs_mapping — stays byte-identical; verified this
session end-to-end at 313 MB).

**Ops note — pathological PDFs (settled 2026-07-12):** a book that extracts
absurdly slowly (the original 2025 file: ~43 s *per document open* from giant
compressed object streams → prod timeout) is fixed by **normalizing the
file** (lossless `pikepdf` rewrite, object streams disabled — proven
cell-identical output, 14× faster, 330 MB peak), never by bending the
pipeline around one bad encoder. Candidate 9.4: auto-detect the open-toll at
upload and normalize server-side.

---

# Weakness phases (after majors — order fixed, scope agreed)

| Phase | Fixes | Notes |
|-------|-------|-------|
| **W1 — Abuse & cost guards** | Rate limiting on `/chat` + `/recommendations` (per-IP/session), daily Gemini budget guard, request-size caps | **First weakness fixed** — protects money and uptime; middleware-only thanks to Phase-1 hooks. |
| **W2 — Production parity & ops** | Provision Render worker + Upstash Redis, apply migrations 37/38 (+ later ones) to Supabase via the standalone-script method, error tracking (Sentry-class) + `/health` + uptime alert, one load test of `/recommendations` | **Required before the first real prod yearly update** — today the PDF pipeline runs only locally. |
| **W3 — Admin security** | Login throttling/lockout (data already in `auth_events`), password policy, optional TOTP later | |
| **W4 — Privacy & retention** | Retention policy + purge job for anonymous conversations, privacy line in student chat UI, documented policy page | Viewer ships earlier with the note; purge is additive. |
| **W5 — Correctness completeness** | O/L-prerequisite notes on results ("also requires O/L: …") and honest "A/L-based check" caveat; Subject-Rules **coverage panel** (which courses are ungated); populate-or-hide `course_mediums` | |
| **W6 — Adoption polish** | Mobile verification pass, shareable results export, "how this works/FAQ" page, i18n groundwork (translatable copy; si/ta columns exist) | Localization itself is a separate future project. |

---

# Cross-cutting rules (unchanged, binding for every phase)

1. **Additive migrations only**; local first, prod via the standalone-asyncpg method (UPDATE the single `alembic_version` row).
2. **Deterministic core; AI only behind human gates** (factsheet regeneration stays draft→approve when it comes).
3. Every admin mutation writes `admin_actions`.
4. Each phase: tests added, **full suite at baseline (no new failures)**, frontend typecheck clean, live verification against the running stack, then **commit as udula** (no Co-Authored-By), one feature-scoped commit per phase.
5. Anything touching ingestion is verified against **both** the 2023 and 2024 books (2021 remains explicitly out of scope).
6. Student-facing copy stays honest: years labeled, previous years marked as reference, guidance-not-guarantee disclaimer everywhere results appear.
