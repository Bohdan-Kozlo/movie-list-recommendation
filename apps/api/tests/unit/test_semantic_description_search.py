from datetime import date

from app.adapters.semantic import SemanticTitleIndexer
from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.use_cases import SearchCatalogueByDescription


def test_description_search_preserves_vector_rank_and_skips_stale_catalogue_records() -> None:
    first = _title("first", "First match")
    second = _title("second", "Second match")

    class Catalogue:
        def details(self, title_id: str) -> TitleDetails | None:
            return {first.id: first, second.id: second}.get(title_id)

    class Index:
        def search_description(
            self, description: str, title_type: str | None, limit: int
        ) -> list[str]:
            assert description == "small coastal town mystery"
            assert title_type == "movie"
            assert limit == 24
            return [first.id, "stale", second.id]

    results = SearchCatalogueByDescription(Catalogue(), Index()).execute(
        "small coastal town mystery", "movie"
    )

    assert [item.id for item in results] == [first.id, second.id]


def test_semantic_adapter_embeds_the_query_and_passes_type_filter_and_limit() -> None:
    class Embeddings:
        def __init__(self) -> None:
            self.texts: list[str] = []

        def embed(self, text: str) -> list[float]:
            self.texts.append(text)
            return [1.0, 0.0]

    class Vectors:
        def __init__(self) -> None:
            self.request: tuple[list[float], int, str | None] | None = None

        def search(
            self, vector: list[float], limit: int, title_type: str | None = None
        ) -> list[str]:
            self.request = (vector, limit, title_type)
            return ["first", "second"]

    embeddings = Embeddings()
    vectors = Vectors()

    results = SemanticTitleIndexer(embeddings, vectors).search_description(
        "sunlit road trip", "tv", 24
    )

    assert results == ["first", "second"]
    assert embeddings.texts == ["sunlit road trip"]
    assert vectors.request == ([1.0, 0.0], 24, "tv")


def _title(identifier: str, title: str) -> TitleDetails:
    return TitleDetails(
        id=identifier,
        title=title,
        title_type="movie",
        release_date=date(2024, 1, 1),
        original_language="en",
        poster_path=None,
        popularity=1.0,
        genres=["Mystery"],
        overview="A mystery.",
        runtime_minutes=100,
        backdrop_path=None,
        vote_average=None,
        tagline=None,
        cast=[],
        creators=[],
        keywords=[],
    )
