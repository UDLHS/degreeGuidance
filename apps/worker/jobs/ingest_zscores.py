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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.db import AsyncSessionLocal
from core.models import District, CourseAlias, ZScoreCutoff, IngestionRun, ParseError


# Validation bounds
MIN_VALID_YEAR = 2010
MAX_VALID_YEAR = 2030
MIN_VALID_ZSCORE = -2.0
MAX_VALID_ZSCORE = 3.0


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

        # Bulk upsert in a single statement
        if upsert_rows:
            stmt = pg_insert(ZScoreCutoff.__table__).values(upsert_rows)
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

        # Finalize the run
        run.status = "partial" if failed > 0 else "success"
        run.completed_at = datetime.now(timezone.utc)
        run.records_processed = processed
        run.records_failed = failed

        await db.commit()

        return {
            "run_id": str(run_id),
            "status": run.status,
            "processed": processed,
            "failed": failed,
        }


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
