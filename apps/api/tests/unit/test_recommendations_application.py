from datetime import date

from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.use_cases import ImportTmdbTitle
from app.modules.recommendations.use_cases import GetSimilarTitles, IndexCatalogue


def title(
    identifier: str,
    name: str,
    *,
    genres: list[str],
    keywords: list[str],
    creators: list[str] | None = None,
) -> TitleDetails:
    return TitleDetails(
        id=identifier,
        title=name,
        title_type="movie",
        release_date=date(2024, 1, 1),
        original_language="en",
        poster_path=None,
        popularity=1.0,
        genres=genres,
        overview="A story about distant worlds.",
        runtime_minutes=100,
        backdrop_path=None,
        vote_average=None,
        tagline=None,
        cast=[],
        creators=creators or [],
        keywords=keywords,
    )


class FakeCatalogue:
    def __init__(self, titles: list[TitleDetails]) -> None:
        self._titles = {item.id: item for item in titles}

    def details(self, title_id: str) -> TitleDetails | None:
        return self._titles.get(title_id)


class FakeSemanticIndex:
    def __init__(self, identifiers: list[str]) -> None:
        self.identifiers = identifiers
        self.source: TitleDetails | None = None
        self.indexed: list[str] = []

    def similar(self, source: TitleDetails, limit: int) -> list[str]:
        self.source = source
        assert limit == 12
        return self.identifiers

    def index(self, title: TitleDetails) -> None:
        self.indexed.append(title.id)


def test_similar_titles_preserve_semantic_rank_and_explain_shared_metadata() -> None:
    source = title("source", "Source", genres=["Science Fiction"], keywords=["space"])
    genre_match = title("genre", "Genre match", genres=["Science Fiction"], keywords=[])
    keyword_match = title("keyword", "Keyword match", genres=[], keywords=["space"])
    index = FakeSemanticIndex(["genre", "keyword", "missing"])

    results = GetSimilarTitles(FakeCatalogue([source, genre_match, keyword_match]), index).execute(
        "source"
    )

    assert [item.title.id for item in results] == ["genre", "keyword"]
    assert [item.reason for item in results] == [
        "Shares the Science Fiction genre.",
        "Shares the space theme.",
    ]
    assert index.source == source


def test_similar_titles_use_a_truthful_semantic_fallback_reason() -> None:
    source = title("source", "Source", genres=["Drama"], keywords=[])
    match = title("match", "Match", genres=["Comedy"], keywords=[])

    result = GetSimilarTitles(FakeCatalogue([source, match]), FakeSemanticIndex(["match"])).execute(
        "source"
    )

    assert result[0].reason == "Similar in synopsis and indexed metadata."


def test_catalogue_sync_indexer_can_rebuild_all_derived_vectors() -> None:
    source = title("source", "Source", genres=["Drama"], keywords=[])
    match = title("match", "Match", genres=["Comedy"], keywords=[])

    class IndexableCatalogue:
        def all_details(self) -> list[TitleDetails]:
            return [source, match]

    index = FakeSemanticIndex([])

    assert IndexCatalogue(IndexableCatalogue(), index).execute() == 2
    assert index.indexed == ["source", "match"]


def test_on_demand_import_persists_then_indexes_the_canonical_title() -> None:
    imported = title("imported", "Imported", genres=["Drama"], keywords=[])

    class FakeRepository:
        def __init__(self) -> None:
            self.upserted = False

        def upsert(self, value: object) -> bool:
            self.upserted = True
            return True

        def details_by_tmdb(self, title_type: str, tmdb_id: int) -> TitleDetails | None:
            assert self.upserted
            assert (title_type, tmdb_id) == ("tv", 44)
            return imported

    class FakeGateway:
        def title_details(self, title_type: str, tmdb_id: int) -> object:
            assert (title_type, tmdb_id) == ("tv", 44)
            return object()

    repository = FakeRepository()
    index = FakeSemanticIndex([])

    result = ImportTmdbTitle(repository, FakeGateway(), index).execute("tv", 44)

    assert result == imported
    assert index.indexed == ["imported"]
