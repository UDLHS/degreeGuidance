"""Recommendation router: POST /api/v1/recommendations (Week 3).

Thin HTTP layer over core/scoring/service.py. Unknown district/stream codes
surface as 422; body validation (z_score range, etc.) is handled by Pydantic.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_db
from core.eligibility.engine import EligibilityInputError
from core.schemas.recommendation import RecommendationRequest, RecommendationResponse
from core.scoring.service import recommend

router = APIRouter(prefix="/api/v1", tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Rank eligible courses for a student profile (deterministic, §9)",
)
async def post_recommendations(
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    try:
        return await recommend(db, payload)
    except EligibilityInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
