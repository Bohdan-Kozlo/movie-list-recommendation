"""PostgreSQL reader for recommendation-specific user and catalogue state."""

from uuid import UUID

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.postgres.mappers.catalogue import to_title_details
from app.adapters.postgres.mappers.recommendations import to_rated_title
from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.models import CatalogueTitle
from app.modules.interactions.models import NotInterestedTitle, UserRating, WatchedTitle
from app.modules.recommendations.domain import RatedTitle


class SqlAlchemyPersonalRecommendationRepository:
    """Load explicit taste signals and non-recommendable library titles."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def details(self, title_id: str) -> TitleDetails | None:
        try:
            canonical_id = UUID(title_id)
        except ValueError:
            return None
        with Session(self._engine) as session:
            title = session.scalar(
                select(CatalogueTitle)
                .where(CatalogueTitle.id == canonical_id)
                .options(selectinload(CatalogueTitle.genres))
            )
        return to_title_details(title) if title is not None else None

    def rated_titles(self, user_id: UUID) -> list[RatedTitle]:
        with Session(self._engine) as session:
            rows = session.execute(
                select(CatalogueTitle, UserRating.value)
                .join(UserRating)
                .where(UserRating.user_id == user_id)
                .options(selectinload(CatalogueTitle.genres))
                .order_by(UserRating.created_at, CatalogueTitle.id)
            ).all()
        return [to_rated_title(title, value) for title, value in rows]

    def excluded_title_ids(self, user_id: UUID) -> set[str]:
        with Session(self._engine) as session:
            watched = session.scalars(
                select(WatchedTitle.title_id).where(WatchedTitle.user_id == user_id)
            ).all()
            not_interested = session.scalars(
                select(NotInterestedTitle.title_id).where(NotInterestedTitle.user_id == user_id)
            ).all()
        return {str(title_id) for title_id in [*watched, *not_interested]}
