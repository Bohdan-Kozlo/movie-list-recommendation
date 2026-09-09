"""HTTP DTOs and centralized mapping for catalogue routes."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.catalog.domain import (
    CatalogueFacets,
    CataloguePage,
    CatalogueQuery,
    ExternalTitle,
    TitleDetails,
    TitleSummary,
)


class TitleSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    title_type: str = Field(serialization_alias="type")
    release_date: str | None = Field(serialization_alias="releaseDate")
    original_language: str = Field(serialization_alias="originalLanguage")
    poster_path: str | None = Field(serialization_alias="posterPath")
    popularity: float
    genres: list[str]


class CataloguePageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[TitleSummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class SemanticDescriptionSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    description: str = Field(min_length=3, max_length=500)
    title_type: Literal["movie", "tv"] | None = Field(default=None, alias="type")

    @field_validator("description", mode="before")
    @classmethod
    def trim_description(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class SemanticDescriptionSearchResponse(BaseModel):
    items: list[TitleSummaryResponse]


class TitleDetailsResponse(TitleSummaryResponse):
    runtime_minutes: int | None = Field(serialization_alias="runtimeMinutes")
    overview: str | None
    backdrop_path: str | None = Field(serialization_alias="backdropPath")
    vote_average: float | None = Field(serialization_alias="voteAverage")
    tagline: str | None
    cast: list[dict[str, str]]
    creators: list[str]
    keywords: list[str]


class CatalogueFacetsResponse(BaseModel):
    genres: list[str]
    languages: list[str]
    years: list[int]


class ExternalTitleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tmdb_id: int = Field(serialization_alias="tmdbId")
    title_type: str = Field(serialization_alias="type")
    title: str
    release_date: str | None = Field(serialization_alias="releaseDate")
    poster_path: str | None = Field(serialization_alias="posterPath")


class ExternalTitleSearchResponse(BaseModel):
    items: list[ExternalTitleResponse]


def to_catalogue_query(
    title_query: str | None,
    title_type: str | None,
    genre: str | None,
    language: str | None,
    year: int | None,
    page: int,
) -> CatalogueQuery:
    return CatalogueQuery(
        title_query=title_query,
        title_type=title_type,
        genre=genre,
        language=language,
        year=year,
        page=page,
    )


def to_summary_response(title: TitleSummary) -> TitleSummaryResponse:
    return TitleSummaryResponse(
        id=title.id,
        title=title.title,
        title_type=title.title_type,
        release_date=title.release_date.isoformat() if title.release_date else None,
        original_language=title.original_language,
        poster_path=title.poster_path,
        popularity=title.popularity,
        genres=title.genres,
    )


def to_page_response(page: CataloguePage) -> CataloguePageResponse:
    return CataloguePageResponse(
        items=[to_summary_response(title) for title in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


def to_semantic_description_search_response(
    titles: list[TitleSummary],
) -> SemanticDescriptionSearchResponse:
    return SemanticDescriptionSearchResponse(items=[to_summary_response(title) for title in titles])


def to_details_response(title: TitleDetails) -> TitleDetailsResponse:
    return TitleDetailsResponse(
        **to_summary_response(title).model_dump(),
        overview=title.overview,
        runtime_minutes=title.runtime_minutes,
        backdrop_path=title.backdrop_path,
        vote_average=title.vote_average,
        tagline=title.tagline,
        cast=title.cast,
        creators=title.creators,
        keywords=title.keywords,
    )


def to_facets_response(facets: CatalogueFacets) -> CatalogueFacetsResponse:
    return CatalogueFacetsResponse(
        genres=facets.genres,
        languages=facets.languages,
        years=facets.years,
    )


def to_external_title_response(title: ExternalTitle) -> ExternalTitleResponse:
    return ExternalTitleResponse(
        tmdb_id=title.tmdb_id,
        title_type=title.title_type,
        title=title.title,
        release_date=title.release_date.isoformat() if title.release_date else None,
        poster_path=title.poster_path,
    )
