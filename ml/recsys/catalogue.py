"""Offline catalogue commands using the application's existing use cases."""

from dataclasses import asdict

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.semantic import create_semantic_index
from app.adapters.tmdb.client import TmdbClient
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.catalog.use_cases import SynchronizeCatalogue
from app.modules.recommendations.use_cases import IndexCatalogue


def sync_catalogue(title_type: str, pages: int) -> dict[str, int]:
    settings = Settings.from_environment()
    gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
    title_types = ["movie", "tv"] if title_type == "all" else [title_type]
    engine = create_database_engine(settings.database_url)
    try:
        repository = SqlAlchemyCatalogueRepository(engine)
        report = SynchronizeCatalogue(repository).execute(gateway, title_types, pages)
        index = create_semantic_index(settings)
        indexed = IndexCatalogue(repository, index).execute(only_missing=False)
        return {"created": report.created, "updated": report.updated, "indexed": indexed.indexed}
    finally:
        engine.dispose()


def index_catalogue() -> dict[str, int]:
    settings = Settings.from_environment()
    engine = create_database_engine(settings.database_url)
    try:
        repository = SqlAlchemyCatalogueRepository(engine)
        index = create_semantic_index(settings)
        return asdict(IndexCatalogue(repository, index).execute())
    finally:
        engine.dispose()
