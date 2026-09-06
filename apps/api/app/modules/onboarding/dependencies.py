"""Composition root and reusable completion guard for taste onboarding."""

from dataclasses import dataclass
from random import SystemRandom
from typing import Annotated

from fastapi import Depends, HTTPException

from app.adapters.postgres.onboarding_repository import SqlAlchemyOnboardingRepository
from app.core.config import Settings
from app.core.database import get_database_engine
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.domain import User
from app.modules.onboarding.use_cases import (
    GetOnboarding,
    IsOnboardingComplete,
    SearchOnboardingTitles,
)


@dataclass(frozen=True)
class OnboardingUseCases:
    get_onboarding: GetOnboarding
    is_onboarding_complete: IsOnboardingComplete
    search_onboarding_titles: SearchOnboardingTitles


def get_onboarding_use_cases() -> OnboardingUseCases:
    return configured_onboarding_use_cases(Settings.from_environment().database_url)


def require_completed_onboarding(
    user: Annotated[User, Depends(get_current_user)],
    use_cases: Annotated[OnboardingUseCases, Depends(get_onboarding_use_cases)],
) -> User:
    if not use_cases.is_onboarding_complete.execute(user.id):
        raise HTTPException(status_code=403, detail="Complete taste onboarding first.")
    return user


def configured_onboarding_use_cases(database_url: str) -> OnboardingUseCases:
    repository = SqlAlchemyOnboardingRepository(get_database_engine(database_url))
    return OnboardingUseCases(
        get_onboarding=GetOnboarding(repository, SystemRandom()),
        is_onboarding_complete=IsOnboardingComplete(repository),
        search_onboarding_titles=SearchOnboardingTitles(repository),
    )
