"""PDF-extraction Arq job — staged handbook pipeline (Phase 1).

Flow (docs/ADMIN_HANDBOOK_PIPELINE_DESIGN.md):
  1. Extract the raw cutoff grid with the format-agnostic extractor
     (auto-detected pages, or the run's confirmed cutoff_pages on re-extract).
  2. Consolidate page-spread repeats into logical columns.
  3. Build the whole-book presence index (the course_removed safeguard) —
     done here because the worker owns the PDF and the time budget.
  4. Compute deterministic mapping suggestions and persist one
     extraction_columns row per logical column (Gate-2 state).
  5. Park the run at:
       needs_mapping — grid extracted, columns await admin confirmation
       needs_pages   — nothing parsable found; admin must supply the range
       failed        — hard error (recorded on error_log)

The cutoff CSV is NOT written here any more: it is produced by the
mapping-confirm endpoint from admin-confirmed columns, then promoted through
the untouched Step-4 loader. The uploaded PDF is RETAINED — re-extraction
with a manual page range and the confirm stage both need it.

Stage inputs/outputs go through core/ingestion/artifact_store.py: the DB row
is the durable copy (the API and this worker are separate machines with
separate disks in production), the work-dir file just a cache.

The heavy pdfplumber work is synchronous and CPU-bound, so it runs in a
worker thread (asyncio.to_thread) to keep the Arq event loop responsive.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, text

from core.config import settings
from core.db import AsyncSessionLocal
from core.ingestion.artifact_store import artifact_path, put_artifact
from core.ingestion.book_search import build_book_text, present_courses
from core.ingestion.column_mapper import suggest_mappings
from core.ingestion.grid_extractor import (
    consolidate,
    extract_grid,
    parse_pages_spec,
)
from core.ingestion.unicode_section import BookMatcher, parse_unicode_section
from core.models import ExtractionColumn, IngestionRun

logger = logging.getLogger(__name__)


def _pages_to_spec(pages: list[int]) -> str:
    """[179,180,...,188] -> '179-188'; non-contiguous -> '150-156,179-188'."""
    if not pages:
        return ""
    parts: list[str] = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
            continue
        parts.append(f"{start}-{prev}" if prev > start else f"{start}")
        start = prev = p
    parts.append(f"{start}-{prev}" if prev > start else f"{start}")
    return ",".join(parts)


def _extract_and_index(pdf_path: str, pages: list[int] | None):
    """Synchronous CPU-bound stage: grid + consolidation + whole-book text +
    the book's own Uni-Code section (the authoritative name -> code table)."""
    extraction = extract_grid(pdf_path, pages)
    logical, conflict_warnings = consolidate(extraction)
    book_text = build_book_text(pdf_path) if logical else ""
    book_rows, book_warnings = parse_unicode_section(pdf_path) if logical else ([], [])
    return extraction, logical, conflict_warnings, book_text, book_rows, book_warnings


async def extract_pdf_job(
    ctx,
    *,
    run_id: str,
    pdf_path: str,
    exam_year: int,
    cutoff_pages: str | None = None,
) -> dict:
    Path(settings.ingestion_work_dir).mkdir(parents=True, exist_ok=True)

    final_status = "failed"
    async with AsyncSessionLocal() as db:
        run = await db.get(IngestionRun, uuid.UUID(run_id))
        if run is None:
            logger.error("extract_pdf_job: ingestion run %s not found", run_id)
            return {"run_id": run_id, "status": "failed", "error": "run not found"}

        try:
            # The upload may have landed on a different instance (split
            # API/worker services in production) — rematerialize the PDF from
            # the artifact store when the local work-dir copy is absent.
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                resolved = await artifact_path(db, run_id, "pdf")
                if resolved is None:
                    raise FileNotFoundError(
                        "uploaded PDF not found on this instance or in the "
                        "artifact store — upload the handbook again"
                    )
                pdf_file = resolved

            pages = parse_pages_spec(cutoff_pages) if cutoff_pages else None
            (
                extraction, logical, conflict_warnings,
                book_text, book_rows, book_warnings,
            ) = await asyncio.to_thread(_extract_and_index, str(pdf_file), pages)

            if not logical:
                run.status = final_status = "needs_pages"
                run.cutoff_pages = cutoff_pages
                run.error_log = None
                run.notes = (
                    "No parsable cutoff grid found"
                    + (f" in pages {cutoff_pages}" if cutoff_pages else " by auto-detection")
                    + " — supply the cutoff table page range and re-extract."
                    + (f" Warnings: {'; '.join(extraction.all_warnings()[:5])}"
                       if extraction.all_warnings() else "")
                )
            else:
                # whole-book presence set (course_removed safeguard)
                courses = (
                    await db.execute(
                        text("SELECT course_code, name_en FROM courses WHERE is_active")
                    )
                ).all()
                present = present_courses(book_text, [(c, n) for c, n in courses])
                await put_artifact(
                    db, run_id, "presence.json",
                    json.dumps(sorted(present)).encode("utf-8"),
                )

                # deterministic mapping suggestions -> extraction_columns rows
                # (the book's own Uni-Code section is the primary source)
                book = BookMatcher(book_rows) if book_rows else None
                suggestions = await suggest_mappings(db, logical, book=book)
                sug_by_key = {s.column_key: s for s in suggestions}
                await db.execute(
                    delete(ExtractionColumn).where(ExtractionColumn.run_id == run.run_id)
                )
                for col in logical:
                    s = sug_by_key[col.column_key]
                    exact = s.confidence is not None and s.confidence >= 0.999
                    db.add(ExtractionColumn(
                        run_id=run.run_id,
                        column_key=col.column_key,
                        page_number=col.page_number,
                        raw_label=col.raw_label or (col.code or ""),
                        markers=col.markers,
                        suggested_course_code=s.suggested_course_code,
                        suggestion_confidence=s.confidence,
                        # pre-fill exact hits (code / alias / book-section);
                        # admin still confirms at the gate
                        mapped_course_code=s.suggested_course_code if exact else None,
                    ))

                # grid artifact — the confirm endpoint builds the CSV from this;
                # the book's code table rides along for future course_added use
                artifact = {
                    "run_id": run_id,
                    "exam_year": exam_year,
                    "pages_processed": extraction.pages_processed,
                    "warnings": extraction.all_warnings() + conflict_warnings + book_warnings,
                    "book_code_rows": [
                        {
                            "code": r.code,
                            "course_name": r.course_name,
                            "university": r.university,
                            "page_number": r.page_number,
                        }
                        for r in book_rows
                    ],
                    "columns": [
                        {
                            "column_key": c.column_key,
                            "page_number": c.page_number,
                            "raw_label": c.raw_label,
                            "code": c.code,
                            "markers": c.markers,
                            "repeat_keys": c.repeat_keys,
                            "values": c.values,
                        }
                        for c in logical
                    ],
                }
                await put_artifact(
                    db, run_id, "grid.json", json.dumps(artifact).encode("utf-8")
                )

                cells = sum(
                    1 for c in logical for v in c.values.values() if v is not None
                )
                repeats = sum(len(c.repeat_keys) for c in logical)
                exact = sum(
                    1 for c in logical
                    if (sug_by_key[c.column_key].confidence or 0) >= 0.999
                )
                run.status = final_status = "needs_mapping"
                run.cutoff_pages = cutoff_pages or _pages_to_spec(extraction.pages_processed)
                run.records_processed = cells
                run.records_failed = 0
                run.error_log = None
                warn_note = (
                    f"; {len(conflict_warnings)} value-conflict warning(s)"
                    if conflict_warnings else ""
                )
                run.notes = (
                    f"{len(logical)} columns extracted from pages "
                    f"{run.cutoff_pages} ({repeats} spread-repeats collapsed); "
                    f"{exact}/{len(logical)} exact-match suggestions pre-filled "
                    f"({len(book_rows)} rows read from the book's Uni-Code section); "
                    f"{len(present)}/{len(courses)} active courses present in book"
                    f"{warn_note} — awaiting column mapping review"
                )
        except Exception as exc:  # noqa: BLE001 - record any failure on the run
            logger.exception("extract_pdf_job failed for run %s", run_id)
            run.status = final_status = "failed"
            run.error_log = f"{type(exc).__name__}: {exc}"
        finally:
            run.completed_at = datetime.now(timezone.utc)
            await db.commit()
            # NOTE: the PDF is intentionally retained — manual re-extraction
            # and the mapping/confirm stage need it.

    return {"run_id": run_id, "status": final_status}
