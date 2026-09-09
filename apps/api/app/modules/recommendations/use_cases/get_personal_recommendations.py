"""Build content-based personal recommendations from explicit ratings."""

from uuid import UUID

from app.modules.catalog.domain import TitleDetails
from app.modules.recommendations.domain import (
    PersonalRecommendation,
    PersonalRecommendations,
    RatedTitle,
    personal_reason,
    to_title_summary,
)
from app.modules.recommendations.ports import PersonalRecommendationRepository, SemanticTitleIndex
from app.modules.recommendations.profile import build_rating_profile
from app.modules.recommendations.ranking import fits_diversity

RESULT_LIMIT = 12
CANDIDATE_LIMIT = 60


class GetPersonalRecommendations:
    """Hide profile construction, candidate exclusions, and diversity selection."""

    def __init__(
        self, repository: PersonalRecommendationRepository, index: SemanticTitleIndex
    ) -> None:
        self._repository = repository
        self._index = index

    def execute(self, user_id: UUID) -> PersonalRecommendations:
        ratings = self._repository.rated_titles(user_id)
        profile = self._profile_vector(ratings)
        if not profile:
            return PersonalRecommendations(movies=[], tv_series=[])

        excluded = self._repository.excluded_title_ids(user_id) | {
            rating.title.id for rating in ratings
        }
        return PersonalRecommendations(
            movies=self._recommend(profile, "movie", excluded, ratings),
            tv_series=self._recommend(profile, "tv", excluded, ratings),
        )

    def _recommend(
        self, profile: list[float], title_type: str, excluded: set[str], ratings: list[RatedTitle]
    ) -> list[PersonalRecommendation]:
        selected: list[TitleDetails] = []
        for title_id in self._index.search_profile(profile, title_type, CANDIDATE_LIMIT, excluded):
            if title_id in excluded:
                continue
            candidate = self._repository.details(title_id)
            if candidate is None or candidate.title_type != title_type:
                continue
            if not fits_diversity(candidate, selected):
                continue
            selected.append(candidate)
            if len(selected) == RESULT_LIMIT:
                break
        return [
            PersonalRecommendation(
                title=to_title_summary(candidate), reason=personal_reason(ratings, candidate)
            )
            for candidate in selected
        ]

    def _profile_vector(self, ratings: list[RatedTitle]) -> list[float]:
        return build_rating_profile(ratings, self._index)
