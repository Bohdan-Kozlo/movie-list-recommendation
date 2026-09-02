"""Catalogue use cases combining persistence and TMDB adapters."""

from dataclasses import dataclass
from typing import Protocol

from app.modules.catalog.service import CatalogueFacets, CataloguePage, CatalogueQuery, TitleDetails
from app.modules.catalog.sync import CatalogueMetadataGateway, SyncedTitle


class CatalogueRepository(Protocol):
    """Persistence operations needed by catalogue use cases."""

    def search(self, query: CatalogueQuery) -> CataloguePage:
        """Return local titles matching a browse query."""

    def details(self, title_id: str) -> TitleDetails | None:
        """Return one local title if it exists."""

    def facets(self) -> CatalogueFacets:
        """Return local filter values."""

    def upsert(self, synced_title: SyncedTitle) -> bool:
        """Persist a normalized TMDB title and report whether it was created."""


@dataclass(frozen=True)
class SyncReport:
    """Observable outcome of one repeatable catalogue synchronization."""

    created: int
    updated: int


class CatalogueApplicationService:
    """The public catalogue module interface and synchronization workflow."""

    def __init__(self, repository: CatalogueRepository) -> None:
        self._repository = repository

    def search(self, query: CatalogueQuery) -> CataloguePage:
        """Browse canonical titles."""
        return self._repository.search(query)

    def details(self, title_id: str) -> TitleDetails | None:
        """Open a canonical title's details."""
        return self._repository.details(title_id)

    def facets(self) -> CatalogueFacets:
        """List filters derived from canonical records."""
        return self._repository.facets()

    def synchronize(
        self, gateway: CatalogueMetadataGateway, title_types: list[str], pages: int
    ) -> SyncReport:
        """Upsert each title from a deterministic set of TMDB discovery pages."""
        created = 0
        updated = 0
        for title_type in title_types:
            for page in range(1, pages + 1):
                for tmdb_id in gateway.popular_ids(title_type, page):
                    title = gateway.title_details(title_type, tmdb_id)
                    if self._repository.upsert(title):
                        created += 1
                    else:
                        updated += 1
        return SyncReport(created=created, updated=updated)
