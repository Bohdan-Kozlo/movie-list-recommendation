"""Independent catalogue use-case classes."""

from app.modules.catalog.use_cases.get_catalogue_facets import GetCatalogueFacets
from app.modules.catalog.use_cases.get_title_details import GetTitleDetails
from app.modules.catalog.use_cases.import_tmdb_title import ImportTmdbTitle
from app.modules.catalog.use_cases.search_catalogue import SearchCatalogue
from app.modules.catalog.use_cases.search_catalogue_by_description import (
    SearchCatalogueByDescription,
)
from app.modules.catalog.use_cases.search_external_titles import SearchExternalTitles
from app.modules.catalog.use_cases.synchronize_catalogue import SynchronizeCatalogue

__all__ = [
    "GetCatalogueFacets",
    "GetTitleDetails",
    "ImportTmdbTitle",
    "SearchCatalogue",
    "SearchCatalogueByDescription",
    "SearchExternalTitles",
    "SynchronizeCatalogue",
]
