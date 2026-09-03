"""Import and index a selected TMDB title on demand."""

from typing import Protocol

from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.ports import CatalogueMetadataGateway, CatalogueRepository


class TitleIndexer(Protocol):
    def index(self, title: TitleDetails) -> None: ...


class ImportTmdbTitle:
    def __init__(
        self,
        repository: CatalogueRepository,
        gateway: CatalogueMetadataGateway,
        indexer: TitleIndexer,
    ) -> None:
        self._repository = repository
        self._gateway = gateway
        self._indexer = indexer

    def execute(self, title_type: str, tmdb_id: int) -> TitleDetails | None:
        self._repository.upsert(self._gateway.title_details(title_type, tmdb_id))
        title = self._repository.details_by_tmdb(title_type, tmdb_id)
        if title is None:
            return None
        self._indexer.index(title)
        return title
