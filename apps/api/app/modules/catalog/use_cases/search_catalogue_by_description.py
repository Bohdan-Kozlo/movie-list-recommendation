"""Find canonical catalogue titles by semantic description."""

from app.modules.catalog.domain import TitleSummary
from app.modules.catalog.ports import CatalogueRepository, SemanticDescriptionIndex


class SearchCatalogueByDescription:
    """Resolve ranked local vector matches into canonical catalogue summaries."""

    def __init__(
        self, repository: CatalogueRepository, semantic_index: SemanticDescriptionIndex
    ) -> None:
        self._repository = repository
        self._semantic_index = semantic_index

    def execute(self, description: str, title_type: str | None) -> list[TitleSummary]:
        title_ids = self._semantic_index.search_description(
            description, title_type=title_type, limit=24
        )
        return [
            TitleSummary(
                id=title.id,
                title=title.title,
                title_type=title.title_type,
                release_date=title.release_date,
                original_language=title.original_language,
                poster_path=title.poster_path,
                popularity=title.popularity,
                genres=title.genres,
            )
            for title_id in title_ids[:24]
            if (title := self._repository.details(title_id)) is not None
        ]
