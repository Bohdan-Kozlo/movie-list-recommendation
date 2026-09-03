"""Check whether a user has supplied enough initial ratings."""

from uuid import UUID

from app.modules.onboarding.ports import OnboardingRepository
from app.modules.onboarding.use_cases.get_onboarding import RATINGS_REQUIRED


class IsOnboardingComplete:
    def __init__(self, repository: OnboardingRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> bool:
        return self._repository.rating_count(user_id) >= RATINGS_REQUIRED
