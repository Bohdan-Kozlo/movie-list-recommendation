"""Public REST endpoint for title-to-title semantic recommendations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.modules.auth.domain import User
from app.modules.onboarding.dependencies import require_completed_onboarding
from app.modules.recommendations.dependencies import (
    get_personal_recommendations_use_case,
    get_similar_titles_use_case,
)
from app.modules.recommendations.dto import (
    PersonalRecommendationsResponse,
    SimilarTitlesResponse,
    to_personal_recommendations_response,
    to_similar_titles_response,
)
from app.modules.recommendations.use_cases import GetPersonalRecommendations, GetSimilarTitles

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/personal", response_model=PersonalRecommendationsResponse)
def get_personal_recommendations(
    user: Annotated[User, Depends(require_completed_onboarding)],
    use_case: Annotated[GetPersonalRecommendations, Depends(get_personal_recommendations_use_case)],
) -> PersonalRecommendationsResponse:
    """Return personalized semantic recommendations for a completed taste profile."""
    try:
        return to_personal_recommendations_response(use_case.execute(user.id))
    except RuntimeError as error:
        raise HTTPException(
            status_code=503, detail="Personal recommendations are unavailable."
        ) from error


@router.get("/titles/{title_id}/similar", response_model=SimilarTitlesResponse)
def get_similar_titles(
    title_id: str,
    use_case: Annotated[GetSimilarTitles, Depends(get_similar_titles_use_case)],
) -> SimilarTitlesResponse:
    """Return semantically nearest local movies and TV series."""
    try:
        results = use_case.execute(title_id)
    except RuntimeError as error:
        raise HTTPException(
            status_code=503, detail="Semantic recommendations are unavailable."
        ) from error
    if results is None:
        raise HTTPException(status_code=404, detail="Catalogue title not found.")
    return to_similar_titles_response(results)
