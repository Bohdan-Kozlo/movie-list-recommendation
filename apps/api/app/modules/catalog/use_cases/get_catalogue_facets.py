"""Catalogue filter-facets use case."""

from app.modules.catalog.domain import CatalogueFacets
from app.modules.catalog.ports import CatalogueRepository


class GetCatalogueFacets:
    def __init__(self, repository: CatalogueRepository) -> None:
        self._repository = repository

    def execute(self) -> CatalogueFacets:
        return self._repository.facets()
