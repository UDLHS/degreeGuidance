"""Integration tests for the stream-specific cutoff override mechanism.

Food Business Management (107L, Sabaragamuwa) is the one real course (traced
across the 2023/2024/2025 handbooks) whose cutoff table carries genuinely
different z-scores per A/L stream under a single official Uni-Code. These
tests prove:

1. core.eligibility.engine.evaluate_eligibility (shared by the recommendation
   service) picks the override cutoff for the student's own stream via the
   new LEFT JOIN + COALESCE, and falls back to the general z_score_cutoffs
   row exactly as before when no override exists (the other 260+ courses'
   path is untouched).
2. apps.worker.jobs.ingest_zscores.apply_stream_overrides correctly turns a
   Gate-2 {run_id}.overrides.json artifact into course_stream_cutoff_overrides
   rows and annotates the base row's notes for the admin matrix viewer.

Uses the real 107L course + real district/stream reference rows (same
sentinel-year isolation pattern as test_admin_ingestions_pdf.py) so nothing
here depends on invented fixture data -- it's the actual case this feature
exists for.
"""

from __future__ import annotations

import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.worker.jobs.ingest_zscores import apply_stream_overrides
from core.config import settings
from core.eligibility.engine import evaluate_eligibility
from core.schemas.eligibility import EligibilityRequest, SubjectInput

SENTINEL_YEAR = 2031
COURSE = "107L"  # Food Business Management, Sabaragamuwa -- the real split course
NORMAL_COURSE = "001A"  # Medicine, Colombo -- an ordinary, unsplit course

COMMERCE_SUBJECTS = [
    SubjectInput(subject="Business Studies", grade="A"),
    SubjectInput(subject="Economics", grade="A"),
    SubjectInput(subject="Accounting", grade="A"),
]
BIO_SUBJECTS = [
    SubjectInput(subject="Biology", grade="A"),
    SubjectInput(subject="Chemistry", grade="A"),
    SubjectInput(subject="Physics", grade="A"),
]


async def _ids(db: AsyncSession) -> dict:
    districts = (await db.execute(text("SELECT code, district_id FROM districts"))).all()
    streams = (await db.execute(text("SELECT code, stream_id FROM streams"))).all()
    return {
        "district": {r[0]: r[1] for r in districts},
        "stream": {r[0]: r[1] for r in streams},
    }


@pytest_asyncio.fixture(autouse=True)
async def _cleanup(db_session: AsyncSession):
    """Sentinel-year isolation: delete only rows this suite creates."""
    yield
    await db_session.execute(
        text("DELETE FROM course_stream_cutoff_overrides WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM eligibility_audit WHERE cutoff_year_used = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_override_picks_correct_cutoff_per_stream(db_session: AsyncSession):
    ids = await _ids(db_session)
    colombo = ids["district"]["COLOMBO"]
    commerce = ids["stream"]["COMMERCE"]
    bio = ids["stream"]["BIO_SCIENCE"]

    # Base row NULL (no single honest number), overrides carry the real values
    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
            "VALUES (:y, :c, :d, NULL)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo},
    )
    await db_session.execute(
        text(
            "INSERT INTO course_stream_cutoff_overrides "
            "(year, course_code, district_id, stream_id, z_score) VALUES "
            "(:y, :c, :d, :s, :z)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo, "s": commerce, "z": 1.2000},
    )
    await db_session.execute(
        text(
            "INSERT INTO course_stream_cutoff_overrides "
            "(year, course_code, district_id, stream_id, z_score) VALUES "
            "(:y, :c, :d, :s, :z)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo, "s": bio, "z": 0.5000},
    )
    await db_session.commit()

    # Commerce-stream student above the Commerce cutoff -> sees the Commerce number
    resp = await evaluate_eligibility(
        db_session,
        EligibilityRequest(
            z_score=1.25, district_code="COLOMBO", stream_code="COMMERCE",
            exam_year=SENTINEL_YEAR, subjects=COMMERCE_SUBJECTS,
        ),
    )
    by_code = {r.course_code: r for r in resp.results}
    assert COURSE in by_code
    assert by_code[COURSE].cutoff_z_score == pytest.approx(1.2000)

    # Bio-Science student above the (much lower) Bio/Physical cutoff -> sees that number
    resp2 = await evaluate_eligibility(
        db_session,
        EligibilityRequest(
            z_score=0.6, district_code="COLOMBO", stream_code="BIO_SCIENCE",
            exam_year=SENTINEL_YEAR, subjects=BIO_SUBJECTS,
        ),
    )
    by_code2 = {r.course_code: r for r in resp2.results}
    assert COURSE in by_code2
    assert by_code2[COURSE].cutoff_z_score == pytest.approx(0.5000)

    # Commerce student BELOW the Commerce cutoff -> correctly excluded
    resp3 = await evaluate_eligibility(
        db_session,
        EligibilityRequest(
            z_score=0.9, district_code="COLOMBO", stream_code="COMMERCE",
            exam_year=SENTINEL_YEAR, subjects=COMMERCE_SUBJECTS,
        ),
    )
    assert COURSE not in {r.course_code for r in resp3.results}


@pytest.mark.asyncio
async def test_ordinary_course_unaffected_by_override_join(db_session: AsyncSession):
    """A normal course with no override row behaves exactly as before --
    proves the LEFT JOIN + COALESCE is a no-op for the other 260+ courses."""
    ids = await _ids(db_session)
    colombo = ids["district"]["COLOMBO"]

    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
            "VALUES (:y, :c, :d, :z)"
        ),
        {"y": SENTINEL_YEAR, "c": NORMAL_COURSE, "d": colombo, "z": 1.5000},
    )
    await db_session.commit()

    resp = await evaluate_eligibility(
        db_session,
        EligibilityRequest(
            z_score=1.6, district_code="COLOMBO", stream_code="BIO_SCIENCE",
            exam_year=SENTINEL_YEAR, subjects=BIO_SUBJECTS,
        ),
    )
    by_code = {r.course_code: r for r in resp.results}
    assert NORMAL_COURSE in by_code
    assert by_code[NORMAL_COURSE].cutoff_z_score == pytest.approx(1.5000)


@pytest.mark.asyncio
async def test_apply_stream_overrides_from_artifact(db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    ids = await _ids(db_session)
    colombo_id = ids["district"]["COLOMBO"]

    run_id = str(uuid.uuid4())
    # Base row must already exist -- apply_stream_overrides runs AFTER
    # ingest_zscores() in the real promote flow.
    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
            "VALUES (:y, :c, :d, NULL)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo_id},
    )
    await db_session.commit()

    artifact = {
        "columns": [
            {
                "course_code": COURSE,
                "column_key": "p1.g1.c0",
                "stream_codes": ["COMMERCE"],
                "raw_label": "FOOD BUSINESS MANAGEMENT [Commerce Stream] (Sabaragamuwa University of Sri Lanka)",
                "values": {"Colombo": "1.2957"},
            },
        ]
    }
    (tmp_path / f"{run_id}.overrides.json").write_text(json.dumps(artifact), encoding="utf-8")

    result = await apply_stream_overrides(db_session, run_id, SENTINEL_YEAR)
    assert result["rows_written"] == 1
    assert result["courses"] == 1

    row = (
        await db_session.execute(
            text(
                "SELECT z_score FROM course_stream_cutoff_overrides "
                "WHERE year = :y AND course_code = :c AND district_id = :d AND stream_id = :s"
            ),
            {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo_id, "s": ids["stream"]["COMMERCE"]},
        )
    ).scalar()
    assert float(row) == pytest.approx(1.2957)

    note = (
        await db_session.execute(
            text(
                "SELECT notes FROM z_score_cutoffs "
                "WHERE year = :y AND course_code = :c AND district_id = :d"
            ),
            {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo_id},
        )
    ).scalar()
    assert "COMMERCE" in note
    assert "1.2957" in note


@pytest.mark.asyncio
async def test_apply_stream_overrides_noop_without_artifact(db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    result = await apply_stream_overrides(db_session, str(uuid.uuid4()), SENTINEL_YEAR)
    assert result == {"rows_written": 0, "courses": 0}
