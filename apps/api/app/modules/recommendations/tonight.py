"""Temporary viewing preferences and diversity selection for tonight."""

from dataclasses import dataclass
from typing import Literal

from app.modules.catalog.domain import TitleDetails
from app.modules.recommendations.domain import PersonalRecommendation


@dataclass(frozen=True)
class TonightPreferences:
    title_type: Literal["movie", "tv"] = "movie"
    genres: tuple[str, ...] = ()
    max_minutes: int | None = None
    year_from: int | None = None
    year_to: int | None = None
    mode: Literal["familiar", "discover"] = "familiar"

    def matches(self, title: TitleDetails) -> bool:
        if title.title_type != self.title_type:
            return False
        if self.genres and not set(self.genres).intersection(title.genres):
            return False
        if self.max_minutes is not None and not (
            title.runtime_minutes is not None and 0 < title.runtime_minutes <= self.max_minutes
        ):
            return False
        year = title.release_date.year if title.release_date else None
        if self.year_from is not None and (year is None or year < self.year_from):
            return False
        if self.year_to is not None and (year is None or year > self.year_to):
            return False
        return True


@dataclass(frozen=True)
class TonightRecommendations:
    items: list[PersonalRecommendation]
    status: Literal["ready", "no_profile", "no_matches"]


def select_tonight(
    candidates: list[TitleDetails],
    vectors: dict[str, list[float]],
    profile: list[float],
    mode: Literal["familiar", "discover"],
    limit: int = 6,
) -> list[TitleDetails]:
    """MMR keeps discovery inside the retrieved taste-relevant candidate pool."""
    relevance_weight = 0.9 if mode == "familiar" else 0.55
    selected: list[TitleDetails] = []
    remaining = candidates.copy()
    while remaining and len(selected) < limit:

        def score(title: TitleDetails) -> float:
            vector = vectors[title.id]
            relevance = sum(a * b for a, b in zip(profile, vector, strict=True))
            redundancy = max(
                (
                    sum(a * b for a, b in zip(vector, vectors[item.id], strict=True))
                    for item in selected
                ),
                default=0.0,
            )
            return relevance_weight * relevance - (1 - relevance_weight) * redundancy

        best = max(remaining, key=score)
        selected.append(best)
        remaining = [
            title
            for title in remaining
            if title.id != best.id
            and title.title.casefold().strip() != best.title.casefold().strip()
        ]
    return selected
