"""Public REST interface for catalogue discovery."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.adapters.tmdb.client import TmdbNotFoundError
from app.modules.catalog.dependencies import (
    CatalogueUseCases,
    ExternalCatalogueUseCases,
    get_catalogue_use_cases,
    get_external_catalogue_use_cases,
)
from app.modules.catalog.dto import (
    CatalogueFacetsResponse,
    CataloguePageResponse,
    ExternalTitleSearchResponse,
    TitleDetailsResponse,
    to_catalogue_query,
    to_details_response,
    to_external_title_response,
    to_facets_response,
    to_page_response,
)

router = APIRouter(prefix="/catalogue", tags=["catalogue"])


@router.get("/titles", response_model=CataloguePageResponse)
def list_titles(
    use_cases: Annotated[CatalogueUseCases, Depends(get_catalogue_use_cases)],
    query: Annotated[str | None, Query(max_length=200)] = None,
    title_type: Annotated[str | None, Query(alias="type", pattern="^(movie|tv)$")] = None,
    genre: Annotated[str | None, Query(max_length=100)] = None,
    language: Annotated[str | None, Query(min_length=2, max_length=8)] = None,
    year: Annotated[int | None, Query(ge=1888, le=2100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
) -> CataloguePageResponse:
    """Browse local canonical titles with AND-combined filters."""
    result = use_cases.search_catalogue.execute(
        to_catalogue_query(query, title_type, genre, language, year, page)
    )
    return to_page_response(result)


@router.get("/tmdb-search", response_model=ExternalTitleSearchResponse)
def search_tmdb_titles(
    use_cases: Annotated[ExternalCatalogueUseCases, Depends(get_external_catalogue_use_cases)],
    query: Annotated[str, Query(min_length=1, max_length=200)],
    title_type: Annotated[str | None, Query(alias="type", pattern="^(movie|tv)$")] = None,
) -> ExternalTitleSearchResponse:
    """Find externally available titles when local search has no match."""
    try:
        titles = use_cases.search_external_titles.execute(query, title_type)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail="TMDB search is unavailable.") from error
    return ExternalTitleSearchResponse(
        items=[to_external_title_response(title) for title in titles]
    )


@router.post("/tmdb-titles/{title_type}/{tmdb_id}", response_model=TitleDetailsResponse)
def import_tmdb_title(
    title_type: Annotated[str, Path(pattern="^(movie|tv)$")],
    tmdb_id: int,
    use_cases: Annotated[ExternalCatalogueUseCases, Depends(get_external_catalogue_use_cases)],
) -> TitleDetailsResponse:
    """Persist, embed, and index an explicitly selected TMDB title."""
    try:
        title = use_cases.import_tmdb_title.execute(title_type, tmdb_id)
    except TmdbNotFoundError as error:
        raise HTTPException(status_code=404, detail="TMDB title not found.") from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail="Title import is unavailable.") from error
    if title is None:
        raise HTTPException(status_code=404, detail="TMDB title not found.")
    return to_details_response(title)


@router.get("/titles/{title_id}", response_model=TitleDetailsResponse)
def get_title(
    title_id: str,
    use_cases: Annotated[CatalogueUseCases, Depends(get_catalogue_use_cases)],
) -> TitleDetailsResponse:
    """Open the local canonical details page for one title."""
    title = use_cases.get_title_details.execute(title_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Catalogue title not found.")
    return to_details_response(title)


@router.get("/filters", response_model=CatalogueFacetsResponse)
def get_filters(
    use_cases: Annotated[CatalogueUseCases, Depends(get_catalogue_use_cases)],
) -> CatalogueFacetsResponse:
    """List the filters available for currently synchronized titles."""
    return to_facets_response(use_cases.get_catalogue_facets.execute())
