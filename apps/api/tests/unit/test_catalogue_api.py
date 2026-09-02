from datetime import date
from types import SimpleNamespace

from app.main import app
from app.modules.catalog.dependencies import get_catalogue_use_cases
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


def _use_cases() -> SimpleNamespace:
    service = FakeCatalogueService()
    return SimpleNamespace(
        search_catalogue=SimpleNamespace(execute=service.search),
        get_title_details=SimpleNamespace(execute=service.details),
        get_catalogue_facets=SimpleNamespace(execute=service.facets),
    )
