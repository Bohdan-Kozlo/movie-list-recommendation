"""Index canonical titles after catalogue synchronization."""

from typing import Protocol

from app.modules.catalog.domain import TitleDetails
from app.modules.recommendations.ports import SemanticTitleIndex


class IndexableCatalogue(Protocol):
    def all_details(self) -> list[TitleDetails]: ...


class IndexCatalogue:
    def __init__(self, catalogue: IndexableCatalogue, index: SemanticTitleIndex) -> None:
        self._catalogue = catalogue
        self._index = index

    def execute(self) -> int:
        titles = self._catalogue.all_details()
        for title in titles:
            self._index.index(title)
        return len(titles)
