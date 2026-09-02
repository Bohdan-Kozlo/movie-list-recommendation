"""Mappings from persistence records to user-library domain values."""

from app.modules.catalog.models import CatalogueTitle
from app.modules.interactions.domain import LibraryItem, LibraryTitle


def to_library_item(title: CatalogueTitle, rating: float | None = None) -> LibraryItem:
    return LibraryItem(
        title=LibraryTitle(
            id=str(title.id),
            title=title.title,
            title_type=title.title_type,
            release_date=title.release_date,
            original_language=title.original_language,
            poster_path=title.poster_path,
            popularity=title.popularity,
            genres=[genre.name for genre in sorted(title.genres, key=lambda item: item.name)],
        ),
        rating=rating,
    )
