"""Domain values for a user's initial taste collection."""

from dataclasses import dataclass
from typing import Literal

TitleType = Literal["movie", "tv"]


@dataclass(frozen=True)
class OnboardingTitle:
    id: str
    title: str
    title_type: TitleType
    release_date: str | None
    original_language: str
    poster_path: str | None
    popularity: float
    genres: list[str]

    @property
    def decade(self) -> int | None:
        return int(self.release_date[:3] + "0") if self.release_date else None


@dataclass(frozen=True)
class OnboardingProgress:
    ratings_recorded: int
    ratings_required: int
    movies: list[OnboardingTitle]
    tv_series: list[OnboardingTitle]

    @property
    def is_complete(self) -> bool:
        return self.ratings_recorded >= self.ratings_required

    @property
    def ratings_remaining(self) -> int:
        return max(0, self.ratings_required - self.ratings_recorded)
