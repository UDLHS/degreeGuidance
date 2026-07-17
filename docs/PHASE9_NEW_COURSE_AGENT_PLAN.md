# Phase 9 — New-course agent: book-derived onboarding at the gate

Added 2026-07-15. **Revised 2026-07-16 after reading the actual handbook** —
the original design was wrong on its central point and is corrected below.

Supersedes Phase 8's *passive* onboarding panel with an *enforcing* gate fed by
the book itself.

---

## THE CORRECTION (read this before anything else)

The first draft of this plan said: *"Gemini reads the course's section and
returns structured fields, including streams."* **That is wrong and it is
dangerous. Do not build it.**

What reading the real book (2023/2024/2025) proved:

1. **The book states the facts. Read them; never infer them.** A course printed
   under `2.2.4 PHYSICAL SCIENCE STREAM` *is* a Physical Science course. That
   is a statement, not a guess. Deterministic parsing scored **99–100%**
   against the hand-seeded catalog — and found errors *in the catalog*.

2. **For cross-stream courses the book names no streams at all.** §2.2.8
   courses (Architecture, Quantity Surveying, IT) are defined purely by
   SUBJECT requirements — *"at least a 'C' in one of: Higher Maths, Combined
   Maths, Maths, Physics"*. So an LLM asked "which streams?" could only
   **guess from subject lists**, on the one field that decides whether a
   student ever sees the course. It would be fluent, confident, and wrong.

3. **The right rule was already in the codebase.** §2.1(8)/§2.2.8's own heading
   — *"COURSES OF STUDY FOR WHICH STUDENTS FROM DIFFERENT SUBJECT STREAMS ARE
   ELIGIBLE"* — means **all six streams**, with the SUBJECT rules filtering
   downstream. `core/ingestion/stream_tags.py` documented this convention
   already (migration 16), and it matches how the catalog seeded Architecture,
   Quantity Surveying and IT.

**So: a big careful reader, plus a small writer.** Deterministic parsing for
every FACT (streams, codes, names, intake, medium, duration). The LLM is only
for WRITING prose (factsheet/knowledge text) from facts already read — where
fluency helps, mistakes are cheap, and the draft gate (D4) catches them.

**And where the book cannot be read, say so — never guess and never stay
quiet.** An under-reported stream list is not "conservative": it makes a course
invisible to students who could have applied, which is the exact bug this phase
exists to kill.

---

## Locked decisions (user)

| # | Decision |
|---|---|
| **D1** | **Approve is blocked until streams exist** ⇒ approved == visible. Enforced server-side (422), never a silent skip. |
| **D2** | **Agent proposes, admin edits, admin approves.** Every field pre-filled but editable, with its source page shown. |
| **D3** | **Factsheet = book first, then web enrichment** (book: streams/requirements/medium; web: careers/industry). |
| **D4** | **Course goes live on approve; the factsheet lands as a draft** and is indexed into the advisor only after separate approval. |
| **D5** | *(2026-07-16)* **ICT is a subject, not a stream.** The book names **six** streams (2024 p.28). The `streams` table's 7th row (ICT) is a modelling artifact. Never emit it as a stream; never build rules around it. |
| **D6** | *(2026-07-16)* **A new course needs subject rules too, not just streams.** Streams decide who *sees* it; subject rules decide who *qualifies*. Both belong at the gate. **BUILT 2026-07-16:** approve refuses without a subject rule (422) unless the course number already has a curated baseline row (which the gate refuses to overwrite). The rule is authored at the gate from the book's verbatim wording (never pre-filled with a guess — one-click templates only), validated structurally AND every subject name against the catalog (a misspelled subject would string-match no student ever — the silent-omission bug in a different coat), and written to `course_requirements` by apply in the same transaction as the course + streams. A course with no real constraint gets an explicit `{"type": "any_n_subjects", "count": 3}` — a visible decision, not a missing row. Enforced at approve only; promote does NOT block on it (no-rule courses are ungated by design for the legacy catalog, migration 24). `validate_subject_rule` in core/eligibility/subject_requirements.py. |

---

## Status

### Done + verified (uncommitted as of 2026-07-16)

- **9.2 — the gate.** Approve refuses without university + name + streams (422,
  server-enforced). Apply creates the course **live** and writes
  `course_stream_eligibility` in the same transaction. Pre-fills name/university
  /page from the book's Uni-Codes section (`_book_prefill`), university by exact
  normalised match only — never a fuzzy guess.
- **9.3 — the promote gate.** `promote` returns 409 listing any new course in
  the run that is unfinished (pending, approved-but-not-applied, or applied
  without streams). Closes both silent-loss doors: the checklist used to only
  *count* them.
- **`core/ingestion/course_details.py`** — reads §2.2 per course: name,
  streams, proposed intake, prerequisite prose verbatim, page number. Works on
  2023/2024/2025 with no per-year changes. **99–100% vs the catalog.**
- **`core/ingestion/catalog_audit.py`** — read-only compare of catalog vs book.
  Distinguishes `invisible` (we're missing a stream the book grants — the
  costly direction) from `over_granted` (we grant one it doesn't).
- **Tests**: 376 passing (14 new unit tests quoting real book strings, 9
  integration tests pinning the gate).

### Known problems (open)

| # | Problem |
|---|---|
| **P1** | **131 Financial Economics is still wrong in PRODUCTION.** Book p.117 grants Arts + Commerce; prod grants all six. Fixed in the dev DB only (2026-07-16). Real students are currently shown a degree they cannot enter. Needs a standalone Supabase script + explicit go-ahead. |
| **P2** | **124's class cannot be read.** The book grants entry *"or [with] any three of: Chemistry, Physics, Biology, Agricultural Science"* — subjects, no stream. The parser reports a **floor** and sets `streams_may_be_incomplete`; a human must widen it. Never auto-"correct" the catalog down to match the book here. |
| **P3** | **`course_mediums` is EMPTY for the whole catalog** — yet students see medium tags and the book prints `Medium : English` for every course. |
| **P4** | **Nothing calls the parser or the audit.** Both are working modules with no caller; the admin sees neither. |
| **P5** | **A stream restriction survived only as a free-text note.** 131's rule carried `notes: "Other 2 subjects from Arts or Commerce stream."` — correct, human-written, and read by no code. Notes are not enforcement. |

---

## Remaining work

### 9.1b — wire the reader in
Call `parse_course_details` inside `apps/worker/jobs/extract_pdf.py`, where the
PDF is already open and already swept (grid, book text, Uni-Code section) —
memory stays bounded via `iter_pages_chunked`. Persist as artifact
`course_details.json`. Everything below reads that artifact instead of
re-opening the book.

### 9.2b — the gate, completed
Pre-fill the New-courses card from `course_details.json`: streams (ticked),
intake, the book's requirement prose, page number. Show the
`streams_may_be_incomplete` warning inline. **Add the subject-rules slot (D6)**,
pre-filled with the book's requirement text for the admin to confirm.

### 9.3b — surface the audit
Run the audit at confirm/promote and show disagreements on the run page:
"N existing courses disagree with this book" + the two severities. This is what
finds the next 131 instead of luck. Report-only; an admin decides.

### 9.4 — factsheet / knowledge draft — **DONE (2026-07-16, factsheet half)**
Built as designed, with one structural improvement: drafts live in their own
`factsheet_drafts` table (migration 44) that the index job never reads — so D4
is enforced by architecture, not by a filter someone can forget. Pieces:

- `apps/worker/jobs/generate_factsheet.py` — arq job; source order is the law:
  book facts from the run's `course_details.json` (verbatim requirements, page,
  streams, intake) → catalog facts → DDG web colour (degrades gracefully,
  recorded in provenance). Gemini writes prose only. Failure lands LOUD on the
  row (`status='failed'` + error).
- Approve endpoint = the ONE door: copies the (possibly admin-edited) text into
  `factsheets` through the same versioned/audited/auto-reindexed path as a hand
  edit, deletes the draft in the same transaction.
- `apply_changes` auto-queues a draft for every newly created course (with the
  run's book pinned), best-effort — a queue outage never fails the apply.
- UI: draft review panel in the factsheet editor (provenance + the
  `streams_may_be_incomplete` warning inline; Approve unlocks only after the
  draft is loaded into the editor — what you see is what goes live), badges +
  "drafts to review" filter on the Factsheets list.
- Tests: `tests/integration/test_factsheet_drafts.py` (9) + apply-auto-queue
  pin in the gate suite. 392 passing. Verified end-to-end in the running admin
  UI (login → list badge → panel → approve → v1 + reindex queued).

Still open from this item: KNOWLEDGE-article drafts (same mechanism, articles
table) — decide whether a new course warrants an article at all, or whether
factsheets cover it; revisit alongside 9.5.

### 9.5 — make the work visible — **CORE DONE (2026-07-17)**
Every note says what is missing AND where the book says it:

- **Subject Rules page**: a banner lists every active course number with no
  baseline rule, each carrying the newest ingested book's requirement prose
  VERBATIM + page (`GET /api/admin/requirements/gaps`; Arts/019 excluded —
  its 4-basket checker is by design). NOTE: as of 2026-07-17 the dev catalog
  has ZERO gaps — all ~129 active numbers except 019 are curated (the old
  "137 uncurated" figure wrongly counted per-code instead of per-number).
- **Courses page onboarding panel**: a missing factsheet now names the actual
  next step — "draft awaiting review / generating / FAILED" (from
  factsheet_drafts, 9.4) instead of a generic "no factsheet"; item carries
  `draft_status`.
- **Factsheets page**: covered by 9.4 (per-row draft badges + "drafts to
  review" filter chip + existing missing/stale chips).
- **Run page**: covered by 9.3b (catalog-audit card) + the gate card itself.

Still open from this item: whether the KNOWLEDGE page needs a per-new-course
banner at all — articles are general-purpose, not per-course; decide with the
user whether a new course warrants an auto-drafted article (9.4's open half)
or whether factsheets cover it.

### 9.6 — the rest of the book (user's list, 2026-07-16)

**9.6a DONE (2026-07-17) — mediums, duration, aptitude READ from the book:**

- `course_details.py` now reads each §2.2 block's `Duration :` (messy variants
  tolerated, "06 years [05 academic years + internship]" → 6.0) and `Medium :`
  — VERBATIM, multi-line capture with a strict continuation rule (a runaway
  once swallowed whole pages of section prose). Codes (EN/SI/TA) are parsed
  only when every token is unambiguously a language; a per-institution medium
  (Siddha/036: Jaffna-Tamil, Trincomalee-English) is flagged for a human,
  never guessed.
- **Anchor bug found + fixed:** the book prints `(Course Code : 001)` (colon)
  for Medicine and Dental Surgery — both were INVISIBLE to the reader since
  9.1b (never prefilled, never audited). Also handled: the plural anchor
  `(Course Codes : Mass Media - 020; Performing Arts - 041)`. 2024 coverage:
  115 → 125 blocks.
- `aptitude_section.py` reads the book's own per-Uni-Code test table by its
  PRINTED caps heading (the TOC prints the same words in title case — decoy).
  All three books: 24 codes; 2024/2023 match the hand-seeded flags exactly;
  **the 2025 book drops 082D and adds 141D** — the audit now surfaces exactly
  this (`aptitude_items`, severity `unwarned` > `over_warned`).
- Wired: one page-text sweep feeds both parsers in extract_pdf (new artifact
  `aptitude_codes.json`); `_book_prefill` carries book_duration/medium/
  aptitude; **apply writes them with the course** (mediums only when
  unambiguous); the gate card shows them; the audit card gained the aptitude
  section.
- `scripts/backfill_course_facts_from_book.py` (dry-run default, idempotent,
  fills only-empty): dev DB went 0 → **138 durations, 69 courses with medium
  rows** — everything the 2024 book prints. 036 correctly held for a human.
  **Run it on PROD alongside the 131 streams fix.**

**Still open in 9.6:**
- **Student UI rendering** of mediums/duration — student-side branch decision.
- **One course = many universities** at the gate — 142A/142B arrive as
  separate cards; nothing groups them for one review.
- **Renames** — a renamed course reads as *removed + added*, so we would
  deactivate a live course and create a duplicate beside it.
- **Removed courses** — already handled by the diff's whole-book safeguard;
  keep it in the agent's story.

---

## Risks

| Risk | Mitigation |
|---|---|
| Guessing a stream we cannot read | `streams_may_be_incomplete` + D2 (editable) + page shown; approve blocked until a human ticks |
| A future book changes format | Sections resolve by their printed **words** and structural **depth**, never by number (a `2.2.9 COMMERCE STREAM` still reads as Commerce). If the format truly changes it finds *nothing* and the admin fills in manually — it does not invent answers. |
| Extraction memory blow-up | `iter_pages_chunked` only; re-measure per book (`pdf-extraction-memory-limit`) |
| LLM writing prose the advisor states as fact | D4: draft before indexing |

## Explicitly out of scope

- A deterministic §2.2 grammar parser for subject *rules* (MASTERPLAN_v4 §66:
  five shapes, multi-week). Prose is carried verbatim for a human + summariser.
- **Using an LLM for any FACT the book states.** See THE CORRECTION.
