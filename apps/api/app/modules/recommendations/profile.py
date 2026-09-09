"""Build the shared rating profile used by personal viewing requests."""

from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.ports import SemanticTitleIndex
from app.modules.recommendations.ranking import NEUTRAL_RATING, profile_vector


def build_rating_profile(ratings: list[RatedTitle], index: SemanticTitleIndex) -> list[float]:
    stored = index.vectors([rating.title.id for rating in ratings])
    weighted = [
        (rating.value - NEUTRAL_RATING, stored.get(rating.title.id) or index.embed(rating.title))
        for rating in ratings
        if rating.value != NEUTRAL_RATING
    ]
    return profile_vector(weighted)
