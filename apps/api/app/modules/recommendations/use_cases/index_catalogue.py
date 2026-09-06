"""Index canonical titles that do not yet have derived vectors."""

from app.modules.recommendations.domain import IndexReport
from app.modules.recommendations.ports import IndexableCatalogue, IndexableSemanticTitleIndex


class IndexCatalogue:
    def __init__(self, catalogue: IndexableCatalogue, index: IndexableSemanticTitleIndex) -> None:
        self._catalogue = catalogue
        self._index = index

    def execute(self, only_missing: bool = True, batch_size: int = 100) -> IndexReport:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1.")
        titles = self._catalogue.all_details()
        indexed = 0
        for offset in range(0, len(titles), batch_size):
            batch = titles[offset : offset + batch_size]
            existing = (
                self._index.existing_ids([title.id for title in batch]) if only_missing else set()
            )
            for title in batch:
                if title.id not in existing:
                    self._index.index(title)
                    indexed += 1
        skipped = len(titles) - indexed if only_missing else 0
        return IndexReport(scanned=len(titles), indexed=indexed, skipped=skipped)
