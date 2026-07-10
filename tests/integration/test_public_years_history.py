"""Public year-selection endpoints (Phase 2 plan §1.1 / §1.4).

GET /api/v1/years          — promoted exam years, newest first, one is_latest.
GET /api/v1/cutoff-history — per-course effective cutoffs per year for one
                             (district, stream), stream-override-aware.

Sentinel-year isolation (year 2033): the assertions never depend on which real
handbooks are promoted, only on rows this suite inserts and removes.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SENTINEL_YEAR = 2033
COURSE = "107L"          # real course with real stream-override behavior
NORMAL_COURSE = "001A"   # ordinary course, no overrides


async def _ids(db: AsyncSession) -> dict:
    districts = (await db.execute(text("SELECT code, district_id FROM districts"))).all()
    streams = (await db.execute(text("SELECT code, stream_id FROM streams"))).all()
    return {"district": dict(districts), "stream": dict(streams)}


@pytest_asyncio.fixture(autouse=True)
async def _sentinel(db_session: AsyncSession):
    ids = await _ids(db_session)
    colombo = ids["district"]["COLOMBO"]
    commerce = ids["stream"]["COMMERCE"]
    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) VALUES "
            "(:y, :normal, :d, 1.5000), (:y, :split, :d, 0.9000)"
        ),
        {"y": SENTINEL_YEAR, "normal": NORMAL_COURSE, "split": COURSE, "d": colombo},
    )
    await db_session.execute(
        text(
            "INSERT INTO course_stream_cutoff_overrides "
            "(year, course_code, district_id, stream_id, z_score) VALUES (:y, :c, :d, :s, 1.2000)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": colombo, "s": commerce},
    )
    await db_session.commit()
    yield
    await db_session.execute(
        text("DELETE FROM course_stream_cutoff_overrides WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.commit()


async def test_years_shape_and_latest(client: AsyncClient):
    r = await client.get("/api/v1/years")
    assert r.status_code == 200
    years = r.json()["years"]
    assert years, "at least the sentinel year must be present"
    values = [y["year"] for y in years]
    assert values == sorted(values, reverse=True), "years must be newest first"
    assert SENTINEL_YEAR in values  # 2033 sentinel is ahead of any real year
    latest_flags = [y for y in years if y["is_latest"]]
    assert len(latest_flags) == 1 and latest_flags[0]["year"] == values[0]


async def test_history_is_stream_aware(client: AsyncClient):
    # Commerce sees the override value for the split course...
    r = await client.get(
        "/api/v1/cutoff-history",
        params={"district_code": "COLOMBO", "stream_code": "COMMERCE"},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["courses"][COURSE][str(SENTINEL_YEAR)] == pytest.approx(1.2000)
    assert d["courses"][NORMAL_COURSE][str(SENTINEL_YEAR)] == pytest.approx(1.5000)
    assert SENTINEL_YEAR in d["years"]

    # ...while a stream with no override sees the general row.
    r2 = await client.get(
        "/api/v1/cutoff-history",
        params={"district_code": "COLOMBO", "stream_code": "ARTS"},
    )
    d2 = r2.json()
    assert d2["courses"][COURSE][str(SENTINEL_YEAR)] == pytest.approx(0.9000)


async def test_history_unknown_codes_422(client: AsyncClient):
    r = await client.get(
        "/api/v1/cutoff-history",
        params={"district_code": "NOWHERE", "stream_code": "ARTS"},
    )
    assert r.status_code == 422
    r2 = await client.get(
        "/api/v1/cutoff-history",
        params={"district_code": "COLOMBO", "stream_code": "NOT_A_STREAM"},
    )
    assert r2.status_code == 422


async def test_recommendations_honour_selected_year(client: AsyncClient):
    """The student-side year switcher contract: exam_year in → that year out."""
    payload = {
        "z_score": 2.0,
        "district_code": "COLOMBO",
        "stream_code": "COMMERCE",
        "exam_year": SENTINEL_YEAR,
        "subjects": [
            {"subject": "Business Studies", "grade": "A"},
            {"subject": "Economics", "grade": "A"},
            {"subject": "Accounting", "grade": "A"},
        ],
    }
    r = await client.post("/api/v1/recommendations", json=payload)
    assert r.status_code == 200
    b = r.json()
    assert b["exam_year_used"] == SENTINEL_YEAR
    by_code = {x["course_code"]: x for x in b["recommendations"]}
    # Commerce student is judged against the OVERRIDE cutoff for the split course.
    if COURSE in by_code:  # subject rules permitting
        assert by_code[COURSE]["cutoff_z_score"] == pytest.approx(1.2000)