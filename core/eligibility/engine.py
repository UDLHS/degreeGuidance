"""Eligibility engine (Phase 6).

Deterministic. No LLM, ever (masterplan v4 §8.4). Runs the §8.1 core SQL with
bound parameters, applies three-state classification + confidence tiering, logs
an eligibility_audit row, and returns an EligibilityResponse.

Three states (§8.2):
  - eligible    : student z >= cutoff, no aptitude test required
  - conditional : student z >= cutoff, BUT requires_aptitude_test = TRUE
  - not_eligible: student z < cutoff OR stream mismatch -> filtered out by the
                  SQL, never returned.

Confidence tier (§8.3), comparing the year served against the most recent year
loaded in z_score_cutoffs (handoff correction #7):
  - current       : serving the freshest year we have (gap 0)
  - previous_year : serving a year 1 behind the freshest (gap 1)
  - estimated     : serving a year 2+ behind the freshest (gap >= 2)
With only year=2023 loaded, every response is 'current'.

Marginal flag (§8.3): student_margin <= 0.05 -> the cutoff could shift and flip
this result next year.
"""

from __future__ import annotations

import hashlib
import logging
import time
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.eligibility.arts_basket import check_arts_eligibility
from core.eligibility.subject_requirements import SubjectResult, evaluate_subject_rule
from core.models.eligibility import EligibilityAudit
from core.schemas.eligibility import (
    EligibilityRequest,
    EligibilityResponse,
    EligibilityResultItem,
)

ARTS_COURSE_NUMBER = "019"

logger = logging.getLogger(__name__)

# Within this z-score distance of the cutoff, flag the result as marginal.
MARGINAL_THRESHOLD = 0.05


class EligibilityInputError(ValueError):
    """A district_code or stream_code did not resolve to a known row.

    The router maps this to HTTP 422.
    """


# The §8.1 core query, verbatim, with bound parameters. The partial index
# idx_zscore_district_lookup (year, district_id, z_score) WHERE z_score IS NOT NULL
# is the hot path for the year/district/z_score filter.
#
# course_stream_cutoff_overrides: a handful of courses print ONE Uni-Code but
# have genuinely different cutoffs per stream (measured case: 107L, Food
# Business Management). For those, z_score_cutoffs.z_score is NULL and the
# real number lives in the override table keyed by the student's own stream;
# the LEFT JOIN + COALESCE make every other course's row (no override exists)
# behave exactly as before this table existed.
_CORE_QUERY = text(
    """
    SELECT
      zc.cutoff_id,
      zc.year,
      COALESCE(so.z_score, zc.z_score) AS cutoff_z_score,
      c.course_code,
      c.course_number,
      c.name_en                        AS course_name,
      c.duration_years,
      c.selection_basis,
      c.requires_aptitude_test,
      u.code                           AS university_code,
      u.name_en                        AS university_name,
      u.district_id                    AS university_district_id,
      ARRAY(
        SELECT m.code FROM course_mediums cm
        JOIN mediums m ON m.medium_id = cm.medium_id
        WHERE cm.course_code = c.course_code
      )                                AS available_mediums
    FROM z_score_cutoffs zc
    JOIN courses      c ON c.course_code   = zc.course_code
    JOIN universities u ON u.university_id = c.university_id
    LEFT JOIN course_stream_cutoff_overrides so
      ON  so.course_code  = zc.course_code
      AND so.district_id  = zc.district_id
      AND so.year         = zc.year
      AND so.stream_id    = :student_stream_id
    WHERE zc.year         = :exam_year
      AND zc.district_id  = :district_id
      AND COALESCE(so.z_score, zc.z_score) IS NOT NULL
      AND COALESCE(so.z_score, zc.z_score) <= :student_z_score
      AND c.is_active     = TRUE
      AND EXISTS (
        SELECT 1 FROM course_stream_eligibility cse
        WHERE cse.course_code = c.course_code
          AND cse.stream_id   = :student_stream_id
      )
    ORDER BY cutoff_z_score DESC
    """
)


async def _resolve_district_id(session: AsyncSession, code: str) -> int:
    row = (
        await session.execute(
            text("SELECT district_id FROM districts WHERE code = :code"),
            {"code": code},
        )
    ).first()
    if row is None:
        raise EligibilityInputError(f"Unknown district code: {code!r}")
    return int(row.district_id)


async def _resolve_stream_id(session: AsyncSession, code: str) -> int:
    row = (
        await session.execute(
            text("SELECT stream_id FROM streams WHERE code = :code"),
            {"code": code},
        )
    ).first()
    if row is None:
        raise EligibilityInputError(f"Unknown stream code: {code!r}")
    return int(row.stream_id)


async def _fetch_subject_rules(
    session: AsyncSession, course_numbers: set[str]
) -> dict[str, dict]:
    """Bulk-fetch baseline (exam_year IS NULL) subject_rule trees for the given
    course_numbers, in one query (avoids N+1 across a result set)."""
    if not course_numbers:
        return {}
    rows = (
        await session.execute(
            text(
                "SELECT course_number, subject_rule FROM course_requirements "
                "WHERE course_number = ANY(:numbers) AND exam_year IS NULL"
            ),
            {"numbers": list(course_numbers)},
        )
    ).all()
    return {r.course_number: r.subject_rule for r in rows}


def _passes_subject_requirement(
    course_number: str | None,
    subjects: list[SubjectResult],
    rules_by_number: dict[str, dict],
    stream_code: str | None,
) -> bool:
    """True if the course is ungated, or the student's subjects (and, where the
    rule needs it, their stream) satisfy its curated rule. False only when a
    rule exists and is NOT satisfied -- a course with no curated rule is always
    ungated by design (masterplan incremental-curation principle, see
    migration 24)."""
    if course_number == ARTS_COURSE_NUMBER:
        return check_arts_eligibility(subjects)
    rule = rules_by_number.get(course_number) if course_number else None
    if rule is None:
        return True
    return evaluate_subject_rule(rule, subjects, stream_code)


async def _get_max_year(session: AsyncSession) -> int | None:
    row = (
        await session.execute(text("SELECT MAX(year) AS max_year FROM z_score_cutoffs"))
    ).first()
    return int(row.max_year) if row and row.max_year is not None else None


def _confidence(max_year: int | None, used_year: int) -> tuple[str, str | None]:
    """Tier + optional caveat message based on how stale the served year is."""
    if max_year is None:
        return "current", None
    gap = max_year - used_year
    if gap <= 0:
        return "current", None
    if gap == 1:
        return "previous_year", "Based on last year's cutoffs; this year's may differ."
    return (
        "estimated",
        f"Based on cutoffs from {used_year}; the most recent data is "
        f"{gap} years newer and may differ.",
    )


async def evaluate_eligibility(
    session: AsyncSession, req: EligibilityRequest
) -> EligibilityResponse:
    """Evaluate which courses a student qualifies for, and log the query."""
    started = time.perf_counter()

    district_id = await _resolve_district_id(session, req.district_code)
    stream_id = await _resolve_stream_id(session, req.stream_code)

    max_year = await _get_max_year(session)
    # Default to the freshest year we have; if the caller named a year, honour it.
    used_year = req.exam_year if req.exam_year is not None else max_year
    if used_year is None:
        # z_score_cutoffs is empty (degenerate). Return an empty, honest result.
        used_year = req.exam_year or 0

    rows = (
        await session.execute(
            _CORE_QUERY,
            {
                "exam_year": used_year,
                "district_id": district_id,
                "student_z_score": Decimal(str(req.z_score)),
                "student_stream_id": stream_id,
            },
        )
    ).mappings().all()

    student_subjects = [SubjectResult(subject=s.subject, grade=s.grade) for s in req.subjects]
    course_numbers = {r["course_number"] for r in rows if r["course_number"]}
    rules_by_number = await _fetch_subject_rules(session, course_numbers)

    results: list[EligibilityResultItem] = []
    eligible_count = 0
    conditional_count = 0
    subject_filtered_count = 0

    for r in rows:
        if not _passes_subject_requirement(
            r["course_number"], student_subjects, rules_by_number, req.stream_code
        ):
            subject_filtered_count += 1
            continue

        cutoff = float(r["cutoff_z_score"])
        margin = round(req.z_score - cutoff, 4)
        conditional = bool(r["requires_aptitude_test"])
        if conditional:
            conditional_count += 1
        else:
            eligible_count += 1
        results.append(
            EligibilityResultItem(
                course_code=r["course_code"],
                course_number=r["course_number"],
                course_name=r["course_name"],
                university_code=r["university_code"],
                university_name=r["university_name"],
                university_district_id=int(r["university_district_id"]),
                duration_years=(
                    float(r["duration_years"]) if r["duration_years"] is not None else None
                ),
                cutoff_z_score=cutoff,
                student_margin=margin,
                selection_basis=r["selection_basis"],
                requires_aptitude_test=conditional,
                status="conditional" if conditional else "eligible",
                is_marginal=margin <= MARGINAL_THRESHOLD,
                available_mediums=list(r["available_mediums"] or []),
            )
        )

    tier, message = _confidence(max_year, used_year)

    response = EligibilityResponse(
        exam_year_used=used_year,
        confidence_tier=tier,
        confidence_message=message,
        student_z_score=req.z_score,
        district_code=req.district_code,
        stream_code=req.stream_code,
        eligible_count=eligible_count,
        conditional_count=conditional_count,
        total_count=len(results),
        subject_filtered_count=subject_filtered_count,
        results=results,
    )

    latency_ms = int((time.perf_counter() - started) * 1000)
    await _write_audit(session, req, district_id, stream_id, used_year, response, latency_ms)

    return response


async def _write_audit(
    session: AsyncSession,
    req: EligibilityRequest,
    district_id: int,
    stream_id: int,
    used_year: int,
    response: EligibilityResponse,
    latency_ms: int,
) -> None:
    """Persist one eligibility_audit row. Logging failure must not deny results."""
    raw = f"{req.z_score}|{district_id}|{stream_id}|{used_year}"
    request_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    audit = EligibilityAudit(
        request_hash=request_hash,
        user_id=None,  # no auth in Phase 6
        z_score=req.z_score,
        district_id=district_id,
        stream_id=stream_id,
        cutoff_year_used=used_year,
        eligible_count=response.eligible_count,
        conditional_count=response.conditional_count,
        confidence_tier=response.confidence_tier,
        result_payload=response.model_dump(mode="json"),
        latency_ms=latency_ms,
    )
    try:
        session.add(audit)
        await session.commit()
    except Exception:  # noqa: BLE001 - audit logging is best-effort
        await session.rollback()
        logger.warning("Failed to write eligibility_audit row", exc_info=True)
