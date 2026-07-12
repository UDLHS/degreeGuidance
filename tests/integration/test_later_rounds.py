"""Later-selection-rounds window + the 4.0 z-score cap (user fine-tunes, 2026-07-12).

Courses whose cutoff sits at most `later_round_z_margin` (default 0.2) ABOVE
the student's z-score are returned in a separate, disclaimed `later_round`
list — in past cycles, seats vacated after the first UGC round admitted
near-miss students. These tests pin the contract:

  - a near miss inside the window lands in later_round, never in results;
  - outside the window it is invisible;
  - an eligible course is never duplicated into later_round;
  - the list is sorted closest-miss first;
  - subject rules still gate the list (a course the student can never take
    is never dangled in front of them);
  - the applied window width is reported;
  - the z-score cap is 4.0 (the official standardisation exceeds 3).

Sentinel exam year 2028 (2029-2034 are taken by other suites), purge-first.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.eligibility.engine import evaluate_eligibility
from core.schemas.eligibility import EligibilityRequest, SubjectInput

SENTINEL_YEAR = 2028
PS_SUBJECTS = [
    SubjectInput(subject="Combined Mathematics", grade="A"),
    SubjectInput(subject="Physics", grade="A"),
    SubjectInput(subject="Chemistry", grade="A"),
]
# No Chemistry — Engineering's curated rule (008) requires it explicitly.
PS_SUBJECTS_NO_CHEM = [
    SubjectInput(subject="Combined Mathematics", grade="A"),
    SubjectInput(subject="Physics", grade="A"),
    SubjectInput(subject="Information & Communication Technology", grade="A"),
]

# course -> sentinel COLOMBO cutoff. All three are real, active,
# PHYSICAL_SCIENCE-eligible catalog courses.
CUTOFFS = {"013A": 1.5000, "013B": 1.6000, "008B": 1.6000}


@pytest_asyncio.fixture
async def sentinel_cutoffs(db_session: AsyncSession):
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    did = (
        await db_session.execute(text("SELECT district_id FROM districts WHERE code='COLOMBO'"))
    ).scalar_one()
    for code, z in CUTOFFS.items():
        await db_session.execute(
            text(
                "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
                "VALUES (:y, :c, :d, :z)"
            ),
            {"y": SENTINEL_YEAR, "c": code, "d": did, "z": z},
        )
    await db_session.commit()
    yield
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.commit()


def _req(z: float, subjects=None) -> EligibilityRequest:
    return EligibilityRequest(
        z_score=z,
        district_code="COLOMBO",
        stream_code="PHYSICAL_SCIENCE",
        exam_year=SENTINEL_YEAR,
        subjects=subjects or PS_SUBJECTS,
    )


async def test_near_miss_lands_in_later_round(db_session, sentinel_cutoffs):
    resp = await evaluate_eligibility(db_session, _req(1.45))
    codes = {i.course_code for i in resp.later_round}
    assert "013A" in codes  # 0.05 above
    assert "013A" not in {i.course_code for i in resp.results}
    item = next(i for i in resp.later_round if i.course_code == "013A")
    assert item.gap_above == pytest.approx(0.05)
    assert item.cutoff_z_score == pytest.approx(1.5)
    assert resp.later_round_count == len(resp.later_round)
    # near misses never inflate the eligibility counts
    assert resp.eligible_count + resp.conditional_count == len(resp.results)


async def test_outside_window_is_invisible(db_session, sentinel_cutoffs):
    resp = await evaluate_eligibility(db_session, _req(1.25))
    assert resp.later_round == []  # 0.25 / 0.35 above: beyond the 0.2 window
    assert {i.course_code for i in resp.results} == set()


async def test_eligible_course_never_duplicated(db_session, sentinel_cutoffs):
    resp = await evaluate_eligibility(db_session, _req(1.55))
    assert "013A" in {i.course_code for i in resp.results}
    later = {i.course_code for i in resp.later_round}
    assert "013A" not in later
    assert "013B" in later  # 1.60 is 0.05 above 1.55


async def test_sorted_closest_miss_first(db_session, sentinel_cutoffs):
    resp = await evaluate_eligibility(db_session, _req(1.45))
    gaps = [i.gap_above for i in resp.later_round]
    assert gaps == sorted(gaps)
    assert resp.later_round[0].course_code == "013A"  # 0.05 before the 0.15s


async def test_subject_rule_gates_later_round(db_session, sentinel_cutoffs):
    # 008B (Engineering) requires Chemistry; without it the near miss must
    # NOT be dangled in front of the student.
    resp = await evaluate_eligibility(db_session, _req(1.55, PS_SUBJECTS_NO_CHEM))
    assert "008B" not in {i.course_code for i in resp.later_round}


async def test_window_width_reported(db_session, sentinel_cutoffs):
    resp = await evaluate_eligibility(db_session, _req(1.45))
    assert resp.later_round_margin == pytest.approx(settings.later_round_z_margin)


# ---- z-score cap: official standardisation exceeds 3; real max is 4.0 ----

async def test_z_score_between_3_and_4_accepted(client: AsyncClient, sentinel_cutoffs):
    r = await client.post("/api/v1/eligibility", json={
        "z_score": 3.5, "district_code": "COLOMBO", "stream_code": "PHYSICAL_SCIENCE",
        "exam_year": SENTINEL_YEAR,
        "subjects": [{"subject": s.subject, "grade": s.grade} for s in PS_SUBJECTS],
    })
    assert r.status_code == 200, r.text


async def test_z_score_above_4_rejected(client: AsyncClient):
    r = await client.post("/api/v1/eligibility", json={
        "z_score": 4.01, "district_code": "COLOMBO", "stream_code": "PHYSICAL_SCIENCE",
        "subjects": [{"subject": s.subject, "grade": s.grade} for s in PS_SUBJECTS],
    })
    assert r.status_code == 422
