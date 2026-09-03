from types import SimpleNamespace
from uuid import uuid4

from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.domain import User
from app.modules.onboarding.dependencies import get_onboarding_use_cases
from app.modules.onboarding.domain import OnboardingProgress, OnboardingTitle
from fastapi.testclient import TestClient


def test_authenticated_user_can_load_onboarding_progress_and_choices() -> None:
    user = User(id=uuid4(), email="person@example.com", password_hash="hashed")
    title = OnboardingTitle(
        id="movie-id",
        title="Arrival",
        title_type="movie",
        release_date="2016-11-10",
        original_language="en",
        poster_path="/arrival.jpg",
        popularity=80.0,
        genres=["Science Fiction"],
    )
    progress = OnboardingProgress(3, 10, [title], [])
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_onboarding_use_cases] = lambda: SimpleNamespace(
        get_onboarding=SimpleNamespace(execute=lambda user_id: progress),
        is_onboarding_complete=SimpleNamespace(execute=lambda user_id: False),
        search_onboarding_titles=SimpleNamespace(
            execute=lambda user_id, query, title_type: [title]
        ),
    )

    client = TestClient(app)
    response = client.get("/onboarding")
    search = client.get("/onboarding/search", params={"query": "arrival", "type": "movie"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["ratingsRecorded"] == 3
    assert response.json()["ratingsRemaining"] == 7
    assert response.json()["movies"][0]["type"] == "movie"
    assert search.json()["items"][0]["id"] == "movie-id"


def test_onboarding_requires_an_authenticated_session(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://unused")
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")

    assert TestClient(app).get("/onboarding").status_code == 401
