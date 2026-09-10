from uuid import UUID, uuid4

import pytest

from app.modules.interactions.domain import DuplicateRatingError
from app.modules.interactions.use_cases import (
    AddNotInterested,
    CreateRating,
    DeleteRating,
    MarkWatched,
)


class FakeInteractionRepository:
    def __init__(self) -> None:
        self.title_ids = {uuid4()}
        self.ratings: dict[tuple[UUID, UUID], float] = {}
        self.watchlist: set[tuple[UUID, UUID]] = set()
        self.watched: set[tuple[UUID, UUID]] = set()
        self.not_interested: set[tuple[UUID, UUID]] = set()

    def title_exists(self, title_id: UUID) -> bool:
        return title_id in self.title_ids

    def rating_exists(self, user_id: UUID, title_id: UUID) -> bool:
        return (user_id, title_id) in self.ratings

    def create_rating(self, user_id: UUID, title_id: UUID, value: float) -> None:
        self.ratings[(user_id, title_id)] = value

    def delete_rating(self, user_id: UUID, title_id: UUID) -> None:
        self.ratings.pop((user_id, title_id), None)

    def mark_watched(self, user_id: UUID, title_id: UUID) -> None:
        self.watched.add((user_id, title_id))
        self.watchlist.discard((user_id, title_id))

    def mark_not_interested(self, user_id: UUID, title_id: UUID) -> None:
        self.not_interested.add((user_id, title_id))
        self.watchlist.discard((user_id, title_id))


def test_user_can_create_one_half_point_rating_but_cannot_replace_it() -> None:
    repository = FakeInteractionRepository()
    user_id = uuid4()
    title_id = next(iter(repository.title_ids))
    create_rating = CreateRating(repository)

    create_rating.execute(user_id, title_id, 4.5)

    assert repository.ratings[(user_id, title_id)] == 4.5
    with pytest.raises(DuplicateRatingError):
        create_rating.execute(user_id, title_id, 3.0)


def test_marking_watched_removes_the_title_from_the_watchlist() -> None:
    repository = FakeInteractionRepository()
    user_id = uuid4()
    title_id = next(iter(repository.title_ids))
    repository.watchlist.add((user_id, title_id))

    MarkWatched(repository).execute(user_id, title_id)

    assert (user_id, title_id) in repository.watched
    assert (user_id, title_id) not in repository.watchlist


def test_user_can_delete_a_rating_without_replacing_it() -> None:
    repository = FakeInteractionRepository()
    user_id = uuid4()
    title_id = next(iter(repository.title_ids))
    CreateRating(repository).execute(user_id, title_id, 2.5)

    DeleteRating(repository).execute(user_id, title_id)

    assert (user_id, title_id) not in repository.ratings


def test_marking_not_interested_removes_the_title_from_the_watchlist() -> None:
    repository = FakeInteractionRepository()
    user_id = uuid4()
    title_id = next(iter(repository.title_ids))
    repository.watchlist.add((user_id, title_id))

    AddNotInterested(repository).execute(user_id, title_id)

    assert (user_id, title_id) in repository.not_interested
    assert (user_id, title_id) not in repository.watchlist
