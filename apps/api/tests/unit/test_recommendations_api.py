from datetime import date
from types import SimpleNamespace

from app.adapters.tmdb.client import TmdbNotFoundError
from app.main import app
from app.modules.catalog.dependencies import get_external_catalogue_use_cases
from app.modules.catalog.domain import TitleSummary
from app.modules.recommendations.dependencies import get_similar_titles_use_case
from app.modules.recommendations.domain import SimilarTitle
from fastapi.testclient import TestClient


def similar_title() -> SimilarTitle:
    return SimilarTitle(
        title=TitleSummary(
            id="4f9c78c0-ff51-4cd2-a922-fa304e1713d4",
            title="Arrival",
            title_type="movie",
            release_date=date(2016, 11, 11),
            original_language="en",
            poster_path="/arrival.jpg",
            popularity=10.0,
            genres=["Science Fiction"],
        ),
        reason="Shares the Science Fiction genre.",
    )


def test_similar_titles_are_public_and_include_a_factual_reason() -> None:
    class FakeUseCase:
        def execute(self, title_id: str) -> list[SimilarTitle]:
            assert title_id == "source"
            return [similar_title()]

    app.dependency_overrides[get_similar_titles_use_case] = FakeUseCase
    response = TestClient(app).get("/recommendations/titles/source/similar")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["reason"] == "Shares the Science Fiction genre."
    assert response.json()["items"][0]["type"] == "movie"


def test_missing_title_returns_not_found() -> None:
    class FakeUseCase:
        def execute(self, title_id: str) -> None:
            return None

    app.dependency_overrides[get_similar_titles_use_case] = FakeUseCase
    response = TestClient(app).get("/recommendations/titles/missing/similar")
    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_unknown_tmdb_title_returns_not_found_during_import() -> None:
    class FailingImport:
        def execute(self, title_type: str, tmdb_id: int) -> None:
            raise TmdbNotFoundError

    app.dependency_overrides[get_external_catalogue_use_cases] = lambda: SimpleNamespace(
        import_tmdb_title=FailingImport()
    )
    response = TestClient(app).post("/catalogue/tmdb-titles/movie/999")
    app.dependency_overrides.clear()

    assert response.status_code == 404
