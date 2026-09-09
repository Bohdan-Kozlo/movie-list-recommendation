"""Ports required for semantic title recommendations."""

from typing import Protocol
from uuid import UUID

from app.modules.catalog.domain import TitleDetails
from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.tonight import TonightPreferences


class SimilarityCatalogue(Protocol):
    def details(self, title_id: str) -> TitleDetails | None: ...


class SemanticTitleIndex(Protocol):
    def index(self, title: TitleDetails) -> None: ...

    def similar(self, source: TitleDetails, limit: int) -> list[str]: ...

    def embed(self, title: TitleDetails) -> list[float]: ...

    def vectors(self, title_ids: list[str]) -> dict[str, list[float]]: ...

    def search_profile(
        self, vector: list[float], title_type: str, limit: int, excluded_ids: set[str]
    ) -> list[str]: ...


class PersonalRecommendationRepository(SimilarityCatalogue, Protocol):
    def rated_titles(self, user_id: UUID) -> list[RatedTitle]: ...

    def excluded_title_ids(self, user_id: UUID) -> set[str]: ...


class IndexableCatalogue(Protocol):
    def all_details(self) -> list[TitleDetails]: ...


class TonightRepository(PersonalRecommendationRepository, Protocol):
    def eligible_title_ids(self, preferences: TonightPreferences) -> set[str]: ...


class TonightIndex(SemanticTitleIndex, Protocol):
    def search_tonight(
        self, vector: list[float], title_type: str, eligible_ids: set[str], limit: int
    ) -> list[str]: ...


class IndexableSemanticTitleIndex(Protocol):
    def existing_ids(self, title_ids: list[str]) -> set[str]: ...

    def index(self, title: TitleDetails) -> None: ...
