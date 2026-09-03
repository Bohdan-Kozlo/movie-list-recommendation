"""Ports required for semantic title recommendations."""

from typing import Protocol

from app.modules.catalog.domain import TitleDetails


class SimilarityCatalogue(Protocol):
    def details(self, title_id: str) -> TitleDetails | None: ...


class SemanticTitleIndex(Protocol):
    def index(self, title: TitleDetails) -> None: ...

    def similar(self, source: TitleDetails, limit: int) -> list[str]: ...
