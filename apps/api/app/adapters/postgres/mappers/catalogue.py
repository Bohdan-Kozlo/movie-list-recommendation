"""Mappings for catalogue persistence records."""

from app.modules.catalog.domain import TitleDetails, TitleSummary
from app.modules.catalog.models import CatalogueTitle


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
    return TitleDetails(
        **to_title_summary(title).__dict__,
        overview=title.overview,
        runtime_minutes=title.runtime_minutes,
        backdrop_path=title.backdrop_path,
        vote_average=title.vote_average,
        tagline=title.tagline,
        cast=title.cast,
        creators=title.creators,
        keywords=title.keywords,
    )
