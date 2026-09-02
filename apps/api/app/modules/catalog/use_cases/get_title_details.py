"""Catalogue title-detail use case."""

from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.ports import CatalogueRepository


class GetTitleDetails:
    def __init__(self, repository: CatalogueRepository) -> None:
        self._repository = repository

    def execute(self, title_id: str) -> TitleDetails | None:
        return self._repository.details(title_id)
