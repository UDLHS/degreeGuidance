"""C2 PDF-extraction Arq job.

Wraps the EXISTING native PDF extractor (scripts/native_pdf_extractor) — it does
NOT reimplement extraction (locked decision: the pipeline already exists, don't
rebuild it). The extractor is synchronous and CPU-bound (pdfplumber), so it runs
in a worker thread via asyncio.to_thread to avoid blocking the Arq event loop.

Flow:
  1. Load course aliases from the DB (incl. the migration-17 unicode self-aliases
     that let the unicode-header CSV resolve through the Step 4 loader).
  2. Extract -> write a wide, unicode-header CSV to the ingestion work dir.
  3. Flip the ingestion_runs row to success (with counts) or failed (with the
     error on error_log). The uploaded PDF is removed; the reviewable CSV stays.

The admin then reviews the CSV (GET .../{run_id}/csv) and commits it via
POST .../{run_id}/promote, which runs the Step 4 loader.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from core.config import settings
from core.db import AsyncSessionLocal
from core.ingestion.handbook_diff import compute_handbook_diff, record_changes
from core.models import CourseAlias, IngestionRun
from scripts.native_pdf_extractor.extract_cutoffs import (
    extract_handbook,
    write_wide_csv,
)

logger = logging.getLogger(__name__)


def _extract_to_csv(
    pdf_path: str, aliases: dict[str, str], out_csv: str
) -> tuple[dict, int, int, list[int]]:
    """Synchronous, CPU-bound extraction — call via asyncio.to_thread.

    Returns the raw cutoffs dict too (course_code -> district -> z-score) so the
    diff stage can compare it against the DB without re-reading the CSV.
    """
    cutoffs, pages = extract_handbook(pdf_path, aliases, verbose=False)
    write_wide_csv(cutoffs, out_csv, header_format="unicode")
    courses = len(cutoffs)
    cells = sum(len(districts) for districts in cutoffs.values())
    return cutoffs, courses, cells, pages


async def extract_pdf_job(ctx, *, run_id: str, pdf_path: str, exam_year: int) -> dict:
    """Arq job: extract a handbook PDF into a reviewable CSV and update the run."""
    work_dir = Path(settings.ingestion_work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    out_csv = work_dir / f"{run_id}.csv"

    final_status = "failed"
    async with AsyncSessionLocal() as db:
        run = await db.get(IngestionRun, uuid.UUID(run_id))
        if run is None:
            logger.error("extract_pdf_job: ingestion run %s not found", run_id)
            return {"run_id": run_id, "status": "failed", "error": "run not found"}

        alias_rows = (await db.scalars(select(CourseAlias))).all()
        aliases = {a.alias_text: a.course_code for a in alias_rows}

        try:
            cutoffs, courses, cells, pages = await asyncio.to_thread(
                _extract_to_csv, pdf_path, aliases, str(out_csv)
            )
            if cells == 0:
                run.status = final_status = "failed"
                run.error_log = "Extraction produced no cutoff cells."
            else:
                run.status = final_status = "success"
                run.records_processed = cells
                run.records_failed = 0
                # Diff the extracted book against the live DB and stage the
                # change-set for admin review. A diff failure must NOT fail the
                # extraction — the CSV is already valid and promotable.
                change_note = ""
                try:
                    changes = await compute_handbook_diff(db, cutoffs, exam_year)
                    n = await record_changes(db, run.run_id, changes)
                    change_note = f"; {n} changes for review"
                except Exception as diff_exc:  # noqa: BLE001
                    logger.exception("diff stage failed for run %s", run_id)
                    change_note = f"; diff failed: {type(diff_exc).__name__}"
                run.notes = (
                    f"{courses} courses, {len(pages)} pages {pages}; "
                    f"CSV ready for review{change_note}"
                )
        except Exception as exc:  # noqa: BLE001 - record any failure on the run
            logger.exception("extract_pdf_job failed for run %s", run_id)
            run.status = final_status = "failed"
            run.error_log = f"{type(exc).__name__}: {exc}"
        finally:
            run.completed_at = datetime.now(timezone.utc)
            await db.commit()
            # The reviewable CSV is what matters now; drop the uploaded PDF.
            try:
                Path(pdf_path).unlink(missing_ok=True)
            except OSError:
                pass

    return {"run_id": run_id, "status": final_status}
