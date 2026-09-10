from dataclasses import replace
from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.modules.catalog.models import Base, CatalogueTitle, ExternalIdentifier
from app.modules.catalog.sync import SyncedGenre, SyncedTitle
from app.modules.catalog.use_cases import SynchronizeCatalogue


class FakeTmdbGateway:
    def popular_ids(self, title_type: str, page: int) -> list[int]:
        assert title_type == "movie"
        assert page == 1
        return [42]

    def title_details(self, title_type: str, tmdb_id: int) -> SyncedTitle:
        return SyncedTitle(
            tmdb_id=tmdb_id,
            title_type=title_type,
            title="The Hitchhiker's Guide to the Galaxy",
            original_title="The Hitchhiker's Guide to the Galaxy",
            overview="Earth is demolished for a hyperspace bypass.",
            original_language="en",
            release_date=date(2005, 4, 28),
            runtime_minutes=109,
            poster_path="/poster.jpg",
            backdrop_path=None,
            popularity=8.0,
            vote_average=6.7,
            tagline=None,
            cast=[],
            creators=["Garth Jennings"],
            keywords=["space"],
            genres=[SyncedGenre(id=878, name="Science Fiction")],
            imdb_id="tt0371724",
        )


class FakeCatalogueRepository:
    def __init__(self) -> None:
        self._tmdb_ids: set[tuple[str, int]] = set()

    def upsert(self, title: SyncedTitle) -> bool:
        key = (title.title_type, title.tmdb_id)
        created = key not in self._tmdb_ids
        self._tmdb_ids.add(key)
        return created


def test_repeat_catalogue_sync_updates_existing_normalized_tmdb_records() -> None:
    use_case = SynchronizeCatalogue(FakeCatalogueRepository())
    gateway = FakeTmdbGateway()

    first_report = use_case.execute(gateway, ["movie"], pages=1)
    second_report = use_case.execute(gateway, ["movie"], pages=1)

    assert first_report.created == 1
    assert first_report.updated == 0
    assert second_report.created == 0
    assert second_report.updated == 1


def test_repository_upsert_updates_tmdb_metadata_and_preserves_normalized_ids() -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyCatalogueRepository(engine)
    original = FakeTmdbGateway().title_details("movie", 42)

    assert repository.upsert(original) is True
    assert repository.upsert(replace(original, title="Updated guide", imdb_id=None)) is False

    with Session(engine) as session:
        stored_title = session.scalar(select(CatalogueTitle))
        identifiers = {
            (identifier.provider, identifier.value)
            for identifier in session.scalars(select(ExternalIdentifier)).all()
        }

    assert stored_title is not None
    assert stored_title.title == "Updated guide"
    assert identifiers == {("tmdb_movie", "42"), ("imdb", "tt0371724")}
    engine.dispose()
