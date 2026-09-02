"""Catalogue browse use case."""

from app.modules.catalog.domain import CataloguePage, CatalogueQuery
from app.modules.catalog.ports import CatalogueRepository


class SearchCatalogue:
    def __init__(self, repository: CatalogueRepository) -> None:
        self._repository = repository

    def execute(self, query: CatalogueQuery) -> CataloguePage:
        return self._repository.search(query)
