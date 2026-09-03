"""Composition root for independent catalogue use cases."""

from dataclasses import dataclass
from functools import lru_cache

from app.adapters.ollama.client import OllamaEmbeddingClient
from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.qdrant.client import QdrantClient
from app.adapters.semantic import SemanticTitleIndexer
from app.adapters.tmdb.client import TmdbClient
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.catalog.use_cases import (
    GetCatalogueFacets,
    GetTitleDetails,
    ImportTmdbTitle,
    SearchCatalogue,
    SearchExternalTitles,
)
from app.modules.catalog.use_cases.synchronize_catalogue import SynchronizeCatalogue


@dataclass(frozen=True)
class CatalogueUseCases:
    search_catalogue: SearchCatalogue
    get_title_details: GetTitleDetails
    get_catalogue_facets: GetCatalogueFacets
    synchronize_catalogue: SynchronizeCatalogue


@dataclass(frozen=True)
class ExternalCatalogueUseCases:
    search_external_titles: SearchExternalTitles
    import_tmdb_title: ImportTmdbTitle


def get_catalogue_use_cases() -> CatalogueUseCases:
    return configured_catalogue_use_cases(Settings.from_environment().database_url)


def get_external_catalogue_use_cases() -> ExternalCatalogueUseCases:
    settings = Settings.from_environment()
    repository = SqlAlchemyCatalogueRepository(create_database_engine(settings.database_url))
    gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
    indexer = SemanticTitleIndexer(
        OllamaEmbeddingClient(settings.ollama_base_url, settings.ollama_embedding_model),
        QdrantClient(
            settings.require_qdrant_url(),
            settings.require_qdrant_api_key(),
            settings.qdrant_collection,
        ),
    )
    return ExternalCatalogueUseCases(
        search_external_titles=SearchExternalTitles(gateway),
        import_tmdb_title=ImportTmdbTitle(repository, gateway, indexer),
    )


@lru_cache
def configured_catalogue_use_cases(database_url: str) -> CatalogueUseCases:
    repository = SqlAlchemyCatalogueRepository(create_database_engine(database_url))
    return CatalogueUseCases(
        search_catalogue=SearchCatalogue(repository),
        get_title_details=GetTitleDetails(repository),
        get_catalogue_facets=GetCatalogueFacets(repository),
        synchronize_catalogue=SynchronizeCatalogue(repository),
    )
