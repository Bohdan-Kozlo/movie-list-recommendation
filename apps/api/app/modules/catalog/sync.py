"""Provider-neutral values used to synchronize canonical catalogue records."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SyncedGenre:
    """A genre normalized from an upstream catalogue provider."""

    id: int
    name: str


@dataclass(frozen=True)
class SyncedTitle:
    """Metadata normalized before it is persisted as a canonical title."""

    tmdb_id: int
    title_type: str
    title: str
    original_title: str | None
    overview: str | None
    original_language: str
    release_date: date | None
    runtime_minutes: int | None
    poster_path: str | None
    backdrop_path: str | None
    popularity: float
    vote_average: float | None
    tagline: str | None
    cast: list[dict[str, str]]
    creators: list[str]
    keywords: list[str]
    genres: list[SyncedGenre]
    imdb_id: str | None
