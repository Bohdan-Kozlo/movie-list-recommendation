from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.adapters.tmdb.client import TmdbNotFoundError
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.catalog.dependencies import get_import_tmdb_title_use_case
from app.modules.catalog.domain import TitleDetails, TitleSummary
from app.modules.onboarding.dependencies import (
    get_onboarding_use_cases,
    require_completed_onboarding,
)
from app.modules.recommendations.dependencies import (
    get_personal_recommendations_use_case,
    get_similar_titles_use_case,
)
from app.modules.recommendations.domain import (
    PersonalRecommendation,
    PersonalRecommendations,
    RatedTitle,
    SimilarTitle,
)
from app.modules.recommendations.use_cases import GetPersonalRecommendations


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

    app.dependency_overrides[get_import_tmdb_title_use_case] = FailingImport
    response = TestClient(app).post("/catalogue/tmdb-titles/movie/999")
    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_personal_recommendations_require_completed_onboarding_and_split_types() -> None:
    user = SimpleNamespace(id="user")

    class FakeUseCase:
        def execute(self, user_id: str) -> PersonalRecommendations:
            assert user_id == "user"
            item = similar_title()
            return PersonalRecommendations(
                movies=[PersonalRecommendation(item.title, item.reason)], tv_series=[]
            )

    app.dependency_overrides[require_completed_onboarding] = lambda: user
    app.dependency_overrides[get_personal_recommendations_use_case] = FakeUseCase
    response = TestClient(app).get("/recommendations/personal")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["tvSeries"] == {"items": []}
    assert response.json()["movies"]["items"][0]["reason"] == "Shares the Science Fiction genre."


def test_personal_recommendations_require_authentication() -> None:
    response = TestClient(app).get("/recommendations/personal")

    assert response.status_code == 401


def test_personal_recommendations_require_completed_taste_onboarding() -> None:
    user = SimpleNamespace(id="user")
    incomplete_onboarding = SimpleNamespace(
        is_onboarding_complete=SimpleNamespace(execute=lambda user_id: False)
    )
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_onboarding_use_cases] = lambda: incomplete_onboarding
    response = TestClient(app).get("/recommendations/personal")
    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_personal_recommendations_endpoint_applies_content_rules() -> None:
    def title(identifier: str, name: str, title_type: str, genres: list[str]) -> TitleDetails:
        return TitleDetails(
            id=identifier,
            title=name,
            title_type=title_type,
            release_date=date(2024, 1, 1),
            original_language="en",
            poster_path=None,
            popularity=1.0,
            genres=genres,
            overview=None,
            runtime_minutes=None,
            backdrop_path=None,
            vote_average=None,
            tagline=None,
            cast=[],
            creators=[],
            keywords=[],
        )

    loved = title("loved", "Loved", "movie", ["Drama"])
    watched = title("watched", "Watched", "movie", ["Drama"])
    movie = title("movie", "Movie", "movie", ["Drama"])
    series = title("series", "Series", "tv", ["Comedy"])

    class Repository:
        def rated_titles(self, user_id: object) -> list[RatedTitle]:
            return [RatedTitle(loved, 4.5)]

        def excluded_title_ids(self, user_id: object) -> set[str]:
            return {"watched", "not-interested"}

        def details(self, title_id: str) -> TitleDetails | None:
            return {item.id: item for item in [loved, watched, movie, series]}.get(title_id)

    class Index:
        def embed(self, source: TitleDetails) -> list[float]:
            return [1.0, 1.0]

        def vectors(self, title_ids: list[str]) -> dict[str, list[float]]:
            return {}

        def search_profile(
            self, vector: list[float], title_type: str, limit: int, excluded_ids: set[str]
        ) -> list[str]:
            assert {"loved", "watched", "not-interested"}.issubset(excluded_ids)
            return {"movie": ["watched", "movie"], "tv": ["series"]}[title_type]

    app.dependency_overrides[require_completed_onboarding] = lambda: SimpleNamespace(id="user")
    app.dependency_overrides[get_personal_recommendations_use_case] = lambda: (
        GetPersonalRecommendations(Repository(), Index())
    )
    response = TestClient(app).get("/recommendations/personal")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["movies"]["items"]] == ["movie"]
    assert [item["type"] for item in response.json()["movies"]["items"]] == ["movie"]
    assert [item["type"] for item in response.json()["tvSeries"]["items"]] == ["tv"]
    assert response.json()["movies"]["items"][0]["reason"] == (
        "Matches the Drama genre in Loved, rated 4.5/5."
    )
