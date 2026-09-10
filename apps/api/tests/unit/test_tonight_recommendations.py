"""Exercise tonight's HTTP contract, canonical filters and real local vector search."""

from dataclasses import replace
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient as QdrantSdkClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.adapters.postgres.recommendation_repository import (
    SqlAlchemyPersonalRecommendationRepository,
)
from app.adapters.qdrant.client import QdrantClient
from app.adapters.semantic import SemanticTitleIndexer
from app.core.database import Base
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.catalog.models import CatalogueTitle, Genre
from app.modules.onboarding.dependencies import (
    get_onboarding_use_cases,
    require_completed_onboarding,
)
from app.modules.recommendations.dependencies import get_tonight_recommendations_use_case
from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.tonight import TonightPreferences
from app.modules.recommendations.use_cases.get_tonight_recommendations import (
    GetTonightRecommendations,
)
from test_recommendations_application import FakePersonalRepository, title


@pytest.fixture(autouse=True)
def clean_overrides():
    yield
    app.dependency_overrides.clear()


class TonightRepository(FakePersonalRepository):
    def eligible_title_ids(self, preferences):
        return {item.id for item in self._titles.values() if preferences.matches(item)}


@pytest.fixture
def local_index():
    vectors = QdrantClient.__new__(QdrantClient)
    vectors._client = QdrantSdkClient(":memory:")
    vectors._collection = "tonight-tests"
    embeddings = SimpleNamespace(embed=lambda text: pytest.fail("Stored vectors should be reused"))
    yield SemanticTitleIndexer(embeddings, vectors)
    vectors._client.close()


def add_title(index, name, vector, **changes):
    item = replace(title(str(uuid4()), name, genres=["Drama"], keywords=[]), **changes)
    index._vectors.upsert(item.id, vector, index._payload(item))
    return item


def request(use_case, payload=None):
    app.dependency_overrides[require_completed_onboarding] = lambda: SimpleNamespace(id=uuid4())
    app.dependency_overrides[get_tonight_recommendations_use_case] = lambda: use_case
    return TestClient(app).post("/recommendations/tonight", json=payload or {})


def test_tonight_filters_before_top_k_and_excludes_all_library_states(local_index):
    index = local_index
    loved = add_title(index, "Loved", [1.0, 0.0])
    watched = add_title(index, "Watched", [1.0, 0.0])
    hidden = add_title(index, "Hidden", [1.0, 0.0])
    # More unsuitable nearest neighbours than the search limit must not hide a valid pick.
    long_titles = [
        add_title(index, f"Long {i}", [1.0, 0.0], runtime_minutes=150) for i in range(65)
    ]
    candidate = add_title(index, "Fits tonight", [0.8, 0.6], runtime_minutes=90)
    unknown = add_title(index, "Unknown duration", [1.0, 0.0], runtime_minutes=None)
    series = add_title(index, "Series", [1.0, 0.0], title_type="tv", runtime_minutes=40)
    repository = TonightRepository(
        [RatedTitle(loved, 5)],
        [loved, watched, hidden, candidate, unknown, series, *long_titles],
        {watched.id, hidden.id},
    )
    response = request(
        GetTonightRecommendations(repository, index),
        {
            "max_minutes": 100,
            "genres": ["Drama", "Comedy"],
            "year_from": 2024,
            "year_to": 2024,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert [item["id"] for item in response.json()["items"]] == [candidate.id]
    assert "90 min runtime" in response.json()["items"][0]["reason"]
    assert "Released in 2024" in response.json()["items"][0]["reason"]


def test_tonight_tv_uses_episode_runtime_and_no_matches_is_explicit(local_index):
    loved = add_title(local_index, "Loved", [1.0, 0.0])
    series = add_title(local_index, "Series", [1.0, 0.0], title_type="tv", runtime_minutes=45)
    repository = TonightRepository([RatedTitle(loved, 5)], [loved, series])
    use_case = GetTonightRecommendations(repository, local_index)
    response = request(use_case, {"type": "tv", "max_minutes": 45})
    assert response.json()["items"][0]["type"] == "tv"
    assert "45 min per episode" in response.json()["items"][0]["reason"]
    assert request(use_case, {"type": "tv", "max_minutes": 44}).json() == {
        "items": [],
        "status": "no_matches",
    }


def test_discovery_changes_the_shortlist_without_losing_the_best_match(local_index):
    loved = add_title(local_index, "Loved", [1.0, 0.0])
    strongest = add_title(local_index, "Strongest", [1.0, 0.0])
    close = [add_title(local_index, f"Close {i}", [0.95, 0.31 + i * 0.01]) for i in range(6)]
    different = add_title(local_index, "Different", [0.7, -0.714])
    repository = TonightRepository([RatedTitle(loved, 5)], [loved, strongest, different, *close])
    use_case = GetTonightRecommendations(repository, local_index)
    familiar = request(use_case).json()["items"]
    discovery = request(use_case, {"mode": "discover"}).json()["items"]
    assert len(familiar) == len(discovery) == 6
    assert familiar[0]["id"] == discovery[0]["id"] == strongest.id
    assert different.id not in {item["id"] for item in familiar}
    assert different.id in {item["id"] for item in discovery}


def test_neutral_ratings_return_no_profile_without_search(local_index):
    neutral = add_title(local_index, "Neutral", [1.0, 0.0])
    repository = TonightRepository([RatedTitle(neutral, 3)], [neutral])
    assert request(GetTonightRecommendations(repository, local_index)).json() == {
        "items": [],
        "status": "no_profile",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"type": "invalid"},
        {"max_minutes": 0},
        {"max_minutes": 1441},
        {"year_from": 2025, "year_to": 2020},
        {"year_from": 1799},
        {"year_to": 2101},
        {"mode": "random"},
        {"genres": [""]},
    ],
)
def test_tonight_rejects_invalid_preferences(payload):
    use_case = SimpleNamespace(execute=lambda *args: pytest.fail("Invalid input reached use case"))
    assert request(use_case, payload).status_code == 422


def test_tonight_requires_authentication_and_onboarding():
    client = TestClient(app)
    assert client.post("/recommendations/tonight", json={}).status_code == 401
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
    app.dependency_overrides[get_onboarding_use_cases] = lambda: SimpleNamespace(
        is_onboarding_complete=SimpleNamespace(execute=lambda _: False)
    )
    assert client.post("/recommendations/tonight", json={}).status_code == 403


def test_tonight_reports_provider_failure():
    def fail(*args):
        raise RuntimeError("Provider details must not leak")

    response = request(SimpleNamespace(execute=fail))
    assert response.status_code == 503
    assert response.json() == {"detail": "Tonight's picks are unavailable."}


def test_canonical_filters_have_inclusive_boundaries_and_or_genres():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        drama, comedy = Genre(id=1, name="Drama"), Genre(id=2, name="Comedy")
        rows = []
        for name, runtime, year, kind, genres in [
            ("At lower boundary", 90, 2000, "movie", [drama]),
            ("At upper boundary", 120, 2020, "movie", [comedy]),
            ("Unknown duration", None, 2010, "movie", [drama]),
            ("Zero duration", 0, 2010, "movie", [drama]),
            ("Unknown year", 90, None, "movie", [drama]),
            ("Too old", 90, 1999, "movie", [drama]),
            ("Too new", 90, 2021, "movie", [drama]),
            ("Too long", 121, 2010, "movie", [drama]),
            ("TV", 90, 2010, "tv", [drama]),
            ("Wrong genre", 90, 2010, "movie", []),
        ]:
            row = CatalogueTitle(
                title=name,
                runtime_minutes=runtime,
                release_year=year,
                release_date=date(year, 1, 1) if year else None,
                title_type=kind,
                genres=genres,
                original_language="en",
            )
            session.add(row)
            rows.append(row)
        session.commit()
        expected = {str(row.id) for row in rows[:2]}
        unknown_id = str(rows[2].id)
    repository = SqlAlchemyPersonalRecommendationRepository(engine)
    criteria = TonightPreferences(
        genres=("Drama", "Comedy"), max_minutes=120, year_from=2000, year_to=2020
    )
    assert repository.eligible_title_ids(criteria) == expected
    assert unknown_id in repository.eligible_title_ids(replace(criteria, max_minutes=None))
    engine.dispose()
