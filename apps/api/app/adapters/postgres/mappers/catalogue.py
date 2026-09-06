"""Mappings for catalogue persistence records."""

from app.modules.catalog.domain import TitleDetails, TitleSummary
from app.modules.catalog.models import CatalogueTitle
from app.modules.catalog.sync import SyncedTitle


def to_title_summary(title: CatalogueTitle) -> TitleSummary:
    return TitleSummary(
        id=str(title.id),
        title=title.title,
        title_type=title.title_type,
        release_date=title.release_date,
        original_language=title.original_language,
        poster_path=title.poster_path,
        popularity=title.popularity,
        genres=[genre.name for genre in sorted(title.genres, key=lambda item: item.name)],
    )


def to_title_details(title: CatalogueTitle) -> TitleDetails:
    tmdb_identifier = next(
        (
            identifier
            for identifier in title.external_ids
            if identifier.provider.startswith("tmdb_")
        ),
        None,
    )
    summary = to_title_summary(title)
    return TitleDetails(
        id=summary.id,
        title=summary.title,
        title_type=summary.title_type,
        release_date=summary.release_date,
        original_language=summary.original_language,
        poster_path=summary.poster_path,
        popularity=summary.popularity,
        genres=summary.genres,
        overview=title.overview,
        runtime_minutes=title.runtime_minutes,
        backdrop_path=title.backdrop_path,
        vote_average=title.vote_average,
        tagline=title.tagline,
        cast=title.cast,
        creators=title.creators,
        keywords=title.keywords,
        tmdb_id=int(tmdb_identifier.value) if tmdb_identifier else None,
    )


def apply_synced_metadata(title: CatalogueTitle, synced_title: SyncedTitle) -> None:
    """Copy scalar provider metadata; the repository owns relations and transactions."""
    title.title_type = synced_title.title_type
    title.title = synced_title.title
    title.original_title = synced_title.original_title
    title.overview = synced_title.overview
    title.original_language = synced_title.original_language.lower()
    title.release_date = synced_title.release_date
    title.release_year = synced_title.release_date.year if synced_title.release_date else None
    title.runtime_minutes = synced_title.runtime_minutes
    title.poster_path = synced_title.poster_path
    title.backdrop_path = synced_title.backdrop_path
    title.popularity = synced_title.popularity
    title.vote_average = synced_title.vote_average
    title.tagline = synced_title.tagline
    title.cast = synced_title.cast
    title.creators = synced_title.creators
    title.keywords = synced_title.keywords
