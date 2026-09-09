"""Composition root for independent catalogue use cases."""

from dataclasses import dataclass

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.semantic import create_semantic_index
from app.adapters.tmdb.client import TmdbClient
from app.core.config import Settings
from app.core.database import get_database_engine
from app.modules.catalog.use_cases import (
    GetCatalogueFacets,
    GetTitleDetails,
    ImportTmdbTitle,
    SearchCatalogue,
    SearchCatalogueByDescription,
    SearchExternalTitles,
)


@dataclass(frozen=True)
class CatalogueUseCases:
    search_catalogue: SearchCatalogue
    get_title_details: GetTitleDetails
    get_catalogue_facets: GetCatalogueFacets


def get_catalogue_use_cases() -> CatalogueUseCases:
    return configured_catalogue_use_cases(Settings.from_environment().database_url)


def get_search_external_titles_use_case() -> SearchExternalTitles:
    settings = Settings.from_environment()
    gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
    return SearchExternalTitles(gateway)


def get_import_tmdb_title_use_case() -> ImportTmdbTitle:
    settings = Settings.from_environment()
    repository = SqlAlchemyCatalogueRepository(get_database_engine(settings.database_url))
    gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
    return ImportTmdbTitle(repository, gateway, create_semantic_index(settings))


def get_semantic_description_search_use_case() -> SearchCatalogueByDescription:
    settings = Settings.from_environment()
    repository = SqlAlchemyCatalogueRepository(get_database_engine(settings.database_url))
    return SearchCatalogueByDescription(repository, create_semantic_index(settings))


def configured_catalogue_use_cases(database_url: str) -> CatalogueUseCases:
    repository = SqlAlchemyCatalogueRepository(get_database_engine(database_url))
    return CatalogueUseCases(
        search_catalogue=SearchCatalogue(repository),
        get_title_details=GetTitleDetails(repository),
        get_catalogue_facets=GetCatalogueFacets(repository),
    )
