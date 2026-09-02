"""Composition root for independent catalogue use cases."""

from dataclasses import dataclass
from functools import lru_cache

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.catalog.use_cases import GetCatalogueFacets, GetTitleDetails, SearchCatalogue
from app.modules.catalog.use_cases.synchronize_catalogue import SynchronizeCatalogue


@dataclass(frozen=True)
class CatalogueUseCases:
    search_catalogue: SearchCatalogue
    get_title_details: GetTitleDetails
    get_catalogue_facets: GetCatalogueFacets
    synchronize_catalogue: SynchronizeCatalogue


def get_catalogue_use_cases() -> CatalogueUseCases:
    return configured_catalogue_use_cases(Settings.from_environment().database_url)


@lru_cache
def configured_catalogue_use_cases(database_url: str) -> CatalogueUseCases:
    repository = SqlAlchemyCatalogueRepository(create_database_engine(database_url))
    return CatalogueUseCases(
        search_catalogue=SearchCatalogue(repository),
        get_title_details=GetTitleDetails(repository),
        get_catalogue_facets=GetCatalogueFacets(repository),
        synchronize_catalogue=SynchronizeCatalogue(repository),
    )
