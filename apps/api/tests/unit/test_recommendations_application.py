from datetime import date

from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.use_cases import ImportTmdbTitle
from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.use_cases import (
    GetPersonalRecommendations,
    GetSimilarTitles,
    IndexCatalogue,
)


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


class FakePersonalIndex(FakeSemanticIndex):
    def __init__(self, identifiers_by_type: dict[str, list[str]]) -> None:
        super().__init__([])
        self.identifiers_by_type = identifiers_by_type

    def embed(self, source: TitleDetails) -> list[float]:
        return [float(len(source.title)), 1.0]

    def search_profile(
        self, vector: list[float], title_type: str, limit: int, excluded_ids: set[str]
    ) -> list[str]:
        assert limit == 60
        assert vector
        assert excluded_ids
        return self.identifiers_by_type[title_type]


class FakePersonalRepository:
    def __init__(
        self,
        ratings: list[RatedTitle],
        titles: list[TitleDetails],
        excluded: set[str] | None = None,
    ) -> None:
        self._ratings = ratings
        self._titles = {title.id: title for title in titles}
        self._excluded = excluded or set()

    def rated_titles(self, user_id: object) -> list[RatedTitle]:
        return self._ratings

    def excluded_title_ids(self, user_id: object) -> set[str]:
        return self._excluded

    def details(self, title_id: str) -> TitleDetails | None:
        return self._titles.get(title_id)


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


def test_personal_recommendations_exclude_library_titles_and_explain_rating() -> None:
    loved = title("loved", "Loved", genres=["Science Fiction"], keywords=[])
    watched = title("watched", "Watched", genres=["Science Fiction"], keywords=[])
    movie = title("movie", "Movie", genres=["Science Fiction"], keywords=[])
    series = title("series", "Series", genres=["Drama"], keywords=[])
    series = TitleDetails(**{**series.__dict__, "title_type": "tv"})
    repository = FakePersonalRepository(
        [RatedTitle(loved, 4.5)], [loved, watched, movie, series], {"watched", "not-interested"}
    )
    index = FakePersonalIndex({"movie": ["watched", "movie"], "tv": ["series"]})

    results = GetPersonalRecommendations(repository, index).execute(object())

    assert [item.title.id for item in results.movies] == ["movie"]
    assert [item.title.id for item in results.tv_series] == ["series"]
    assert results.movies[0].reason == "Matches the Science Fiction genre in Loved, rated 4.5/5."


def test_personal_recommendations_skip_neutral_profile_and_near_duplicates() -> None:
    neutral = title("neutral", "Neutral", genres=["Drama"], keywords=[])
    first = title("first", "First", genres=["Drama", "Mystery"], keywords=[], creators=["Maker"])
    duplicate = title(
        "duplicate", "Duplicate", genres=["Drama", "Mystery"], keywords=[], creators=["Maker"]
    )
    repository = FakePersonalRepository([RatedTitle(neutral, 3.0)], [neutral, first, duplicate])
    index = FakePersonalIndex({"movie": ["first", "duplicate"], "tv": []})

    empty = GetPersonalRecommendations(repository, index).execute(object())

    assert empty.movies == []
    assert empty.tv_series == []


def test_personal_recommendations_keep_only_one_near_duplicate() -> None:
    loved = title("loved", "Loved", genres=["Drama"], keywords=[])
    first = title("first", "First", genres=["Drama", "Mystery"], keywords=[], creators=["Maker"])
    duplicate = title(
        "duplicate", "Duplicate", genres=["Drama", "Mystery"], keywords=[], creators=["Maker"]
    )
    repository = FakePersonalRepository([RatedTitle(loved, 4.0)], [loved, first, duplicate])
    index = FakePersonalIndex({"movie": ["first", "duplicate"], "tv": []})

    results = GetPersonalRecommendations(repository, index).execute(object())

    assert [item.title.id for item in results.movies] == ["first"]


def test_personal_recommendations_use_a_negative_rating_when_no_positive_rating_exists() -> None:
    disliked = title("disliked", "Disliked", genres=["Horror"], keywords=[])
    candidate = title("candidate", "Candidate", genres=["Comedy"], keywords=[])
    repository = FakePersonalRepository([RatedTitle(disliked, 2.0)], [disliked, candidate])
    index = FakePersonalIndex({"movie": ["candidate"], "tv": []})

    results = GetPersonalRecommendations(repository, index).execute(object())

    assert [item.title.id for item in results.movies] == ["candidate"]
    assert results.movies[0].reason == "Balances against your 2.0/5 rating for Disliked."


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
