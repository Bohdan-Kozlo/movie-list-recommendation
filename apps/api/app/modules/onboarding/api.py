"""REST transport for mandatory taste onboarding."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.domain import User
from app.modules.onboarding.dependencies import OnboardingUseCases, get_onboarding_use_cases
from app.modules.onboarding.domain import TitleType
from app.modules.onboarding.dto import (
    OnboardingResponse,
    OnboardingSearchResponse,
    to_onboarding_response,
    to_search_response,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("", response_model=OnboardingResponse)
def get_onboarding(
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[OnboardingUseCases, Depends(get_onboarding_use_cases)],
) -> OnboardingResponse:
    return to_onboarding_response(use_cases.get_onboarding.execute(user.id))


@router.get("/search", response_model=OnboardingSearchResponse)
def search_onboarding_titles(
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[OnboardingUseCases, Depends(get_onboarding_use_cases)],
    query: Annotated[str, Query(min_length=1, max_length=200)],
    title_type: Annotated[TitleType | None, Query(alias="type")] = None,
) -> OnboardingSearchResponse:
    titles = use_cases.search_onboarding_titles.execute(user.id, query, title_type)
    return to_search_response(titles)
