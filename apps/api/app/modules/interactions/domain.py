"""Domain values and errors for a user's title library."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID


class DuplicateRatingError(Exception):
    """Raised when a user attempts to replace an existing rating."""


class InvalidRatingError(Exception):
    """Raised when a rating is outside the supported half-point scale."""


class TitleNotFoundError(Exception):
    """Raised when an interaction targets a missing catalogue title."""


@dataclass(frozen=True)
class InteractionStatus:
    title_id: UUID
    rating: float | None
    is_watchlisted: bool
    is_watched: bool
    is_not_interested: bool


@dataclass(frozen=True)
class LibraryTitle:
    """Catalogue metadata needed to render an entry in a user library."""

    id: str
    title: str
    title_type: str
    release_date: date | None
    original_language: str
    poster_path: str | None
    popularity: float
    genres: list[str]


@dataclass(frozen=True)
class LibraryItem:
    title: LibraryTitle
    rating: float | None


def rating_is_valid(value: float) -> bool:
    return 0.5 <= value <= 5.0 and (value * 2).is_integer()
