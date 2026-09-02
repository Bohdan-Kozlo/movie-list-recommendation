"""HTTP DTOs and centralized mapping for user-library interactions."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.interactions.domain import InteractionStatus, LibraryItem, rating_is_valid
from app.modules.interactions.ports import LibraryCollection


class RatingRequest(BaseModel):
    value: float

    @field_validator("value")
    @classmethod
    def validate_half_point_range(cls, value: float) -> float:
        if not rating_is_valid(value):
            raise ValueError("Rating must be from 0.5 to 5.0 in half-point increments.")
        return value


class InteractionStatusResponse(BaseModel):
    rating: float | None
    is_watchlisted: bool
    is_watched: bool
    is_not_interested: bool


class LibraryItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    title_type: str = Field(serialization_alias="type")
    release_date: str | None = Field(serialization_alias="releaseDate")
    original_language: str = Field(serialization_alias="originalLanguage")
    poster_path: str | None = Field(serialization_alias="posterPath")
    popularity: float
    genres: list[str]
    rating: float | None


class LibraryResponse(BaseModel):
    collection: LibraryCollection
    items: list[LibraryItemResponse]


def to_status_response(status: InteractionStatus) -> InteractionStatusResponse:
    return InteractionStatusResponse(
        rating=status.rating,
        is_watchlisted=status.is_watchlisted,
        is_watched=status.is_watched,
        is_not_interested=status.is_not_interested,
    )


def to_library_item_response(item: LibraryItem) -> LibraryItemResponse:
    return LibraryItemResponse(
        id=item.title.id,
        title=item.title.title,
        title_type=item.title.title_type,
        release_date=item.title.release_date.isoformat() if item.title.release_date else None,
        original_language=item.title.original_language,
        poster_path=item.title.poster_path,
        popularity=item.title.popularity,
        genres=item.title.genres,
        rating=item.rating,
    )


def to_library_response(collection: LibraryCollection, items: list[LibraryItem]) -> LibraryResponse:
    return LibraryResponse(
        collection=collection,
        items=[to_library_item_response(item) for item in items],
    )
