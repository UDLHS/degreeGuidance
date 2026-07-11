"""Step 4 — Z-score ingestion.

Takes a human-reviewed merged CSV (rows = districts, columns = course labels)
and inserts normalized rows into z_score_cutoffs.

Handles:
- District name normalization (case, whitespace, spaces↔underscores)
- Course alias lookup (via course_aliases.alias_text)
- NQC parsing → z_score=NULL, notes='NQC'
- Idempotent upsert via INSERT ... ON CONFLICT DO UPDATE
- Parse error logging to parse_errors table
- Per-run accounting in ingestion_runs

CLI:
    python -m apps.worker.jobs.ingest_zscores \\
        --csv data/test/sample_zscores_2023.csv \\
        --exam-year 2023 \\
        --triggered-by 'udula@dev'
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import AsyncSessionLocal
from core.ingestion.artifact_store import load_artifact
from core.models import (
    District,
    CourseAlias,
    CourseStreamCutoffOverride,
    Stream,
    UnmappedCutoff,
    ZScoreCutoff,
    IngestionRun,
    ParseError,
)


# Validation bounds
MIN_VALID_YEAR = 2010
MAX_VALID_YEAR = 2030
MIN_VALID_ZSCORE = -2.0
MAX_VALID_ZSCORE = 3.0

# asyncpg caps bind parameters at 32,767 per statement. A full handbook is
# ~6,600 rows x 5 params ≈ 33,000 — the single-statement upsert sat 142 params
# under the limit on the 2023 data and breaks as soon as the book grows (it did
# in 2025). Chunk well below the cap.
UPSERT_CHUNK_ROWS = 4000


def normalize_district_label(raw: str) -> str:
    """Convert 'Nuwara Eliya' → 'NUWARA_ELIYA' to match districts.code."""
    s = raw.strip().upper()
    s = re.sub(r"\s+", " ", s)  # collapse internal whitespace
    s = s.replace(" ", "_")
    return s


def parse_zscore_value(raw) -> tuple[Optional[float], Optional[str]]:
    """Return (value, note). value=None for NQC / unparseable / out-of-range."""
    s = str(raw).strip().upper()
    if s == "NQC":
        return None, "NQC"
    if s in ("", "-", "NAN", "NULL", "N/A"):
        return None, "MISSING"
    try:
        v = float(s)
    except ValueError:
        return None, f"UNPARSEABLE: {raw!r}"
    if v < MIN_VALID_ZSCORE or v > MAX_VALID_ZSCORE:
        return None, f"OUT_OF_RANGE: {v}"
    return v, None


async def cutoff_coverage_gaps(db, exam_year: int) -> list[str]:
    """Active catalog courses that received NO cutoff for exam_year.

    This is the safeguard against silent extractor drops / code-misreads: after a
    full-handbook ingest, every course in this list either legitimately had no
    intake that year (NQC) or is a misread that landed under the wrong code (as
    007K did when it was read as 006K). Either way it must be a conscious review
    decision, never an unnoticed gap. Surfaced on the ingestion run's notes.
    """
    rows = (
        await db.execute(
            text(
                "SELECT c.course_code FROM courses c "
                "WHERE c.is_active = TRUE AND NOT EXISTS ("
                "  SELECT 1 FROM z_score_cutoffs z "
                "  WHERE z.course_code = c.course_code AND z.year = :y) "
                "ORDER BY c.course_code"
            ),
            {"y": exam_year},
        )
    ).scalars().all()
    return list(rows)


async def ingest_zscores(
    csv_path: str,
    exam_year: int,
    triggered_by: str = "cli",
) -> dict:
    """Core ingestion logic. Returns summary dict.

    Raises:
        ValueError: invalid exam_year or empty CSV.
        FileNotFoundError: csv_path doesn't exist.
    """
    if not (MIN_VALID_YEAR <= exam_year <= MAX_VALID_YEAR):
        raise ValueError(
            f"exam_year {exam_year} out of valid range "
            f"({MIN_VALID_YEAR}-{MAX_VALID_YEAR})"
        )

    path = Path(csv_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    async with AsyncSessionLocal() as db:
        # Pre-load reference data
        district_rows = (await db.scalars(select(District))).all()
        districts_by_code = {d.code: d.district_id for d in district_rows}

        alias_rows = (await db.scalars(select(CourseAlias))).all()
        aliases_by_text = {a.alias_text: a.course_code for a in alias_rows}

        # Create run row
        run = IngestionRun(
            run_type="zscore",
            source_label=f"zscore_csv_year_{exam_year}",
            year=exam_year,
            status="running",
            triggered_by=triggered_by,
        )
        db.add(run)
        await db.flush()  # populates run.run_id
        run_id = run.run_id  # capture for use after commit

        processed = 0
        failed = 0
        upsert_rows: list[dict] = []
        parse_errors: list[ParseError] = []

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                raise ValueError(f"CSV is empty: {csv_path}")

            course_labels = headers[1:]  # first column is the district column

            for row_num, row in enumerate(reader, start=2):  # 1-indexed including header
                if not row or not row[0].strip():
                    continue

                raw_district = row[0]
                district_code = normalize_district_label(raw_district)
                district_id = districts_by_code.get(district_code)

                if district_id is None:
                    parse_errors.append(ParseError(
                        run_id=run_id,
                        source_label=run.source_label,
                        page_number=row_num,
                        raw_block=raw_district,
                        error_type="unknown_district",
                        error_message=f"District {raw_district!r} did not resolve to any code",
                    ))
                    failed += 1
                    continue

                for col_idx, raw_value in enumerate(row[1:]):
                    label = (course_labels[col_idx] if col_idx < len(course_labels) else "").strip()
                    if not label or label.startswith("_blank_"):
                        continue

                    course_code = aliases_by_text.get(label)
                    if course_code is None:
                        parse_errors.append(ParseError(
                            run_id=run_id,
                            source_label=run.source_label,
                            page_number=row_num,
                            raw_block=label,
                            error_type="unknown_course_alias",
                            error_message=f"Course label {label!r} not in course_aliases",
                        ))
                        failed += 1
                        continue

                    z_score, note = parse_zscore_value(raw_value)
                    upsert_rows.append({
                        "year": exam_year,
                        "course_code": course_code,
                        "district_id": district_id,
                        "z_score": z_score,
                        "notes": note,
                    })
                    processed += 1

        # Bulk upsert, chunked under asyncpg's 32,767-parameter cap
        for i in range(0, len(upsert_rows), UPSERT_CHUNK_ROWS):
            chunk = upsert_rows[i : i + UPSERT_CHUNK_ROWS]
            stmt = pg_insert(ZScoreCutoff.__table__).values(chunk)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_zscore_year_course_district",
                set_={
                    "z_score": stmt.excluded.z_score,
                    "notes": stmt.excluded.notes,
                },
            )
            await db.execute(stmt)

        # Add parse errors (if any)
        for pe in parse_errors:
            db.add(pe)

        # Coverage check (visible to the uncommitted upserts in this txn): flag
        # active courses that ended up with no cutoff for this year, for review.
        gaps = await cutoff_coverage_gaps(db, exam_year)

        # Finalize the run
        run.status = "partial" if failed > 0 else "success"
        run.completed_at = datetime.now(timezone.utc)
        run.records_processed = processed
        run.records_failed = failed
        run.notes = (
            f"coverage: {len(gaps)} active course(s) without cutoffs for {exam_year}"
            + (f" — review: {', '.join(gaps[:30])}" if gaps else "")
        )

        await db.commit()

        return {
            "run_id": str(run_id),
            "status": run.status,
            "processed": processed,
            "failed": failed,
        }


async def apply_stream_overrides(db: AsyncSession, run_id: str, exam_year: int) -> dict:
    """Apply a run's stream-variant columns (Gate 2's {run_id}.overrides.json,
    written by confirm_mapping when >1 confirmed column legitimately shares a
    course code via disjoint stream splits) into
    course_stream_cutoff_overrides, and annotate the affected z_score_cutoffs
    rows' notes with the per-stream breakdown.

    A no-op when the run has no such artifact -- true for the overwhelming
    majority of runs, since this only exists for courses like 107L (Food
    Business Management) whose handbook cutoff table carries different
    z-scores per stream under one Uni-Code. Call AFTER ingest_zscores() has
    written the run's normal CSV, so the base rows already exist to annotate.
    """
    raw = await load_artifact(db, run_id, "overrides.json")
    if raw is None:
        return {"rows_written": 0, "courses": 0}

    payload = json.loads(raw)
    columns = payload.get("columns", [])
    if not columns:
        return {"rows_written": 0, "courses": 0}

    district_rows = (await db.scalars(select(District))).all()
    district_id_by_code = {d.code: d.district_id for d in district_rows}
    stream_rows = (await db.scalars(select(Stream))).all()
    stream_id_by_code = {s.code: s.stream_id for s in stream_rows}

    override_rows: list[dict] = []
    # (course_code, district_id) -> ["STREAM_CODE: 1.2345", ...] for the notes summary
    summary: dict[tuple[str, int], list[str]] = {}

    for col in columns:
        course_code = col["course_code"]
        stream_codes = [s for s in (col.get("stream_codes") or []) if s in stream_id_by_code]
        values = col.get("values") or {}
        for raw_district, raw_value in values.items():
            district_id = district_id_by_code.get(normalize_district_label(raw_district))
            if district_id is None:
                continue  # unknown district text -- same tolerance as ingest_zscores itself
            z_score, note = parse_zscore_value(raw_value)
            for stream_code in stream_codes:
                override_rows.append({
                    "year": exam_year,
                    "course_code": course_code,
                    "district_id": district_id,
                    "stream_id": stream_id_by_code[stream_code],
                    "z_score": z_score,
                    "notes": note,
                })
            label = "/".join(stream_codes) if stream_codes else "?"
            display = f"{z_score:.4f}" if z_score is not None else (note or "—")
            summary.setdefault((course_code, district_id), []).append(f"{label}: {display}")

    if override_rows:
        stmt = pg_insert(CourseStreamCutoffOverride.__table__).values(override_rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_stream_override_year_course_district_stream",
            set_={"z_score": stmt.excluded.z_score, "notes": stmt.excluded.notes},
        )
        await db.execute(stmt)

    # Annotate the base row so the admin matrix's hover-note shows the
    # per-stream breakdown instead of a bare blank cell (its own z_score stays
    # NULL -- no single number is honest for these courses).
    for (course_code, district_id), fragments in summary.items():
        note_text = "Stream-specific cutoffs — " + "; ".join(fragments)
        await db.execute(
            text(
                "UPDATE z_score_cutoffs SET notes = :note "
                "WHERE course_code = :c AND district_id = :d AND year = :y"
            ),
            {"note": note_text, "c": course_code, "d": district_id, "y": exam_year},
        )

    await db.commit()
    return {"rows_written": len(override_rows), "courses": len({c for c, _ in summary})}


async def apply_unmapped_cutoffs(db: AsyncSession, run_id: str, exam_year: int) -> dict:
    """Apply a run's codeless columns (Gate 2's {run_id}.unmapped.json — columns
    with real z-scores but NO Uni-Code in the book) into unmapped_cutoffs,
    keyed by the printed label instead of a course code. A no-op when the run
    has no such artifact. Never touches z_score_cutoffs. Call at promote, so
    codeless data goes live alongside the normal cutoffs."""
    raw = await load_artifact(db, run_id, "unmapped.json")
    if raw is None:
        return {"rows_written": 0, "columns": 0}

    payload = json.loads(raw)
    columns = payload.get("columns", [])
    if not columns:
        return {"rows_written": 0, "columns": 0}

    district_rows = (await db.scalars(select(District))).all()
    district_id_by_code = {d.code: d.district_id for d in district_rows}

    rows: list[dict] = []
    for col in columns:
        raw_label = col["raw_label"]
        for raw_district, raw_value in (col.get("values") or {}).items():
            district_id = district_id_by_code.get(normalize_district_label(raw_district))
            if district_id is None:
                continue
            z_score, note = parse_zscore_value(raw_value)
            rows.append({
                "run_id": run_id,
                "year": exam_year,
                "raw_label": raw_label,
                "course_name": col.get("course_name"),
                "university": col.get("university"),
                "district_id": district_id,
                "z_score": z_score,
                "notes": note,
            })

    if rows:
        stmt = pg_insert(UnmappedCutoff.__table__).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_unmapped_year_label_district",
            set_={
                "z_score": stmt.excluded.z_score,
                "notes": stmt.excluded.notes,
                "run_id": stmt.excluded.run_id,
                "course_name": stmt.excluded.course_name,
                "university": stmt.excluded.university,
            },
        )
        await db.execute(stmt)
        await db.commit()
    return {"rows_written": len(rows), "columns": len({c["raw_label"] for c in columns})}


# Arq worker job wrapper (used by admin UI in Week 2)
async def ingest_zscores_job(ctx, csv_path: str, exam_year: int, admin_user_id: str):
    return await ingest_zscores(csv_path, exam_year, f"admin:{admin_user_id}")


# CLI entry point
def main():
    parser = argparse.ArgumentParser(description="Step 4 z-score ingestion")
    parser.add_argument("--csv", required=True, help="Path to merged CSV")
    parser.add_argument(
        "--exam-year",
        type=int,
        required=True,
        help="A/L exam year (e.g., 2023 for 2024/2025 handbook data)",
    )
    parser.add_argument("--triggered-by", default="cli", help="Caller identifier")
    args = parser.parse_args()

    try:
        result = asyncio.run(
            ingest_zscores(args.csv, args.exam_year, args.triggered_by)
        )
        print("\nIngestion complete:")
        print(f"  Run ID:    {result['run_id']}")
        print(f"  Status:    {result['status']}")
        print(f"  Processed: {result['processed']}")
        print(f"  Failed:    {result['failed']}")
        return 0 if result["status"] in ("success", "partial") else 1
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
