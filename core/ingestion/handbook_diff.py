"""Handbook diff — compare an extracted handbook against the live DB.

Given the native extractor's output (course_code -> district_name -> z-score
string, see scripts/native_pdf_extractor) and the exam year being ingested,
produce a list of reviewable change records:

- course_removed : an active course absent from the new book
- course_added   : an extracted Uni-Code with no course row at all
- cutoff_changed : a course whose z-scores moved vs the latest prior year

This is read-only against the DB; the caller persists the records as
HandbookChange rows tied to the ingestion run. Keeping *compute* and *persist*
separate makes the diff unit-testable without a worker or a run row.

The course-code set comes for free from the extractor's header row, so this
needs no new PDF parsing — it works off what the cutoff extractor already
produces (Phase A1).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# z-score moves at or above this are worth flagging; smaller deltas are rounding
# noise in a 4-dp value.
CUTOFF_EPSILON = 0.0001


@dataclass
class ChangeRecord:
    change_type: str
    course_code: str
    summary: str
    before_value: dict[str, Any] | None = None
    after_value: dict[str, Any] | None = None


def _parse_z(raw: str | None) -> float | None:
    """Parse an extracted cell into a float, or None for NQC / blank / garbage."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.upper() == "NQC":
        return None
    try:
        return float(s)
    except ValueError:
        return None


async def compute_handbook_diff(
    db: AsyncSession,
    extracted: dict[str, dict[str, str]],
    exam_year: int,
    present_in_book: set[str] | None = None,
) -> list[ChangeRecord]:
    """Diff the extracted handbook against the DB. Pure read; returns records.

    present_in_book — coverage safeguard (core.ingestion.book_search): codes of
    active courses found ANYWHERE in the whole book text. When provided, a
    course absent from the extracted grids but still present in the book is
    NOT flagged removed (it lives outside the cutoff tables — the
    007K/103D/104H/105L/140P false-positive class).
    """
    extracted_codes = {str(c).strip().upper() for c in extracted}
    # normalise the keys we look up cutoffs by, too
    extracted_norm = {str(c).strip().upper(): v for c, v in extracted.items()}

    course_rows = (
        await db.execute(
            text("SELECT course_code, name_en, is_active FROM courses")
        )
    ).mappings().all()
    db_codes = {r["course_code"] for r in course_rows}
    active_codes = {r["course_code"] for r in course_rows if r["is_active"]}
    name_by_code = {r["course_code"]: r["name_en"] for r in course_rows}

    changes: list[ChangeRecord] = []

    # --- Removed: active in DB, absent from the grids AND from the whole book ---
    for code in sorted(active_codes - extracted_codes):
        if present_in_book is not None and code in present_in_book:
            continue  # printed elsewhere in the book — not a removal
        where = (
            "absent from the cutoff tables and the rest of the book"
            if present_in_book is not None
            else "absent from the extracted cutoff tables (whole-book check not run)"
        )
        changes.append(
            ChangeRecord(
                change_type="course_removed",
                course_code=code,
                summary=(
                    f"{code} — \"{name_by_code[code]}\" is active in the DB but "
                    f"{where} in the {exam_year} handbook."
                ),
                before_value={"course_code": code, "name_en": name_by_code[code], "is_active": True},
                after_value=None,
            )
        )

    # --- Added: extracted code with no course row at all ---
    for code in sorted(extracted_codes - db_codes):
        cutoff_count = sum(1 for v in extracted_norm[code].values() if _parse_z(v) is not None)
        changes.append(
            ChangeRecord(
                change_type="course_added",
                course_code=code,
                summary=(
                    f"{code} — new in the {exam_year} handbook "
                    f"({cutoff_count} district cutoffs); no matching course in the DB."
                ),
                before_value=None,
                after_value={"course_code": code, "district_cutoff_count": cutoff_count},
            )
        )

    # --- Cutoff changes: codes present in both (and active) ---
    prior_year = (
        await db.execute(
            text("SELECT max(year) FROM z_score_cutoffs WHERE year < :y"),
            {"y": exam_year},
        )
    ).scalar()

    if prior_year is not None:
        district_rows = (
            await db.execute(text("SELECT district_id, upper(name_en) AS uname FROM districts"))
        ).mappings().all()
        name_to_id = {r["uname"]: r["district_id"] for r in district_rows}

        for code in sorted(extracted_codes & active_codes):
            old_rows = (
                await db.execute(
                    text(
                        "SELECT district_id, z_score FROM z_score_cutoffs "
                        "WHERE course_code = :c AND year = :y"
                    ),
                    {"c": code, "y": prior_year},
                )
            ).all()
            old_map = {r[0]: (float(r[1]) if r[1] is not None else None) for r in old_rows}

            deltas: list[dict[str, Any]] = []
            for dname, raw in extracted_norm[code].items():
                did = name_to_id.get(str(dname).strip().upper())
                if did is None:
                    continue
                new_v = _parse_z(raw)
                old_v = old_map.get(did)
                if new_v is None and old_v is None:
                    continue
                if old_v is None or new_v is None or abs(new_v - old_v) >= CUTOFF_EPSILON:
                    deltas.append({"district": str(dname).strip().upper(), "old": old_v, "new": new_v})

            if not deltas:
                continue
            numeric = [d for d in deltas if d["old"] is not None and d["new"] is not None]
            max_delta = max((abs(d["new"] - d["old"]) for d in numeric), default=0.0)
            changes.append(
                ChangeRecord(
                    change_type="cutoff_changed",
                    course_code=code,
                    summary=(
                        f"{code} — cutoffs changed in {len(deltas)}/{len(extracted_norm[code])} "
                        f"districts vs {prior_year} (max Δ {max_delta:.4f})."
                    ),
                    before_value={"year": prior_year},
                    after_value={
                        "year": exam_year,
                        "districts_changed": len(deltas),
                        "details": deltas,
                    },
                )
            )

    return changes


async def record_changes(
    db: AsyncSession, run_id: uuid.UUID, changes: list[ChangeRecord]
) -> int:
    """Persist computed changes as HandbookChange rows. Caller commits."""
    from core.models.cutoffs import HandbookChange

    for ch in changes:
        db.add(
            HandbookChange(
                run_id=run_id,
                change_type=ch.change_type,
                course_code=ch.course_code,
                summary=ch.summary,
                before_value=ch.before_value,
                after_value=ch.after_value,
            )
        )
    return len(changes)
