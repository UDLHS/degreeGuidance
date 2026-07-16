"""Factsheet-draft generation job (Phase 9.4 — decisions D3/D4).

Writes a factsheet DRAFT for one course of study into factsheet_drafts — never
into factsheets. The index job reads the factsheets table and nothing else, so
nothing written here can reach the AI advisor until an admin approves it
(admin_factsheets' approve endpoint copies the text across through the same
versioned/audited path as a hand edit).

Source order is the law of the phase (D3):

  1. THE BOOK (authoritative): the extraction job's course_details.json
     artifact — name, streams, proposed intake, prerequisite prose VERBATIM,
     page number. Facts are READ from the book, never inferred; the LLM's only
     job is prose (see docs/PHASE9_NEW_COURSE_AGENT_PLAN.md, "THE CORRECTION").
  2. THE CATALOG (trustworthy): course names, Uni-Codes, universities,
     eligible streams, aptitude flag from the live DB.
  3. THE WEB (background colour only): DuckDuckGo snippets for careers and
     curriculum texture. A web failure degrades to book+catalog facts — it is
     recorded in provenance, and never fails the job.

Every draft row carries provenance (run, book page, streams as the book states
them, web-result count, model) so the reviewer can check each claim against
its source.

Failure is loud: any error lands on the draft row as status='failed' with the
message, so the admin sees "generation failed: …" instead of nothing.

The blocking work (DDG, Gemini) runs in a worker thread to keep the Arq event
loop responsive, mirroring extract_pdf.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone

from sqlalchemy import text

from core.config import settings
from core.db import AsyncSessionLocal
from core.ingestion.artifact_store import load_artifact
from core.ingestion.course_details import BookCourseDetail, details_from_artifact
from core.models.rag import FactsheetDraft

logger = logging.getLogger(__name__)

#: seconds between DDG queries — polite, and mirrors scripts/generate_factsheets.py
DDG_DELAY = 2.0
#: Gemini 429 retries: 60s, 120s, 180s (the Arq job budget absorbs this)
MAX_RETRIES = 3

#: Section structure kept IDENTICAL to scripts/generate_factsheets.py (the
#: bulk seed that wrote the existing 129) so machine drafts read like the rest
#: of the library and chunk the same way (## headings) for the index job.
FACTSHEET_TEMPLATE = """\
You are writing a factsheet for a degree guidance system used by Sri Lankan A/L students
choosing their university degree. The factsheet must be accurate, practical, and Sri Lanka-specific.

Write a factsheet for the following degree programme using EXACTLY this markdown structure.
Do not add or remove sections. Do not include placeholder text — every section must have real content.

---

# {course_name}
**Course Number:** {course_number}
**Degree:** [Full official degree name, e.g. "Bachelor of Science (Honours) in ..."]
**Duration:** [e.g. "3 years" or "4 years"]
**Entry Stream:** [A/L stream(s) accepted, e.g. "Physical Science, Biological Science"]
**Available at:** [List each university with its course code, e.g. "University of Kelaniya (119D)"]

---

## Overview

[2-3 paragraphs. Explain what this degree is, why it matters in Sri Lanka, what the industry
or sector looks like locally, and what makes this particular university/faculty notable.
Be specific — mention actual Sri Lankan institutions, industries, and context.]

---

## What You Will Study

[Year-by-year curriculum breakdown. Use bold headings for each year.
Include all major subject areas, specializations (if any), and final year project/research.
If there are tracks or specializations students choose between, list them clearly with what
each covers. Be specific about the academic content — not just vague subject names.]

---

## Career Paths in Sri Lanka

[Bullet points. Each bullet = one career pathway with:
- The role/sector
- Actual Sri Lankan employers or organisations in that sector
- What the day-to-day work involves
Include at least 5-6 distinct pathways. Include postgraduate study options.]

---

## Entry Requirements

[A/L stream, required subjects, any aptitude tests, language of instruction,
physical requirements if any (e.g. Nursing). Mention Z-score competitiveness
in general terms without giving specific numbers — those come from the database.]

---

## Differences Between Universities

[Only include this section if the programme is offered at more than one university.
Compare the universities on: faculty size, specializations offered, research focus,
industry links, location advantages, and any unique features.]

---

## Special Notes

[Any important details not covered above: professional body recognition (IESL, SLMC, ACCA etc.),
registration or licensing requirements after graduation, overseas employment demand,
postgraduate conversion pathways, medium of instruction, or anything else a student
making a life decision should know.]

---

Ground every claim in the sources below, in this order of authority:

1. OFFICIAL UGC HANDBOOK FACTS — authoritative. Copy them faithfully. If any
   other source contradicts them, the handbook wins. Quote the entry
   requirements essentially verbatim; do not paraphrase eligibility rules into
   something the handbook does not say.
2. CATALOG FACTS — from the live database; trustworthy.
3. WEB SEARCH RESULTS — background colour for careers and curriculum only. If
   they conflict with 1 or 2, ignore them. Never copy numbers from them.

If a fact appears in none of the sources, write around it rather than guessing.
Never invent intake numbers, Z-scores, fees, dates, or statistics.

COURSE: {course_name} (Number: {course_number})

OFFICIAL UGC HANDBOOK FACTS:
{book_facts}

CATALOG FACTS:
{db_facts}

WEB SEARCH RESULTS:
{web_context}

Write only the factsheet markdown. No preamble, no explanation, no sign-off.
"""

_STREAM_LABELS = {
    "ARTS": "Arts",
    "COMMERCE": "Commerce",
    "BIO_SCIENCE": "Biological Science",
    "PHYSICAL_SCIENCE": "Physical Science",
    "ENGINEERING_TECH": "Engineering Technology",
    "BIOSYSTEMS_TECH": "Biosystems Technology",
}


def _stream_names(codes: list[str]) -> str:
    return ", ".join(_STREAM_LABELS.get(c, c) for c in codes)


async def _db_facts(session, course_number: str) -> dict | None:
    """What the live catalog knows about this course of study. None = unknown
    course number (the job then fails loud rather than writing fiction)."""
    rows = (
        await session.execute(
            text(
                "SELECT c.course_code, c.name_en, u.name_en AS university, "
                "       c.requires_aptitude_test, "
                "       (SELECT string_agg(DISTINCT s.code, ',') "
                "          FROM course_stream_eligibility cse "
                "          JOIN streams s ON s.stream_id = cse.stream_id "
                "         WHERE cse.course_code = c.course_code) AS streams "
                "FROM courses c JOIN universities u ON u.university_id = c.university_id "
                "WHERE c.course_number = :cn AND c.is_active "
                "ORDER BY c.course_code"
            ),
            {"cn": course_number},
        )
    ).all()
    if not rows:
        return None
    streams: set[str] = set()
    for r in rows:
        streams.update(s for s in (r.streams or "").split(",") if s)
    return {
        "name": rows[0].name_en.split("(")[0].strip(),
        "offerings": [
            {"course_code": r.course_code, "university": r.university} for r in rows
        ],
        "stream_codes": sorted(streams),
        "requires_aptitude_test": any(r.requires_aptitude_test for r in rows),
    }


async def _book_detail(
    session, course_number: str, run_id: str | None
) -> tuple[BookCourseDetail | None, str | None]:
    """The book's statement about this course, from the given run's
    course_details.json artifact — or the newest run that has one. Returns
    (detail, run_id_used). (None, None) simply means "no book has been read";
    the draft then says so in provenance instead of pretending."""
    if run_id is None:
        row = (
            await session.execute(
                text(
                    "SELECT ir.run_id FROM ingestion_runs ir "
                    "JOIN ingestion_artifacts ia ON ia.run_id = ir.run_id "
                    "WHERE ia.kind = 'course_details.json' "
                    "ORDER BY ir.started_at DESC LIMIT 1"
                )
            )
        ).first()
        run_id = str(row.run_id) if row else None
    if run_id is None:
        return None, None
    raw = await load_artifact(session, run_id, "course_details.json")
    if raw is None:
        return None, run_id
    details = details_from_artifact(json.loads(raw))
    return details.get(course_number), run_id


def _format_book_facts(detail: BookCourseDetail | None) -> str:
    if detail is None:
        return (
            "(no ingested handbook mentions this course — rely on CATALOG FACTS "
            "and write nothing the catalog does not support)"
        )
    lines = [f"Course name as printed: {detail.name or '(not stated)'}"]
    if detail.stream_codes:
        stated = "states" if detail.streams_are_stated else "suggests (prose)"
        lines.append(f"Eligible streams the book {stated}: {_stream_names(detail.stream_codes)}")
    if detail.streams_may_be_incomplete:
        lines.append(
            "NOTE: the book also grants entry by subject list without naming a "
            "stream, so the stream list above may be incomplete — do not present "
            "it as exhaustive."
        )
    if detail.proposed_intake is not None:
        lines.append(f"Proposed intake: {detail.proposed_intake}")
    if detail.page_number is not None:
        lines.append(f"Handbook page: {detail.page_number}")
    if detail.requirements_text:
        lines.append(
            "Minimum eligibility requirements, VERBATIM from the handbook:\n"
            + detail.requirements_text
        )
    return "\n".join(lines)


def _format_db_facts(facts: dict) -> str:
    lines = [
        "Offered at: "
        + "; ".join(f"{o['university']} ({o['course_code']})" for o in facts["offerings"]),
    ]
    if facts["stream_codes"]:
        lines.append(f"Eligible streams in the catalog: {_stream_names(facts['stream_codes'])}")
    if facts["requires_aptitude_test"]:
        lines.append("Requires a practical/aptitude test conducted by the university.")
    return "\n".join(lines)


def _web_search(course_name: str, university: str) -> list[str]:
    """DDG snippets — blocking; call via asyncio.to_thread. Raises on total
    failure so the caller can record the degradation in provenance."""
    from ddgs import DDGS

    queries = [
        f'"{course_name}" degree Sri Lanka curriculum specializations duration',
        f'"{course_name}" graduates Sri Lanka careers jobs {university}',
    ]
    snippets: list[str] = []
    for i, query in enumerate(queries):
        with DDGS(timeout=15) as ddgs:
            for r in list(ddgs.text(query, max_results=5)):
                snippets.append(
                    f"[{r.get('title', '')}]\n{r.get('body', '')}\nURL: {r.get('href', '')}"
                )
        if i < len(queries) - 1:
            time.sleep(DDG_DELAY)
    return snippets[:8]


def _generate(prompt: str) -> str:
    """One Gemini call with 429 backoff — blocking; call via asyncio.to_thread."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=settings.gemini_chat_model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=4096),
            )
            content = (response.text or "").strip()
            if not content:
                raise RuntimeError("Gemini returned an empty draft")
            return content
        except Exception as exc:  # noqa: BLE001 - classify for retry below
            last_err = exc
            msg = str(exc)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                time.sleep(60 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"Gemini rate-limited after {MAX_RETRIES} retries: {last_err}")


async def _write_row(
    session, course_number: str, *, status: str, content: str | None = None,
    error: str | None = None, provenance: dict | None = None,
) -> None:
    row = await session.get(FactsheetDraft, course_number)
    if row is None:
        row = FactsheetDraft(course_number=course_number)
        session.add(row)
    row.status = status
    row.content = content
    row.error = error
    row.provenance = provenance
    row.updated_at = datetime.now(timezone.utc)
    await session.commit()


async def generate_factsheet_draft_job(
    ctx, course_number: str, run_id: str | None = None
) -> dict:
    """Arq entrypoint: assemble facts → write prose → land it as a draft."""
    async with AsyncSessionLocal() as session:
        try:
            facts = await _db_facts(session, course_number)
            if facts is None:
                raise ValueError(
                    f"course number {course_number!r} has no active courses in the catalog"
                )
            detail, book_run_id = await _book_detail(session, course_number, run_id)

            web_note = None
            snippets: list[str] = []
            try:
                snippets = await asyncio.to_thread(
                    _web_search, facts["name"], facts["offerings"][0]["university"]
                )
            except Exception as exc:  # noqa: BLE001 - degrade, never fail the draft
                web_note = f"web search unavailable ({type(exc).__name__}); draft is book+catalog only"
                logger.warning("web enrichment failed for %s: %s", course_number, exc)
            web_context = (
                "\n\n---\n\n".join(snippets)
                if snippets
                else "(no web results — use only the handbook and catalog facts)"
            )

            prompt = FACTSHEET_TEMPLATE.format(
                course_name=facts["name"],
                course_number=course_number,
                book_facts=_format_book_facts(detail),
                db_facts=_format_db_facts(facts),
                web_context=web_context,
            )
            content = await asyncio.to_thread(_generate, prompt)

            provenance = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": settings.gemini_chat_model,
                "run_id": book_run_id,
                "book_found": detail is not None,
                "book_page": detail.page_number if detail else None,
                "book_streams": detail.stream_codes if detail else [],
                "book_streams_are_stated": detail.streams_are_stated if detail else False,
                "book_streams_may_be_incomplete": (
                    detail.streams_may_be_incomplete if detail else False
                ),
                "proposed_intake": detail.proposed_intake if detail else None,
                "web_results": len(snippets),
                **({"web_note": web_note} if web_note else {}),
            }
            await _write_row(
                session, course_number,
                status="ready", content=content, provenance=provenance,
            )
            return {"course_number": course_number, "status": "ready", "chars": len(content)}
        except Exception as exc:  # noqa: BLE001 - fail LOUD on the row, not silently
            logger.exception("factsheet draft generation failed for %s", course_number)
            await session.rollback()
            await _write_row(
                session, course_number,
                status="failed", error=f"{type(exc).__name__}: {exc}",
            )
            return {"course_number": course_number, "status": "failed"}
