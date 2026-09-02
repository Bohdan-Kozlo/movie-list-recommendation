"""Repeatable TMDB synchronization use case."""

from dataclasses import dataclass

from app.modules.catalog.ports import CatalogueMetadataGateway, CatalogueRepository


@dataclass(frozen=True)
class SyncReport:
    created: int
    updated: int


class SynchronizeCatalogue:
    def __init__(self, repository: CatalogueRepository) -> None:
        self._repository = repository

    def execute(
        self, gateway: CatalogueMetadataGateway, title_types: list[str], pages: int
    ) -> SyncReport:
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
