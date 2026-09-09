"""Choose a short personalized list that satisfies today's viewing constraints."""

from uuid import UUID

from app.modules.recommendations.domain import (
    PersonalRecommendation,
    personal_reason,
    to_title_summary,
)
from app.modules.recommendations.ports import TonightIndex, TonightRepository
from app.modules.recommendations.profile import build_rating_profile
from app.modules.recommendations.ranking import profile_vector
from app.modules.recommendations.tonight import (
    TonightPreferences,
    TonightRecommendations,
    select_tonight,
)


class GetTonightRecommendations:
    def __init__(self, repository: TonightRepository, index: TonightIndex) -> None:
        self._repository = repository
        self._index = index

    def execute(self, user_id: UUID, preferences: TonightPreferences) -> TonightRecommendations:
        ratings = self._repository.rated_titles(user_id)
        if not ratings:
            return TonightRecommendations([], "no_profile")
        profile = build_rating_profile(ratings, self._index)
        if not profile:
            return TonightRecommendations([], "no_profile")
        excluded = self._repository.excluded_title_ids(user_id) | {r.title.id for r in ratings}
        eligible = self._repository.eligible_title_ids(preferences) - excluded
        if not eligible:
            return TonightRecommendations([], "no_matches")
        identifiers = self._index.search_tonight(profile, preferences.title_type, eligible, 60)
        candidates = []
        for identifier in dict.fromkeys(identifiers):
            if identifier not in eligible:
                continue
            title = self._repository.details(identifier)
            if title is not None and preferences.matches(title):
                candidates.append(title)
        stored = self._index.vectors([title.id for title in candidates]) if candidates else {}
        vectors = {}
        for title in candidates:
            vector = profile_vector([(1.0, stored.get(title.id) or self._index.embed(title))])
            if len(vector) != len(profile):
                raise RuntimeError("Semantic title embeddings have incompatible dimensions.")
            vectors[title.id] = vector
        selected = select_tonight(candidates, vectors, profile, preferences.mode)
        items = []
        for title in selected:
            reason = personal_reason(ratings, title)
            if title.runtime_minutes and title.runtime_minutes > 0:
                unit = "per episode" if title.title_type == "tv" else "runtime"
                reason += f" {title.runtime_minutes} min {unit}."
            if title.release_date:
                reason += f" Released in {title.release_date.year}."
            items.append(PersonalRecommendation(to_title_summary(title), reason))
        return TonightRecommendations(items, "ready" if items else "no_matches")
