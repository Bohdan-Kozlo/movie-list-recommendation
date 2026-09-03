"""Find TMDB titles that are not yet part of the canonical catalogue."""

from app.modules.catalog.domain import ExternalTitle
from app.modules.catalog.ports import CatalogueMetadataGateway


class SearchExternalTitles:
    def __init__(self, gateway: CatalogueMetadataGateway) -> None:
        self._gateway = gateway

    def execute(self, query: str, title_type: str | None) -> list[ExternalTitle]:
        return self._gateway.search_titles(query, title_type)
