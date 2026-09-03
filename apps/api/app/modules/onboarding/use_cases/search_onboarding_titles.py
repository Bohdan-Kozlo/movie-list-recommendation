"""Find locally available, unrated alternatives for taste onboarding."""

from uuid import UUID

from app.modules.onboarding.domain import OnboardingTitle, TitleType
from app.modules.onboarding.ports import OnboardingRepository


class SearchOnboardingTitles:
    def __init__(self, repository: OnboardingRepository) -> None:
        self._repository = repository

    def execute(
        self, user_id: UUID, query: str, title_type: TitleType | None
    ) -> list[OnboardingTitle]:
        return self._repository.search_unrated_titles(user_id, query, title_type, limit=24)
