"""HTTP-contract smoke tests for POST /api/v1/eligibility.

These complement the engine suite: they verify the FastAPI layer wiring,
Pydantic request validation, the 422 paths, and the response shape — not the
eligibility maths (that is covered exhaustively in test_eligibility_engine.py).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

ENDPOINT = "/api/v1/eligibility"


async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


_BIO_SUBJECTS = [
    {"subject": "Biology", "grade": "C"},
    {"subject": "Chemistry", "grade": "C"},
    {"subject": "Physics", "grade": "S"},
]


async def test_happy_path_shape(client: AsyncClient):
    r = await client.post(
        ENDPOINT,
        json={
            "z_score": 2.38, "district_code": "COLOMBO", "stream_code": "BIO_SCIENCE",
            "subjects": _BIO_SUBJECTS,
        },
    )
    assert r.status_code == 200
    body = r.json()
    for key in (
        "exam_year_used", "confidence_tier", "eligible_count",
        "conditional_count", "total_count", "results",
    ):
        assert key in body, f"missing key {key}"
    assert body["total_count"] == len(body["results"])
    assert body["confidence_tier"] == "current"
    # Medicine Colombo (cutoff 2.3700) must be present for a 2.38 bio student.
    codes = {item["course_code"] for item in body["results"]}
    assert "001A" in codes
    item = next(i for i in body["results"] if i["course_code"] == "001A")
    assert item["student_margin"] == pytest.approx(0.01, abs=1e-6)
    assert item["is_marginal"] is True


async def test_lowercase_codes_normalize(client: AsyncClient):
    r = await client.post(
        ENDPOINT,
        json={
            "z_score": 2.38, "district_code": "colombo", "stream_code": "bio_science",
            "subjects": _BIO_SUBJECTS,
        },
    )
    assert r.status_code == 200


async def test_unknown_district_is_422(client: AsyncClient):
    r = await client.post(
        ENDPOINT,
        json={
            "z_score": 2.0, "district_code": "ATLANTIS", "stream_code": "BIO_SCIENCE",
            "subjects": _BIO_SUBJECTS,
        },
    )
    assert r.status_code == 422


async def test_unknown_stream_is_422(client: AsyncClient):
    r = await client.post(
        ENDPOINT,
        json={
            "z_score": 2.0, "district_code": "COLOMBO", "stream_code": "WIZARDRY",
            "subjects": _BIO_SUBJECTS,
        },
    )
    assert r.status_code == 422


@pytest.mark.parametrize("bad_z", [4.5, -2.5])  # cap raised 3.0->4.0 (2026-07-12): 3.5 is a legal score
async def test_z_score_out_of_range_is_422(client: AsyncClient, bad_z: float):
    r = await client.post(
        ENDPOINT,
        json={
            "z_score": bad_z, "district_code": "COLOMBO", "stream_code": "BIO_SCIENCE",
            "subjects": _BIO_SUBJECTS,
        },
    )
    assert r.status_code == 422


async def test_missing_subjects_is_422(client: AsyncClient):
    r = await client.post(
        ENDPOINT,
        json={"z_score": 2.0, "district_code": "COLOMBO", "stream_code": "BIO_SCIENCE"},
    )
    assert r.status_code == 422
