"""PostgreSQL reader for recommendation-specific user and catalogue state."""

from uuid import UUID

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.postgres.mappers.recommendations import to_rated_title
from app.modules.catalog.domain import TitleDetails
from app.modules.catalog.models import CatalogueTitle, Genre
from app.modules.interactions.models import NotInterestedTitle, UserRating, WatchedTitle
from app.modules.recommendations.domain import RatedTitle
from app.modules.recommendations.tonight import TonightPreferences


class SqlAlchemyPersonalRecommendationRepository:
    """Load explicit taste signals and non-recommendable library titles."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._catalogue = SqlAlchemyCatalogueRepository(engine)

    def details(self, title_id: str) -> TitleDetails | None:
        return self._catalogue.details(title_id)

    def eligible_title_ids(self, preferences: TonightPreferences) -> set[str]:
        statement = select(CatalogueTitle.id).where(
            CatalogueTitle.title_type == preferences.title_type
        )
        if preferences.genres:
            statement = statement.where(
                CatalogueTitle.genres.any(Genre.name.in_(preferences.genres))
            )
        if preferences.max_minutes is not None:
            statement = statement.where(
                CatalogueTitle.runtime_minutes > 0,
                CatalogueTitle.runtime_minutes <= preferences.max_minutes,
            )
        if preferences.year_from is not None:
            statement = statement.where(CatalogueTitle.release_year >= preferences.year_from)
        if preferences.year_to is not None:
            statement = statement.where(CatalogueTitle.release_year <= preferences.year_to)
        with Session(self._engine) as session:
            return {str(identifier) for identifier in session.scalars(statement)}

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
