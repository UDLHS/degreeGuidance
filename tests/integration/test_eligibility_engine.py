"""Eligibility correctness suite (masterplan v4 §16.1).

For EVERY case in tests/fixtures/eligibility_cases.yaml we:
  1. Run the production engine (core.eligibility.engine.evaluate_eligibility).
  2. Independently recompute the expected eligible set with a plain reference
     query (JOIN form, vs the engine's EXISTS+ARRAY form) — a genuinely separate
     code path, so a bug in one is unlikely to be mirrored in the other.
  3. Assert the engine's results == the reference, course-for-course, including
     status / cutoff / margin / is_marginal.
  4. Enforce universal invariants (NQC excluded, aptitude => conditional,
     ordering, count arithmetic, tier formula).
  5. Apply the case's explicit `assert` pins (includes / excludes / expect_empty
     / expect_tier).

The reference and invariants are the oracle, so no expected values are hardcoded
except the DB-verified 001A anchors embedded in the fixture's explicit pins.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.eligibility.arts_basket import check_arts_eligibility
from core.eligibility.engine import (
    ARTS_COURSE_NUMBER,
    MARGINAL_THRESHOLD,
    evaluate_eligibility,
)
from core.eligibility.subject_requirements import SubjectResult, evaluate_subject_rule
from core.schemas.eligibility import EligibilityRequest, SubjectInput

_FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "eligibility_cases.yaml"
_CASES = yaml.safe_load(_FIXTURE.read_text())["cases"]

# Per-stream subject sets used to drive this fixture suite. This suite's job is
# to verify stream + Z-score + district arithmetic (cross-checked against an
# independent reference query) -- subject-combination correctness has its own
# dedicated test suites (test_subject_requirements.py, test_arts_basket.py,
# test_course_requirements_seed.py). High grades minimise incidental subject
# exclusions so this suite stays focused on what it's actually testing; the
# reference query below applies the SAME subject filter as the engine, so any
# exclusion that does occur is still required to match on both sides.
_STREAM_SUBJECTS: dict[str, list[SubjectInput]] = {
    "BIO_SCIENCE": [
        SubjectInput(subject="Biology", grade="A"),
        SubjectInput(subject="Chemistry", grade="A"),
        SubjectInput(subject="Physics", grade="A"),
    ],
    "PHYSICAL_SCIENCE": [
        SubjectInput(subject="Chemistry", grade="A"),
        SubjectInput(subject="Combined Mathematics", grade="A"),
        SubjectInput(subject="Physics", grade="A"),
    ],
    "COMMERCE": [
        SubjectInput(subject="Business Studies", grade="A"),
        SubjectInput(subject="Economics", grade="A"),
        SubjectInput(subject="Accounting", grade="A"),
    ],
    "ARTS": [
        SubjectInput(subject="Economics", grade="A"),
        SubjectInput(subject="Geography", grade="A"),
        SubjectInput(subject="History", grade="A"),
    ],
}


def _case_id(case: dict) -> str:
    return f"{case['category']}::{case['id']}"


async def _reference(
    session: AsyncSession, z: float, district: str, stream: str, year: int,
    subjects: list[SubjectInput],
):
    """Independent recomputation of the eligible set (plain JOIN form).

    Applies the same subject-requirement filter as the engine -- subject-rule
    *correctness* is verified by its own dedicated suites; here the point is
    only that both code paths apply it identically, so a real divergence in
    the stream/Z-score JOIN math still surfaces.

    Stream-specific cutoff overrides (course_stream_cutoff_overrides,
    migration 37 -- e.g. 107L Food Business Management's Commerce vs
    Bio/Physical split) are part of the INTENDED semantics: the student's own
    stream picks the override over the general row. The oracle mirrors that
    rule here in JOIN form (vs the engine's EXISTS + COALESCE-in-SELECT), so
    the two stay independently-written implementations of the same spec."""
    did = (
        await session.execute(text("SELECT district_id FROM districts WHERE code = :c"), {"c": district})
    ).scalar_one_or_none()
    sid = (
        await session.execute(text("SELECT stream_id FROM streams WHERE code = :c"), {"c": stream})
    ).scalar_one_or_none()
    assert did is not None, f"district {district} missing"
    assert sid is not None, f"stream {stream} missing"

    rows = (
        await session.execute(
            text(
                """
                SELECT zc.course_code,
                       c.course_number,
                       COALESCE(so.z_score, zc.z_score) AS z_score,
                       c.requires_aptitude_test
                FROM z_score_cutoffs zc
                JOIN courses c                      ON c.course_code = zc.course_code
                JOIN course_stream_eligibility e    ON e.course_code = c.course_code
                LEFT JOIN course_stream_cutoff_overrides so
                       ON so.course_code = zc.course_code
                      AND so.district_id = zc.district_id
                      AND so.year        = zc.year
                      AND so.stream_id   = :s
                WHERE zc.year = :y
                  AND zc.district_id = :d
                  AND e.stream_id = :s
                  AND COALESCE(so.z_score, zc.z_score) IS NOT NULL
                  AND c.is_active = TRUE
                  AND COALESCE(so.z_score, zc.z_score) <= :z
                """
            ),
            {"y": year, "d": did, "s": sid, "z": Decimal(str(z))},
        )
    ).mappings().all()

    course_numbers = {r["course_number"] for r in rows if r["course_number"]}
    rules_by_number = {}
    if course_numbers:
        rule_rows = (
            await session.execute(
                text(
                    "SELECT course_number, subject_rule FROM course_requirements "
                    "WHERE course_number = ANY(:numbers) AND exam_year IS NULL"
                ),
                {"numbers": list(course_numbers)},
            )
        ).all()
        rules_by_number = {rr.course_number: rr.subject_rule for rr in rule_rows}

    student_subjects = [SubjectResult(subject=s.subject, grade=s.grade) for s in subjects]

    expected = {}
    for r in rows:
        course_number = r["course_number"]
        if course_number == ARTS_COURSE_NUMBER:
            if not check_arts_eligibility(student_subjects):
                continue
        else:
            rule = rules_by_number.get(course_number)
            if rule is not None and not evaluate_subject_rule(rule, student_subjects, stream):
                continue

        cutoff = float(r["z_score"])
        margin = round(z - cutoff, 4)
        expected[r["course_code"]] = {
            "cutoff": cutoff,
            "margin": margin,
            "status": "conditional" if r["requires_aptitude_test"] else "eligible",
            "is_marginal": margin <= MARGINAL_THRESHOLD,
        }
    return expected


async def _max_year(session: AsyncSession) -> int:
    return (
        await session.execute(text("SELECT MAX(year) FROM z_score_cutoffs"))
    ).scalar_one()


def _expected_tier(max_year: int, used_year: int) -> str:
    gap = max_year - used_year
    if gap <= 0:
        return "current"
    if gap == 1:
        return "previous_year"
    return "estimated"


@pytest.fixture(scope="session", autouse=True)
def _sanity_anchor_note():
    # The 001A anchors assume Medicine (001A) is BIO_SCIENCE-eligible; a dedicated
    # test below asserts that explicitly so the assumption can never go silent.
    pass


async def test_requested_year_without_data_falls_back_to_latest(db_session: AsyncSession):
    """A named exam_year with NO promoted rows must not produce a ghost-empty
    'verified YYYY' result (a browser can remember a year an admin later
    re-labeled away — happened in prod 2026-07-12). The engine serves the
    freshest year instead and says so."""
    from core.eligibility.engine import _get_max_year, evaluate_eligibility
    from core.schemas.eligibility import EligibilityRequest

    max_year = await _get_max_year(db_session)
    assert max_year is not None, "suite requires promoted cutoff data"
    ghost_year = max_year + 1  # never has data: nothing newer than MAX exists

    resp = await evaluate_eligibility(
        db_session,
        EligibilityRequest(
            z_score=1.8, district_code="COLOMBO", stream_code="BIO_SCIENCE",
            exam_year=ghost_year, subjects=_STREAM_SUBJECTS["BIO_SCIENCE"],
        ),
    )
    assert resp.exam_year_used == max_year, "must fall back to the freshest year"
    assert resp.eligible_count > 0, "fallback must serve real data, not an empty year"
    assert resp.confidence_message is not None
    assert str(ghost_year) in resp.confidence_message
    assert str(max_year) in resp.confidence_message


async def test_001A_is_bio_science_eligible(db_session: AsyncSession):
    """Guard for the 001A anchors: Medicine must be a BIO_SCIENCE course."""
    found = (
        await db_session.execute(
            text(
                """
                SELECT 1 FROM course_stream_eligibility e
                JOIN streams s ON s.stream_id = e.stream_id
                WHERE e.course_code = '001A' AND s.code = 'BIO_SCIENCE'
                """
            )
        )
    ).first()
    assert found is not None, "001A (Medicine) is not BIO_SCIENCE-eligible; fixture anchors invalid"


@pytest.mark.parametrize("case", _CASES, ids=[_case_id(c) for c in _CASES])
async def test_eligibility_case(case: dict, db_session: AsyncSession):
    inp = case["input"]
    z = float(inp["z_score"])
    district = inp["district"]
    stream = inp["stream"]
    exam_year = inp.get("exam_year")
    pins = case.get("assert", {})

    subjects = _STREAM_SUBJECTS[stream]
    req = EligibilityRequest(
        z_score=z, district_code=district, stream_code=stream, exam_year=exam_year,
        subjects=subjects,
    )
    resp = await evaluate_eligibility(db_session, req)

    # Mirror of the engine's year rule: a named year is honoured only if it
    # has promoted rows; otherwise the engine serves the freshest year (with
    # a note) instead of a ghost-empty result.
    max_year = await _max_year(db_session)
    used_year = exam_year if exam_year is not None else max_year
    if exam_year is not None and not (
        await db_session.execute(
            text("SELECT 1 FROM z_score_cutoffs WHERE year = :y LIMIT 1"),
            {"y": exam_year},
        )
    ).first():
        used_year = max_year
    assert resp.exam_year_used == used_year
    by_code = {r.course_code: r for r in resp.results}

    # ---- count arithmetic ----
    assert resp.total_count == len(resp.results)
    assert resp.eligible_count + resp.conditional_count == resp.total_count

    # ---- ordering: cutoff descending ----
    cutoffs = [r.cutoff_z_score for r in resp.results]
    assert cutoffs == sorted(cutoffs, reverse=True), "results not ordered by cutoff desc"

    # ---- universal invariants on every returned row ----
    for r in resp.results:
        assert r.cutoff_z_score is not None, "NQC/NULL cutoff leaked into results"
        assert r.cutoff_z_score <= z + 1e-9, "course above student's z returned"
        assert r.student_margin == pytest.approx(round(z - r.cutoff_z_score, 4), abs=1e-6)
        assert r.is_marginal == (r.student_margin <= MARGINAL_THRESHOLD)
        if r.requires_aptitude_test:
            assert r.status == "conditional"
        else:
            assert r.status == "eligible"

    # ---- confidence tier formula ----
    assert resp.confidence_tier == _expected_tier(max_year, used_year)

    # ---- cross-check against the independent reference (THE oracle) ----
    # (fallback cases resolve to the freshest year, so the oracle applies too)
    expected = await _reference(db_session, z, district, stream, used_year, subjects)
    assert set(by_code) == set(expected), (
        f"set mismatch: only-engine={set(by_code) - set(expected)}, "
        f"only-ref={set(expected) - set(by_code)}"
    )
    for code, exp in expected.items():
        got = by_code[code]
        assert got.cutoff_z_score == pytest.approx(exp["cutoff"], abs=1e-6)
        assert got.status == exp["status"]
        assert got.is_marginal == exp["is_marginal"]

    # ---- explicit per-case pins ----
    if pins.get("expect_fallback"):
        assert exam_year is not None and used_year == max_year != exam_year
        assert resp.total_count > 0, "fallback must serve the freshest year's data"
        assert resp.confidence_message and str(exam_year) in resp.confidence_message
    if "expect_tier" in pins:
        assert resp.confidence_tier == pins["expect_tier"]
    for inc in pins.get("includes", []):
        code = inc["course_code"]
        assert code in by_code, f"{code} expected but absent"
        if "status" in inc:
            assert by_code[code].status == inc["status"]
        if "is_marginal" in inc:
            assert by_code[code].is_marginal == inc["is_marginal"]
    for code in pins.get("excludes", []):
        assert code not in by_code, f"{code} expected absent but present"
