"""PostgreSQL persistence adapter for user-library interactions."""

from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.postgres.mappers.interactions import to_library_item
from app.modules.catalog.models import CatalogueTitle
from app.modules.interactions.domain import InteractionStatus, LibraryItem
from app.modules.interactions.models import (
    NotInterestedTitle,
    UserRating,
    WatchedTitle,
    WatchlistEntry,
)
from app.modules.interactions.ports import LibraryCollection


class SqlAlchemyInteractionRepository:
    """Own ratings and the stateful collections in one user's library."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def title_exists(self, title_id: UUID) -> bool:
        with Session(self._engine) as session:
            return session.get(CatalogueTitle, title_id) is not None

    def rating_exists(self, user_id: UUID, title_id: UUID) -> bool:
        with Session(self._engine) as session:
            return session.get(UserRating, {"user_id": user_id, "title_id": title_id}) is not None

    def create_rating(self, user_id: UUID, title_id: UUID, value: float) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(UserRating(user_id=user_id, title_id=title_id, value=Decimal(str(value))))

    def delete_rating(self, user_id: UUID, title_id: UUID) -> None:
        self._delete(UserRating, user_id, title_id)

    def add_watchlist(self, user_id: UUID, title_id: UUID) -> None:
        self._add(WatchlistEntry, user_id, title_id)

    def remove_watchlist(self, user_id: UUID, title_id: UUID) -> None:
        self._delete(WatchlistEntry, user_id, title_id)

    def mark_watched(self, user_id: UUID, title_id: UUID) -> None:
        self._add_and_remove_from_watchlist(WatchedTitle, user_id, title_id)

    def remove_watched(self, user_id: UUID, title_id: UUID) -> None:
        self._delete(WatchedTitle, user_id, title_id)

    def mark_not_interested(self, user_id: UUID, title_id: UUID) -> None:
        self._add_and_remove_from_watchlist(NotInterestedTitle, user_id, title_id)

    def _add_and_remove_from_watchlist(
        self, entry_type: type[Any], user_id: UUID, title_id: UUID
    ) -> None:
        with Session(self._engine) as session, session.begin():
            self._merge(session, entry_type, user_id, title_id)
            self._delete_from_session(session, WatchlistEntry, user_id, title_id)

    def remove_not_interested(self, user_id: UUID, title_id: UUID) -> None:
        self._delete(NotInterestedTitle, user_id, title_id)

    def status(self, user_id: UUID, title_id: UUID) -> InteractionStatus:
        with Session(self._engine) as session:
            rating = session.get(UserRating, {"user_id": user_id, "title_id": title_id})
            return InteractionStatus(
                title_id=title_id,
                rating=float(rating.value) if rating is not None else None,
                is_watchlisted=session.get(
                    WatchlistEntry, {"user_id": user_id, "title_id": title_id}
                )
                is not None,
                is_watched=session.get(WatchedTitle, {"user_id": user_id, "title_id": title_id})
                is not None,
                is_not_interested=session.get(
                    NotInterestedTitle, {"user_id": user_id, "title_id": title_id}
                )
                is not None,
            )

    def library(self, user_id: UUID, collection: LibraryCollection) -> list[LibraryItem]:
        with Session(self._engine) as session:
            if collection == "ratings":
                rows = session.execute(
                    select(CatalogueTitle, UserRating.value)
                    .join(UserRating)
                    .where(UserRating.user_id == user_id)
                    .options(selectinload(CatalogueTitle.genres))
                    .order_by(UserRating.created_at.desc())
                ).all()
                return [to_library_item(title, float(value)) for title, value in rows]
            entry_type = {
                "watchlist": WatchlistEntry,
                "watched": WatchedTitle,
                "not-interested": NotInterestedTitle,
            }[collection]
            entry = cast(Any, entry_type)
            titles = session.scalars(
                select(CatalogueTitle)
                .join(entry)
                .where(entry.user_id == user_id)
                .options(selectinload(CatalogueTitle.genres))
                .order_by(entry.created_at.desc())
            ).all()
        return [to_library_item(title) for title in titles]

    def _add(self, entry_type: type[Any], user_id: UUID, title_id: UUID) -> None:
        with Session(self._engine) as session, session.begin():
            self._merge(session, entry_type, user_id, title_id)

    def _delete(self, entry_type: type[Any], user_id: UUID, title_id: UUID) -> None:
        with Session(self._engine) as session, session.begin():
            self._delete_from_session(session, entry_type, user_id, title_id)

    @staticmethod
    def _merge(session: Session, entry_type: type[Any], user_id: UUID, title_id: UUID) -> None:
        session.merge(entry_type(user_id=user_id, title_id=title_id))

    @staticmethod
    def _delete_from_session(
        session: Session, entry_type: type[Any], user_id: UUID, title_id: UUID
    ) -> None:
        entry = cast(Any, entry_type)
        session.execute(delete(entry).where(entry.user_id == user_id, entry.title_id == title_id))
