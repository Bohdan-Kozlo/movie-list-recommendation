"""Build a fresh, varied collection of popular titles for onboarding."""

from random import Random
from uuid import UUID

from app.modules.onboarding.domain import OnboardingProgress, OnboardingTitle, TitleType
from app.modules.onboarding.ports import OnboardingRepository

RATINGS_REQUIRED = 10
CANDIDATE_LIMIT = 120
SELECTION_SIZE = 12


class GetOnboarding:
    def __init__(self, repository: OnboardingRepository, randomizer: Random) -> None:
        self._repository = repository
        self._randomizer = randomizer

    def execute(self, user_id: UUID) -> OnboardingProgress:
        return OnboardingProgress(
            ratings_recorded=self._repository.rating_count(user_id),
            ratings_required=RATINGS_REQUIRED,
            movies=self._select(user_id, "movie"),
            tv_series=self._select(user_id, "tv"),
        )

    def _select(self, user_id: UUID, title_type: TitleType) -> list[OnboardingTitle]:
        candidates = self._repository.popular_unrated_titles(
            user_id,
            title_type,
            CANDIDATE_LIMIT,
        )
        self._randomizer.shuffle(candidates)
        selected: list[OnboardingTitle] = []
        remaining = candidates
        while remaining and len(selected) < SELECTION_SIZE:
            title = max(remaining, key=lambda item: self._novelty(item, selected))
            selected.append(title)
            remaining.remove(title)
        return selected

    @staticmethod
    def _novelty(title: OnboardingTitle, selected: list[OnboardingTitle]) -> tuple[int, int]:
        genres = {genre for item in selected for genre in item.genres}
        decades = {item.decade for item in selected if item.decade is not None}
        adds_genre = any(genre not in genres for genre in title.genres)
        adds_decade = title.decade is not None and title.decade not in decades
        return (int(adds_genre), int(adds_decade))
