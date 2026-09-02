"""Public REST interface for catalogue discovery."""

from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.adapters.catalogue_repository import SqlAlchemyCatalogueRepository, create_catalogue_engine
from app.core.config import Settings
from app.modules.catalog.application import CatalogueApplicationService
from app.modules.catalog.service import (
    CatalogueFacets,
    CataloguePage,
    CatalogueQuery,
    CatalogueService,
    TitleDetails,
    TitleSummary,
)

router = APIRouter(prefix="/catalogue", tags=["catalogue"])


class TitleSummaryResponse(BaseModel):
    """Title data rendered in a catalogue card."""

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
    """Paginated catalogue response."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[TitleSummaryResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")


class TitleDetailsResponse(TitleSummaryResponse):
    """Complete metadata for a title detail page."""

    runtime_minutes: int | None = Field(serialization_alias="runtimeMinutes")
    overview: str | None
    backdrop_path: str | None = Field(serialization_alias="backdropPath")
    vote_average: float | None = Field(serialization_alias="voteAverage")
    tagline: str | None
    cast: list[dict[str, str]]
    creators: list[str]
    keywords: list[str]


class CatalogueFacetsResponse(BaseModel):
    """Available local catalogue filter values."""

    genres: list[str]
    languages: list[str]
    years: list[int]


def get_catalogue_service() -> CatalogueService:
    """Provide the configured catalogue service after application wiring."""
    settings = Settings.from_environment()
    return configured_catalogue_service(settings.database_url)


@lru_cache
def configured_catalogue_service(database_url: str) -> CatalogueApplicationService:
    """Reuse one PostgreSQL engine for the active application configuration."""
    return CatalogueApplicationService(
        SqlAlchemyCatalogueRepository(create_catalogue_engine(database_url))
    )


def to_summary_response(title: TitleSummary) -> TitleSummaryResponse:
    """Map the module DTO to its stable REST representation."""
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


def to_details_response(title: TitleDetails) -> TitleDetailsResponse:
    """Map detailed canonical metadata to its REST representation."""
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


@router.get("/titles", response_model=CataloguePageResponse)
def list_titles(
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
    query: Annotated[str | None, Query(max_length=200)] = None,
    title_type: Annotated[str | None, Query(alias="type", pattern="^(movie|tv)$")] = None,
    genre: Annotated[str | None, Query(max_length=100)] = None,
    language: Annotated[str | None, Query(min_length=2, max_length=8)] = None,
    year: Annotated[int | None, Query(ge=1888, le=2100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
) -> CataloguePageResponse:
    """Browse local canonical titles with AND-combined filters."""
    result: CataloguePage = service.search(
        CatalogueQuery(
            title_query=query,
            title_type=title_type,
            genre=genre,
            language=language,
            year=year,
            page=page,
        )
    )
    return CataloguePageResponse(
        items=[to_summary_response(title) for title in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/titles/{title_id}", response_model=TitleDetailsResponse)
def get_title(
    title_id: str, service: Annotated[CatalogueService, Depends(get_catalogue_service)]
) -> TitleDetailsResponse:
    """Open the local canonical details page for one title."""
    title = service.details(title_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Catalogue title not found.")
    return to_details_response(title)


@router.get("/filters", response_model=CatalogueFacetsResponse)
def get_filters(
    service: Annotated[CatalogueService, Depends(get_catalogue_service)],
) -> CatalogueFacetsResponse:
    """List the filters available for currently synchronized titles."""
    facets: CatalogueFacets = service.facets()
    return CatalogueFacetsResponse(
        genres=facets.genres,
        languages=facets.languages,
        years=facets.years,
    )
