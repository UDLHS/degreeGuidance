"""Integration tests for POST /api/v1/recommendations (Week 3).

Runs against the real 2023 data. A high Z-score in Colombo / Bio-Science yields
eligible courses; we check ranking, the no-preferences vs preference modes, the
visible breakdown, the no-cutoff 'also offered' list, and validation.
"""

from __future__ import annotations

from httpx import AsyncClient

BASE = {
    "z_score": 2.6,
    "district_code": "COLOMBO",
    "stream_code": "BIO_SCIENCE",
    "subjects": [
        {"subject": "Biology", "grade": "A"},
        {"subject": "Chemistry", "grade": "A"},
        {"subject": "Physics", "grade": "A"},
    ],
}


async def test_normal_mode_ranks_by_cutoff_descending(client: AsyncClient):
    # User decision 2026-07-13: with no preferences the student is asking
    # "what's the highest course I can get?" — normal mode serves the ladder,
    # highest cutoff first. (Preference mode keeps the personalised score
    # order — pinned in test_preference_mode_activates_university.)
    r = await client.post("/api/v1/recommendations", json=BASE)
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["mode"] == "normal"
    assert b["eligible_count"] >= 1
    assert len(b["recommendations"]) >= 1
    cutoffs = [x["cutoff_z_score"] for x in b["recommendations"]]
    assert cutoffs == sorted(cutoffs, reverse=True)  # the ladder: high -> low
    # With no student preferences the mode stays "normal", but per the scoring
    # design (core/scoring/engine.py) `industry` is ALWAYS active when a course
    # carries industry tags (pure market-demand signal) — so the breakdown is
    # z_margin plus optionally industry, never the preference dimensions.
    dims = {d["name"] for d in b["recommendations"][0]["breakdown"]}
    assert "z_margin" in dims
    assert dims <= {"z_margin", "industry"}
    assert not dims & {"university", "interest", "career"}
    # Active weights are renormalized to sum to 1.
    total_weight = sum(d["weight"] for d in b["recommendations"][0]["breakdown"])
    assert abs(total_weight - 1.0) < 1e-6
    assert isinstance(b["bucket_counts"], dict)


async def test_preference_mode_activates_university(client: AsyncClient):
    r = await client.post(
        "/api/v1/recommendations", json={**BASE, "preferred_university_codes": ["CMB"]}
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["mode"] == "preference"
    # university must activate; industry may also be active (course-side signal).
    dims = {d["name"] for d in b["recommendations"][0]["breakdown"]}
    assert {"z_margin", "university"} <= dims
    assert dims <= {"z_margin", "university", "industry"}
    cmb = [x for x in b["recommendations"] if x["university_code"] == "CMB"]
    assert cmb, "expected at least one Colombo course eligible"
    uni = {d["name"]: d["raw_score"] for d in cmb[0]["breakdown"]}["university"]
    assert uni == 1.0  # preferred university scores full


async def test_also_offered_no_cutoff_shape(client: AsyncClient):
    b = (await client.post("/api/v1/recommendations", json=BASE)).json()
    assert isinstance(b["also_offered_no_cutoff_count"], int)
    for item in b["also_offered_no_cutoff"]:
        assert item["reason"] == "no_cutoff_in_district"
        assert item["course_code"] and item["university_code"]


async def test_unknown_district_is_422(client: AsyncClient):
    r = await client.post(
        "/api/v1/recommendations",
        json={**BASE, "district_code": "NOWHERE"},
    )
    assert r.status_code == 422


async def test_zscore_out_of_range_is_422(client: AsyncClient):
    r = await client.post("/api/v1/recommendations", json={**BASE, "z_score": 5.0})
    assert r.status_code == 422
