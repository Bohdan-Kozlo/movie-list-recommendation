from datetime import date
from types import SimpleNamespace

from app.main import app
from app.modules.catalog.dependencies import (
    get_catalogue_use_cases,
    get_semantic_description_search_use_case,
)
from app.modules.catalog.domain import (
    CatalogueFacets,
    CataloguePage,
    CatalogueQuery,
    TitleDetails,
    TitleSummary,
)
from fastapi.testclient import TestClient


class FakeCatalogueService:
    def search(self, query: CatalogueQuery) -> CataloguePage:
        assert query.title_query == "dune"
        assert query.title_type == "movie"
        assert query.genre == "Science Fiction"
        assert query.language == "en"
        assert query.year == 2021
        assert query.page == 2
        return CataloguePage(
            items=[
                TitleSummary(
                    id="dune-id",
                    title="Dune",
                    title_type="movie",
                    release_date=date(2021, 9, 15),
                    original_language="en",
                    poster_path="/dune.jpg",
                    popularity=100.0,
                    genres=["Science Fiction"],
                )
            ],
            total=25,
            page=2,
            page_size=24,
        )

    def details(self, title_id: str) -> TitleDetails | None:
        if title_id != "dune-id":
            return None
        return TitleDetails(
            **_dune_summary().__dict__,
            overview="A noble family travels to Arrakis.",
            runtime_minutes=155,
            backdrop_path="/dune-backdrop.jpg",
            vote_average=8.2,
            tagline="It begins.",
            cast=[{"name": "Timothée Chalamet", "character": "Paul Atreides"}],
            creators=["Denis Villeneuve"],
            keywords=["desert", "space"],
        )

    def facets(self) -> CatalogueFacets:
        return CatalogueFacets(genres=["Science Fiction"], languages=["en"], years=[2021])


def _dune_summary() -> TitleSummary:
    return TitleSummary(
        id="dune-id",
        title="Dune",
        title_type="movie",
        release_date=date(2021, 9, 15),
        original_language="en",
        poster_path="/dune.jpg",
        popularity=100.0,
        genres=["Science Fiction"],
    )


def test_visitors_can_search_filter_and_paginate_catalogue_titles() -> None:
    app.dependency_overrides[get_catalogue_use_cases] = _use_cases

    response = TestClient(app).get(
        "/catalogue/titles",
        params={
            "query": "dune",
            "type": "movie",
            "genre": "Science Fiction",
            "language": "en",
            "year": 2021,
            "page": 2,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": "dune-id",
                "title": "Dune",
                "type": "movie",
                "releaseDate": "2021-09-15",
                "originalLanguage": "en",
                "posterPath": "/dune.jpg",
                "popularity": 100.0,
                "genres": ["Science Fiction"],
            }
        ],
        "total": 25,
        "page": 2,
        "pageSize": 24,
    }


def test_visitors_can_open_title_details_and_catalogue_facets() -> None:
    app.dependency_overrides[get_catalogue_use_cases] = _use_cases

    detail_response = TestClient(app).get("/catalogue/titles/dune-id")
    facet_response = TestClient(app).get("/catalogue/filters")

    app.dependency_overrides.clear()

    assert detail_response.status_code == 200
    assert detail_response.json()["overview"] == "A noble family travels to Arrakis."
    assert detail_response.json()["cast"] == [
        {"name": "Timothée Chalamet", "character": "Paul Atreides"}
    ]
    assert facet_response.json() == {
        "genres": ["Science Fiction"],
        "languages": ["en"],
        "years": [2021],
    }


def test_visitors_can_semantically_search_descriptions_with_optional_format() -> None:
    search = FakeSemanticDescriptionSearch([_dune_summary(), _bear_summary()])
    app.dependency_overrides[get_semantic_description_search_use_case] = lambda: search

    all_formats = TestClient(app).post(
        "/catalogue/semantic-search", json={"description": "  tense desert politics  "}
    )
    movies = TestClient(app).post(
        "/catalogue/semantic-search",
        json={"description": "tense desert politics", "type": "movie"},
    )
    series = TestClient(app).post(
        "/catalogue/semantic-search",
        json={"description": "tense desert politics", "type": "tv"},
    )

    app.dependency_overrides.clear()

    assert all_formats.status_code == 200
    assert [item["id"] for item in all_formats.json()["items"]] == ["dune-id", "bear-id"]
    assert movies.status_code == 200
    assert [item["id"] for item in movies.json()["items"]] == ["dune-id"]
    assert series.status_code == 200
    assert [item["id"] for item in series.json()["items"]] == ["bear-id"]
    assert search.requests == [
        ("tense desert politics", None),
        ("tense desert politics", "movie"),
        ("tense desert politics", "tv"),
    ]


def test_semantic_description_search_validates_the_trimmed_description_and_type() -> None:
    app.dependency_overrides[get_semantic_description_search_use_case] = lambda: (
        FakeSemanticDescriptionSearch([])
    )
    client = TestClient(app)

    too_short = client.post("/catalogue/semantic-search", json={"description": "  ab  "})
    too_long = client.post("/catalogue/semantic-search", json={"description": "x" * 501})
    unsupported_type = client.post(
        "/catalogue/semantic-search", json={"description": "space opera", "type": "film"}
    )
    unexpected_field = client.post(
        "/catalogue/semantic-search", json={"description": "space opera", "unexpected": True}
    )
    lower_boundary = client.post("/catalogue/semantic-search", json={"description": "  abc  "})
    upper_boundary = client.post("/catalogue/semantic-search", json={"description": "x" * 500})

    app.dependency_overrides.clear()

    assert too_short.status_code == 422
    assert too_long.status_code == 422
    assert unsupported_type.status_code == 422
    assert unexpected_field.status_code == 422
    assert lower_boundary.status_code == 200
    assert upper_boundary.status_code == 200


def test_semantic_description_search_preserves_rank_skips_stale_titles_and_limits_results() -> None:
    titles = [
        TitleSummary(
            id=f"title-{index}",
            title=f"Title {index}",
            title_type="movie",
            release_date=None,
            original_language="en",
            poster_path=None,
            popularity=float(index),
            genres=[],
        )
        for index in range(25)
    ]
    app.dependency_overrides[get_semantic_description_search_use_case] = lambda: (
        FakeSemanticDescriptionSearch(titles)
    )

    response = TestClient(app).post(
        "/catalogue/semantic-search", json={"description": "mystery in a coastal town"}
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [
        f"title-{index}" for index in range(24)
    ]


def test_semantic_description_search_returns_empty_results_and_hides_provider_details() -> None:
    app.dependency_overrides[get_semantic_description_search_use_case] = lambda: (
        FakeSemanticDescriptionSearch([])
    )
    empty = TestClient(app).post(
        "/catalogue/semantic-search", json={"description": "quiet village drama"}
    )
    app.dependency_overrides[get_semantic_description_search_use_case] = lambda: (
        FailingSemanticDescriptionSearch()
    )
    unavailable = TestClient(app).post(
        "/catalogue/semantic-search", json={"description": "quiet village drama"}
    )

    app.dependency_overrides.clear()

    assert empty.status_code == 200
    assert empty.json() == {"items": []}
    assert unavailable.status_code == 503
    assert unavailable.json() == {"detail": "Description search is unavailable."}


class FakeSemanticDescriptionSearch:
    def __init__(self, titles: list[TitleSummary]) -> None:
        self._titles = titles
        self.requests: list[tuple[str, str | None]] = []

    def execute(self, description: str, title_type: str | None) -> list[TitleSummary]:
        self.requests.append((description, title_type))
        return [
            title for title in self._titles if title_type is None or title.title_type == title_type
        ][:24]


class FailingSemanticDescriptionSearch:
    def execute(self, description: str, title_type: str | None) -> list[TitleSummary]:
        raise RuntimeError("Ollama connection details must not leak")


def _bear_summary() -> TitleSummary:
    return TitleSummary(
        id="bear-id",
        title="The Bear",
        title_type="tv",
        release_date=date(2022, 6, 23),
        original_language="en",
        poster_path="/bear.jpg",
        popularity=90.0,
        genres=["Drama"],
    )


def _use_cases() -> SimpleNamespace:
    service = FakeCatalogueService()
    return SimpleNamespace(
        search_catalogue=SimpleNamespace(execute=service.search),
        get_title_details=SimpleNamespace(execute=service.details),
        get_catalogue_facets=SimpleNamespace(execute=service.facets),
    )
