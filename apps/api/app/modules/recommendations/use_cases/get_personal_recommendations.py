"""Build content-based personal recommendations from explicit ratings."""

from math import sqrt
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
            if any(self._is_near_duplicate(candidate, accepted) for accepted in selected):
                continue
            if any(
                sum(genre in accepted.genres for accepted in selected) >= 3
                for genre in candidate.genres
            ):
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
        weighted_vectors: list[tuple[float, list[float]]] = []
        for rating in ratings:
            weight = rating.value - 3.0
            if weight:
                weighted_vectors.append((weight, self._index.embed(rating.title)))
        if not weighted_vectors:
            return []
        dimensions = len(weighted_vectors[0][1])
        if dimensions == 0 or any(len(vector) != dimensions for _, vector in weighted_vectors):
            raise RuntimeError("Semantic title embeddings have incompatible dimensions.")
        profile = [
            sum(weight * vector[index] for weight, vector in weighted_vectors)
            for index in range(dimensions)
        ]
        magnitude = sqrt(sum(component * component for component in profile))
        return [component / magnitude for component in profile] if magnitude else []

    @staticmethod
    def _is_near_duplicate(candidate: TitleDetails, accepted: TitleDetails) -> bool:
        if candidate.title.casefold().strip() == accepted.title.casefold().strip():
            return True
        if GetPersonalRecommendations._franchise_key(candidate.title) == (
            GetPersonalRecommendations._franchise_key(accepted.title)
        ):
            return True
        candidate_genres = set(candidate.genres)
        accepted_genres = set(accepted.genres)
        shared_creators = set(candidate.creators).intersection(accepted.creators)
        return bool(candidate_genres and candidate_genres == accepted_genres and shared_creators)

    @staticmethod
    def _franchise_key(title: str) -> str:
        words = [word for word in title.casefold().replace(":", " ").split() if word]
        if words[:1] in (["the"], ["a"], ["an"]):
            words = words[1:]
        return " ".join(words[:2])
