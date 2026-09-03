from uuid import uuid4

from app.adapters.postgres.onboarding_repository import SqlAlchemyOnboardingRepository
from sqlalchemy.dialects import postgresql


def test_popular_selection_excludes_titles_already_rated_by_the_current_user() -> None:
    user_id = uuid4()
    statement = SqlAlchemyOnboardingRepository._unrated_statement(user_id, "movie")

    query = str(
        statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    )

    assert "NOT (EXISTS" in query
    assert "user_ratings.user_id" in query
    assert "user_ratings.title_id = catalogue_titles.id" in query
    assert str(user_id) in query
