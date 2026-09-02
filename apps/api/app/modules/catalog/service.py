"""Public catalogue application service contracts."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class CatalogueQuery:
    """Validated criteria for browsing canonical catalogue titles."""

    title_query: str | None
    title_type: str | None
    genre: str | None
    language: str | None
    year: int | None
    page: int
    page_size: int = 24


@dataclass(frozen=True)
class TitleSummary:
    """A compact title representation for catalogue result cards."""

    id: str
    title: str
    title_type: str
    release_date: date | None
    original_language: str
    poster_path: str | None
    popularity: float
    genres: list[str]


@dataclass(frozen=True)
class CataloguePage:
    """A single page of searchable catalogue titles."""

    items: list[TitleSummary]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class TitleDetails(TitleSummary):
    """The complete persisted metadata rendered on a title page."""

    overview: str | None
    runtime_minutes: int | None
    backdrop_path: str | None
    vote_average: float | None
    tagline: str | None
    cast: list[dict[str, str]]
    creators: list[str]
    keywords: list[str]


@dataclass(frozen=True)
class CatalogueFacets:
    """Selectable values available in the local canonical catalogue."""

    genres: list[str]
    languages: list[str]
    years: list[int]


class CatalogueService(Protocol):
    """The catalogue module interface used by HTTP routes and CLI workflows."""

    def search(self, query: CatalogueQuery) -> CataloguePage:
        """Return canonical titles matching the visitor's browse criteria."""

    def details(self, title_id: str) -> TitleDetails | None:
        """Return one canonical title or no match."""

    def facets(self) -> CatalogueFacets:
        """Return current catalogue filter values."""
