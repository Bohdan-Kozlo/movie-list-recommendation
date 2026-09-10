from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.api import get_current_user
from app.modules.auth.domain import User
from app.modules.interactions.dependencies import get_interaction_use_cases
from app.modules.interactions.domain import DuplicateRatingError, InteractionStatus, LibraryItem


class FakeInteractions:
    def __init__(self) -> None:
        self.user_id = uuid4()
        self.title_id = uuid4()
        self.rating: float | None = None
        self.watchlisted = False
        self.watched = False
        self.not_interested = False

    def create_rating(self, user_id: UUID, title_id: UUID, value: float) -> None:
        self._verify(user_id, title_id)
        if self.rating is not None:
            raise DuplicateRatingError
        self.rating = value

    def add_watchlist(self, user_id: UUID, title_id: UUID) -> None:
        self._verify(user_id, title_id)
        self.watchlisted = True

    def mark_watched(self, user_id: UUID, title_id: UUID) -> None:
        self._verify(user_id, title_id)
        self.watched = True
        self.watchlisted = False

    def status(self, user_id: UUID, title_id: UUID) -> InteractionStatus:
        self._verify(user_id, title_id)
        return InteractionStatus(
            title_id=title_id,
            rating=self.rating,
            is_watchlisted=self.watchlisted,
            is_watched=self.watched,
            is_not_interested=self.not_interested,
        )

    def library(self, user_id: UUID, collection: str) -> list[LibraryItem]:
        assert user_id == self.user_id
        assert collection == "watched"
        return []

    def _verify(self, user_id: UUID, title_id: UUID) -> None:
        assert user_id == self.user_id
        assert title_id == self.title_id


def test_user_can_rate_and_mark_a_title_watched_through_the_rest_api() -> None:
    interactions = FakeInteractions()
    app.dependency_overrides[get_current_user] = lambda: User(
        id=interactions.user_id, email="person@example.com", password_hash="hashed"
    )
    app.dependency_overrides[get_interaction_use_cases] = lambda: SimpleNamespace(
        create_rating=SimpleNamespace(execute=interactions.create_rating),
        add_watchlist=SimpleNamespace(execute=interactions.add_watchlist),
        mark_watched=SimpleNamespace(execute=interactions.mark_watched),
        get_interaction_status=SimpleNamespace(execute=interactions.status),
        get_library=SimpleNamespace(execute=interactions.library),
    )
    client = TestClient(app)

    rating = client.post(
        f"/interactions/titles/{interactions.title_id}/ratings",
        json={"value": 4.5},
    )
    watchlist = client.post(f"/interactions/titles/{interactions.title_id}/watchlist")
    watched = client.post(f"/interactions/titles/{interactions.title_id}/watched")
    status = client.get(f"/interactions/titles/{interactions.title_id}")
    library = client.get("/interactions/library/watched")

    app.dependency_overrides.clear()

    assert rating.status_code == 201
    assert watchlist.status_code == 204
    assert watched.status_code == 204
    assert status.json() == {
        "rating": 4.5,
        "is_watchlisted": False,
        "is_watched": True,
        "is_not_interested": False,
    }
    assert library.json() == {"collection": "watched", "items": []}


def test_library_interaction_endpoints_require_an_authenticated_session(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://unused")
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")
    response = TestClient(app).get(f"/interactions/titles/{uuid4()}")

    assert response.status_code == 401


def test_rest_api_rejects_a_second_rating_for_the_same_title() -> None:
    interactions = FakeInteractions()
    app.dependency_overrides[get_current_user] = lambda: User(
        id=interactions.user_id, email="person@example.com", password_hash="hashed"
    )
    app.dependency_overrides[get_interaction_use_cases] = lambda: SimpleNamespace(
        create_rating=SimpleNamespace(execute=interactions.create_rating)
    )
    client = TestClient(app)

    first = client.post(
        f"/interactions/titles/{interactions.title_id}/ratings",
        json={"value": 4.0},
    )
    duplicate = client.post(
        f"/interactions/titles/{interactions.title_id}/ratings",
        json={"value": 3.0},
    )

    app.dependency_overrides.clear()

    assert first.status_code == 201
    assert duplicate.status_code == 409
