"""PostgreSQL persistence adapter for canonical catalogue records."""

from uuid import UUID

from sqlalchemy import Engine, Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.postgres.mappers.catalogue import to_title_details, to_title_summary
from app.modules.catalog.domain import CatalogueFacets, CataloguePage, CatalogueQuery, TitleDetails
from app.modules.catalog.models import CatalogueTitle, ExternalIdentifier, Genre
from app.modules.catalog.sync import SyncedTitle


class SqlAlchemyCatalogueRepository:
    """Own canonical title persistence and visitor discovery queries."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def search(self, query: CatalogueQuery) -> CataloguePage:
        statement = self._filtered_titles(query).order_by(
            CatalogueTitle.popularity.desc(), CatalogueTitle.title.asc()
        )
        with Session(self._engine) as session:
            total = session.scalar(select(func.count()).select_from(statement.subquery())) or 0
            titles = session.scalars(
                statement.options(selectinload(CatalogueTitle.genres))
                .offset((query.page - 1) * query.page_size)
                .limit(query.page_size)
            ).all()
        return CataloguePage(
            items=[to_title_summary(title) for title in titles],
            total=total,
            page=query.page,
            page_size=query.page_size,
        )

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

    def facets(self) -> CatalogueFacets:
        with Session(self._engine) as session:
            genres = list(session.scalars(select(Genre.name).order_by(Genre.name)).all())
            languages = list(
                session.scalars(
                    select(CatalogueTitle.original_language)
                    .distinct()
                    .order_by(CatalogueTitle.original_language)
                ).all()
            )
            stored_years = list(
                session.scalars(
                    select(CatalogueTitle.release_year)
                    .where(CatalogueTitle.release_year.is_not(None))
                    .distinct()
                    .order_by(CatalogueTitle.release_year.desc())
                ).all()
            )
        return CatalogueFacets(
            genres=genres,
            languages=languages,
            years=[year for year in stored_years if year is not None],
        )

    def upsert(self, synced_title: SyncedTitle) -> bool:
        provider = f"tmdb_{synced_title.title_type}"
        external_value = normalize_external_id(provider, str(synced_title.tmdb_id))
        with Session(self._engine) as session, session.begin():
            identifier = session.scalar(
                select(ExternalIdentifier)
                .where(
                    ExternalIdentifier.provider == provider,
                    ExternalIdentifier.value == external_value,
                )
                .options(selectinload(ExternalIdentifier.title).selectinload(CatalogueTitle.genres))
            )
            created = identifier is None
            if identifier is None:
                title = CatalogueTitle(
                    title_type=synced_title.title_type,
                    title=synced_title.title,
                    original_language="en",
                )
                title.external_ids.append(
                    ExternalIdentifier(provider=provider, value=external_value)
                )
                session.add(title)
            else:
                title = identifier.title
            title.title_type = synced_title.title_type
            title.title = synced_title.title
            title.original_title = synced_title.original_title
            title.overview = synced_title.overview
            title.original_language = synced_title.original_language.lower()
            title.release_date = synced_title.release_date
            title.release_year = (
                synced_title.release_date.year if synced_title.release_date else None
            )
            title.runtime_minutes = synced_title.runtime_minutes
            title.poster_path = synced_title.poster_path
            title.backdrop_path = synced_title.backdrop_path
            title.popularity = synced_title.popularity
            title.vote_average = synced_title.vote_average
            title.tagline = synced_title.tagline
            title.cast = synced_title.cast
            title.creators = synced_title.creators
            title.keywords = synced_title.keywords
            title.genres = self._genres(session, synced_title)
            self._replace_imdb_id(title, synced_title.imdb_id)
        return created

    def _filtered_titles(self, query: CatalogueQuery) -> Select[tuple[CatalogueTitle]]:
        statement = select(CatalogueTitle)
        if query.title_query:
            statement = statement.where(
                func.lower(CatalogueTitle.title).contains(query.title_query.lower())
            )
        if query.title_type:
            statement = statement.where(CatalogueTitle.title_type == query.title_type)
        if query.genre:
            statement = statement.join(CatalogueTitle.genres).where(Genre.name == query.genre)
        if query.language:
            statement = statement.where(
                func.lower(CatalogueTitle.original_language) == query.language.lower()
            )
        if query.year:
            statement = statement.where(CatalogueTitle.release_year == query.year)
        return statement

    @staticmethod
    def _genres(session: Session, synced_title: SyncedTitle) -> list[Genre]:
        genre_ids = [genre.id for genre in synced_title.genres]
        existing = {
            genre.id: genre
            for genre in session.scalars(select(Genre).where(Genre.id.in_(genre_ids))).all()
        }
        for genre in synced_title.genres:
            if genre.id not in existing:
                existing[genre.id] = Genre(id=genre.id, name=genre.name)
        return [existing[genre.id] for genre in synced_title.genres]

    @staticmethod
    def _replace_imdb_id(title: CatalogueTitle, imdb_id: str | None) -> None:
        if not imdb_id:
            return
        normalized_id = normalize_external_id("imdb", imdb_id)
        existing_identifier = next(
            (identifier for identifier in title.external_ids if identifier.provider == "imdb"), None
        )
        if existing_identifier is None:
            title.external_ids.append(ExternalIdentifier(provider="imdb", value=normalized_id))
        else:
            existing_identifier.value = normalized_id


def normalize_external_id(provider: str, value: str) -> str:
    """Canonicalize identifiers before they participate in a uniqueness constraint."""
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError(f"{provider} identifiers cannot be blank.")
    if provider.startswith("tmdb_"):
        return str(int(normalized))
    return normalized
