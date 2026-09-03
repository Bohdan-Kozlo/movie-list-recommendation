"""HTTP DTOs and centralized mapping for taste onboarding."""

from pydantic import BaseModel, ConfigDict, Field

from app.modules.onboarding.domain import OnboardingProgress, OnboardingTitle


class OnboardingTitleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    title_type: str = Field(serialization_alias="type")
    release_date: str | None = Field(serialization_alias="releaseDate")
    original_language: str = Field(serialization_alias="originalLanguage")
    poster_path: str | None = Field(serialization_alias="posterPath")
    popularity: float
    genres: list[str]


class OnboardingResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ratings_recorded: int = Field(serialization_alias="ratingsRecorded")
    ratings_required: int = Field(serialization_alias="ratingsRequired")
    ratings_remaining: int = Field(serialization_alias="ratingsRemaining")
    is_complete: bool = Field(serialization_alias="isComplete")
    movies: list[OnboardingTitleResponse]
    tv_series: list[OnboardingTitleResponse] = Field(serialization_alias="tvSeries")


class OnboardingSearchResponse(BaseModel):
    items: list[OnboardingTitleResponse]


def to_title_response(title: OnboardingTitle) -> OnboardingTitleResponse:
    return OnboardingTitleResponse(
        id=title.id,
        title=title.title,
        title_type=title.title_type,
        release_date=title.release_date,
        original_language=title.original_language,
        poster_path=title.poster_path,
        popularity=title.popularity,
        genres=title.genres,
    )


def to_onboarding_response(progress: OnboardingProgress) -> OnboardingResponse:
    return OnboardingResponse(
        ratings_recorded=progress.ratings_recorded,
        ratings_required=progress.ratings_required,
        ratings_remaining=progress.ratings_remaining,
        is_complete=progress.is_complete,
        movies=[to_title_response(title) for title in progress.movies],
        tv_series=[to_title_response(title) for title in progress.tv_series],
    )


def to_search_response(titles: list[OnboardingTitle]) -> OnboardingSearchResponse:
    return OnboardingSearchResponse(items=[to_title_response(title) for title in titles])
