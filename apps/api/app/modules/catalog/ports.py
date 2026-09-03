"""Interfaces required by catalogue use cases."""

from typing import Protocol

from app.modules.catalog.domain import (
    CatalogueFacets,
    CataloguePage,
    CatalogueQuery,
    ExternalTitle,
    TitleDetails,
)
from app.modules.catalog.sync import SyncedTitle


class CatalogueRepository(Protocol):
    def search(self, query: CatalogueQuery) -> CataloguePage: ...

    def details(self, title_id: str) -> TitleDetails | None: ...

    def facets(self) -> CatalogueFacets: ...

    def upsert(self, synced_title: SyncedTitle) -> bool: ...

    def details_by_tmdb(self, title_type: str, tmdb_id: int) -> TitleDetails | None: ...

    def all_details(self) -> list[TitleDetails]: ...


class CatalogueMetadataGateway(Protocol):
    def popular_ids(self, title_type: str, page: int) -> list[int]: ...

    def title_details(self, title_type: str, tmdb_id: int) -> SyncedTitle: ...

    def search_titles(self, query: str, title_type: str | None) -> list[ExternalTitle]: ...
