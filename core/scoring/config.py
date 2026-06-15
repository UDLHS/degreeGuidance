"""Active scoring-config loader (Week 3, masterplan §9).

Reads the single active row from scoring_config. The code-level fallback mirrors
the seeded v1 row (migration 22) so the scorer still works if the table is empty.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_CONFIG: dict = {
    "weights": {
        "interest": 0.30,
        "career": 0.25,
        "z_margin": 0.15,
        "university": 0.15,
        "industry": 0.15,
    },
    "thresholds": {
        "safe_score": 0.6,
        "safe_margin": 0.10,
        "ambitious_score": 0.6,
        "ambitious_margin": 0.05,
        "hidden_score": 0.5,
        "marginal_band": 0.05,
        "z_margin_tanh_scale": 4.0,
    },
}


async def load_active_config(session: AsyncSession) -> dict:
    row = (
        await session.execute(
            text(
                "SELECT weights, thresholds FROM scoring_config "
                "WHERE is_active ORDER BY config_id DESC LIMIT 1"
            )
        )
    ).first()
    if row is None:
        return DEFAULT_CONFIG
    return {"weights": dict(row.weights), "thresholds": dict(row.thresholds)}
