"""PostgreSQL read adapter for mandatory taste onboarding."""

from uuid import UUID

from sqlalchemy import Engine, Select, exists, func, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.postgres.mappers.onboarding import to_onboarding_title
from app.modules.catalog.models import CatalogueTitle
from app.modules.interactions.models import UserRating
from app.modules.onboarding.domain import OnboardingTitle, TitleType


class SqlAlchemyOnboardingRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def rating_count(self, user_id: UUID) -> int:
        with Session(self._engine) as session:
            return (
                session.scalar(
                    select(func.count())
                    .select_from(UserRating)
                    .where(UserRating.user_id == user_id)
                )
                or 0
            )

    def popular_unrated_titles(
        self, user_id: UUID, title_type: TitleType, limit: int
    ) -> list[OnboardingTitle]:
        statement = self._unrated_statement(user_id, title_type).order_by(
            CatalogueTitle.popularity.desc(), CatalogueTitle.title.asc()
        )
        return self._titles(statement, limit)

    def search_unrated_titles(
        self, user_id: UUID, query: str, title_type: TitleType | None, limit: int
    ) -> list[OnboardingTitle]:
        statement = (
            self._unrated_statement(user_id, title_type)
            .where(func.lower(CatalogueTitle.title).contains(query.lower()))
            .order_by(CatalogueTitle.popularity.desc(), CatalogueTitle.title.asc())
        )
        return self._titles(statement, limit)

    @staticmethod
    def _unrated_statement(
        user_id: UUID, title_type: TitleType | None
    ) -> Select[tuple[CatalogueTitle]]:
        rated = exists(
            select(UserRating.title_id).where(
                UserRating.user_id == user_id, UserRating.title_id == CatalogueTitle.id
            )
        )
        statement = select(CatalogueTitle).where(~rated)
        return statement.where(CatalogueTitle.title_type == title_type) if title_type else statement

    def _titles(
        self, statement: Select[tuple[CatalogueTitle]], limit: int
    ) -> list[OnboardingTitle]:
        with Session(self._engine) as session:
            titles = session.scalars(
                statement.options(selectinload(CatalogueTitle.genres)).limit(limit)
            ).all()
        return [to_onboarding_title(title) for title in titles]
