"""Ports required for semantic title recommendations."""

from typing import Protocol
from uuid import UUID

from app.modules.catalog.domain import TitleDetails
from app.modules.recommendations.domain import RatedTitle


class SimilarityCatalogue(Protocol):
    def details(self, title_id: str) -> TitleDetails | None: ...


class SemanticTitleIndex(Protocol):
    def index(self, title: TitleDetails) -> None: ...

    def similar(self, source: TitleDetails, limit: int) -> list[str]: ...

    def embed(self, title: TitleDetails) -> list[float]: ...

    def search_profile(
        self, vector: list[float], title_type: str, limit: int, excluded_ids: set[str]
    ) -> list[str]: ...


class PersonalRecommendationRepository(SimilarityCatalogue, Protocol):
    def rated_titles(self, user_id: UUID) -> list[RatedTitle]: ...

    def excluded_title_ids(self, user_id: UUID) -> set[str]: ...
