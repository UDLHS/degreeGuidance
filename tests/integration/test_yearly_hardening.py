"""Yearly-loop hardening helpers (Phase 7 plan gate).

Direct tests of the promote-path helpers with sentinel-year data and tmp
archive dirs: pre-promote snapshot CSVs, per-year artifact archiving, and the
post-promote checklist (year-agnostic — computed from whatever data exists).
The wiring into /promote is exercised by the existing promote suite
(test_admin_ingestions_pdf.py), which now also redirects the archive dir.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.routers.admin_ingestions import (
    archive_run_artifacts,
    build_promote_checklist,
    snapshot_year_data,
)
from core.config import settings

SENTINEL_YEAR = 2034
COURSE = "001A"
SPLIT_COURSE = "107L"
LABEL = "yearly-hardening sentinel label"


@pytest_asyncio.fixture(autouse=True)
def _tmp_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_work_dir", str(tmp_path / "work"))
    monkeypatch.setattr(settings, "archive_dir", str(tmp_path / "archive"))
    (tmp_path / "work").mkdir()
    return tmp_path


@pytest_asyncio.fixture
async def sentinel_year(db_session: AsyncSession):
    ids = (
        await db_session.execute(
            text(
                "SELECT (SELECT district_id FROM districts WHERE code='COLOMBO'), "
                "(SELECT stream_id FROM streams WHERE code='COMMERCE')"
            )
        )
    ).first()
    did, sid = ids
    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
            "VALUES (:y, :c, :d, 1.5000)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": did},
    )
    await db_session.execute(
        text(
            "INSERT INTO course_stream_cutoff_overrides "
            "(year, course_code, district_id, stream_id, z_score) VALUES (:y, :c, :d, :s, 1.2)"
        ),
        {"y": SENTINEL_YEAR, "c": SPLIT_COURSE, "d": did, "s": sid},
    )
    await db_session.execute(
        text(
            "INSERT INTO unmapped_cutoffs (year, raw_label, district_id, z_score) "
            "VALUES (:y, :l, :d, 0.9)"
        ),
        {"y": SENTINEL_YEAR, "l": LABEL, "d": did},
    )
    await db_session.commit()
    yield SENTINEL_YEAR
    await db_session.execute(
        text("DELETE FROM unmapped_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM course_stream_cutoff_overrides WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.commit()


async def test_snapshot_writes_all_three_when_data_exists(
    db_session: AsyncSession, sentinel_year
):
    written = await snapshot_year_data(db_session, sentinel_year, "t1")
    names = {Path(p).name for p in written}
    assert names == {
        "snapshot_cutoffs_t1.csv",
        "snapshot_stream_overrides_t1.csv",
        "snapshot_unmapped_t1.csv",
    }
    cutoffs_csv = (
        Path(settings.archive_dir) / str(sentinel_year) / "snapshot_cutoffs_t1.csv"
    ).read_text(encoding="utf-8-sig")
    assert COURSE in cutoffs_csv and "COLOMBO" in cutoffs_csv and "1.5" in cutoffs_csv
    unmapped_csv = (
        Path(settings.archive_dir) / str(sentinel_year) / "snapshot_unmapped_t1.csv"
    ).read_text(encoding="utf-8-sig")
    assert LABEL in unmapped_csv


async def test_snapshot_noop_for_empty_year(db_session: AsyncSession):
    written = await snapshot_year_data(db_session, 2099, "t2")
    assert written == []
    assert not (Path(settings.archive_dir) / "2099").exists() or not any(
        (Path(settings.archive_dir) / "2099").iterdir()
    )


async def test_archive_run_artifacts_copies_what_exists(_tmp_dirs):
    run_id = str(uuid.uuid4())
    work = Path(settings.ingestion_work_dir)
    (work / f"{run_id}.pdf").write_bytes(b"%PDF-fake")
    (work / f"{run_id}.csv").write_text("a,b", encoding="utf-8")
    # no overrides/unmapped files -> only two archived
    written = archive_run_artifacts(run_id, 2034, "t3")
    names = {Path(p).name for p in written}
    assert names == {"handbook_2034_t3.pdf", "promoted_t3.csv"}
    assert (Path(settings.archive_dir) / "2034" / "handbook_2034_t3.pdf").read_bytes() == b"%PDF-fake"


async def test_checklist_reflects_year_data(db_session: AsyncSession, sentinel_year):
    checklist = await build_promote_checklist(db_session, sentinel_year)
    assert checklist["promoted_year"] == sentinel_year
    # sentinel 2034 is ahead of every real year, so it becomes the default
    assert checklist["students_now_see"] == sentinel_year
    assert checklist["is_default_year"] is True
    assert checklist["stream_override_rows"] == 1
    assert checklist["codeless_rows"] == 1
    # coverage gaps = every active course except the one we gave a cutoff
    assert checklist["coverage_gap_count"] > 0
    assert COURSE not in checklist["coverage_gaps"]