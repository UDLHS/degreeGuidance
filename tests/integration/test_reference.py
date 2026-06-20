"""GET /api/v1/reference — public, no auth (Week 3, Part 1 UI)."""

from __future__ import annotations

from httpx import AsyncClient


async def test_reference_shape_and_counts(client: AsyncClient):
    r = await client.get("/api/v1/reference")
    assert r.status_code == 200, r.text
    b = r.json()
    assert len(b["districts"]) == 25
    codes = {s["code"] for s in b["streams"]}
    assert codes == {
        "ARTS", "COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE",
        "ENGINEERING_TECH", "BIOSYSTEMS_TECH", "ICT",
    }
    assert len(b["universities"]) == 21
    cmb = next(u for u in b["universities"] if u["code"] == "CMB")
    assert cmb["name_en"] == "University of Colombo"

    phys = next(s for s in b["streams"] if s["code"] == "PHYSICAL_SCIENCE")
    assert "Combined Mathematics" in phys["subjects"]
    assert "Physics" in phys["subjects"]
