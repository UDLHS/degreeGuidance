"""Integration tests for the codeless-cutoff mechanism (migration 38).

The requirement: a cutoff-table column with real z-scores but NO Uni-Code in
the book must be PRESERVED, never ignored, never force-fitted onto another
course's code. Real 2023 case: "Computing & Information Systems (Sabaragamuwa)"
— discontinued/merged into Information Systems (096L), but still prints its own
cutoff column. apply_unmapped_cutoffs stores it verbatim in unmapped_cutoffs.

Sentinel-year isolation, same pattern as the other ingestion tests.
"""

from __future__ import annotations

import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.worker.jobs.ingest_zscores import apply_unmapped_cutoffs
from core.config import settings

SENTINEL_YEAR = 2032
LABEL = "COMPUTING & INFORMATION SYSTEMS (Sabaragamuwa University of Sri Lanka)"


@pytest_asyncio.fixture(autouse=True)
async def _cleanup(db_session: AsyncSession):
    yield
    await db_session.execute(
        text("DELETE FROM unmapped_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM ingestion_runs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.commit()


async def _make_run(db: AsyncSession) -> str:
    """A real ingestion_runs row (unmapped_cutoffs.run_id FKs to it)."""
    run_id = str(uuid.uuid4())
    await db.execute(
        text(
            "INSERT INTO ingestion_runs (run_id, run_type, status, year) "
            "VALUES (:id, 'pdf_extraction', 'success', :y)"
        ),
        {"id": run_id, "y": SENTINEL_YEAR},
    )
    await db.commit()
    return run_id


@pytest.mark.asyncio
async def test_apply_unmapped_preserves_zscores(db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    run_id = await _make_run(db_session)

    artifact = {
        "columns": [
            {
                "column_key": "p181.g1.c02",
                "raw_label": LABEL,
                "course_name": "Computing & Information Systems",
                "university": "Sabaragamuwa University of Sri Lanka",
                "values": {"Colombo": "1.0381", "Gampaha": "1.0380", "Kalutara": "NQC"},
            }
        ]
    }
    (tmp_path / f"{run_id}.unmapped.json").write_text(json.dumps(artifact), encoding="utf-8")

    result = await apply_unmapped_cutoffs(db_session, run_id, SENTINEL_YEAR)
    assert result["columns"] == 1
    assert result["rows_written"] == 3  # 3 districts in the fixture

    rows = (
        await db_session.execute(
            text(
                "SELECT d.code, u.z_score, u.notes, u.course_name FROM unmapped_cutoffs u "
                "JOIN districts d ON d.district_id = u.district_id "
                "WHERE u.year = :y AND u.raw_label = :l ORDER BY d.code"
            ),
            {"y": SENTINEL_YEAR, "l": LABEL},
        )
    ).all()
    by_district = {r.code: (r.z_score, r.notes) for r in rows}
    assert float(by_district["COLOMBO"][0]) == pytest.approx(1.0381)
    assert float(by_district["GAMPAHA"][0]) == pytest.approx(1.0380)
    assert by_district["KALUTARA"][0] is None          # NQC -> null z-score
    assert by_district["KALUTARA"][1] == "NQC"         # note preserved
    assert rows[0].course_name == "Computing & Information Systems"


@pytest.mark.asyncio
async def test_apply_unmapped_is_idempotent(db_session: AsyncSession, tmp_path, monkeypatch):
    """Re-promoting the same book updates, never duplicates (unique key)."""
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    run_id = await _make_run(db_session)
    artifact = {"columns": [{
        "column_key": "k", "raw_label": LABEL,
        "course_name": None, "university": None,
        "values": {"Colombo": "1.0381"},
    }]}
    (tmp_path / f"{run_id}.unmapped.json").write_text(json.dumps(artifact), encoding="utf-8")

    await apply_unmapped_cutoffs(db_session, run_id, SENTINEL_YEAR)
    await apply_unmapped_cutoffs(db_session, run_id, SENTINEL_YEAR)  # again

    n = (await db_session.execute(
        text("SELECT count(*) FROM unmapped_cutoffs WHERE year = :y AND raw_label = :l"),
        {"y": SENTINEL_YEAR, "l": LABEL},
    )).scalar()
    assert n == 1  # not 2


@pytest.mark.asyncio
async def test_apply_unmapped_noop_without_artifact(db_session: AsyncSession, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path))
    result = await apply_unmapped_cutoffs(db_session, str(uuid.uuid4()), SENTINEL_YEAR)
    assert result == {"rows_written": 0, "columns": 0}
