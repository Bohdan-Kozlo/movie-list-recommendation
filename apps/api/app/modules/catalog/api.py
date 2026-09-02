"""Public REST interface for catalogue discovery."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.modules.catalog.dependencies import CatalogueUseCases, get_catalogue_use_cases
from app.modules.catalog.dto import (
    CatalogueFacetsResponse,
    CataloguePageResponse,
    TitleDetailsResponse,
    to_catalogue_query,
    to_details_response,
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
