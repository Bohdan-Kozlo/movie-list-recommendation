"""Console interface for reproducible recommendation-system workflows."""

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
API_SOURCE_ROOT = REPOSITORY_ROOT / "apps" / "api"


def main() -> None:
    """Run a supported recommendation-system command."""
    parser = argparse.ArgumentParser(prog="recsys")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("diagnostics", help="report the active Python runtime")
    catalogue = commands.add_parser("catalog", help="manage the canonical title catalogue")
    catalogue_commands = catalogue.add_subparsers(dest="catalogue_command", required=True)
    sync = catalogue_commands.add_parser("sync", help="synchronize popular TMDB titles")
    sync.add_argument("--type", choices=["all", "movie", "tv"], default="all", dest="title_type")
    sync.add_argument("--pages", type=int, default=5)
    arguments = parser.parse_args()

    if arguments.command == "diagnostics":
        print(json.dumps({"status": "ok", "python": sys.version.split()[0]}))
    elif arguments.command == "catalog" and arguments.catalogue_command == "sync":
        if arguments.pages < 1:
            parser.error("--pages must be at least 1")
        sys.path.insert(0, str(API_SOURCE_ROOT))
        from app.adapters.ollama.client import OllamaEmbeddingClient
        from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
        from app.adapters.qdrant.client import QdrantClient
        from app.adapters.semantic import SemanticTitleIndexer
        from app.adapters.tmdb.client import TmdbClient
        from app.core.config import Settings
        from app.core.database import create_database_engine
        from app.modules.catalog.use_cases import SynchronizeCatalogue
        from app.modules.recommendations.use_cases import IndexCatalogue

        settings = Settings.from_environment()
        gateway = TmdbClient(settings.require_tmdb_api_key(), settings.tmdb_base_url)
        title_types = ["movie", "tv"] if arguments.title_type == "all" else [arguments.title_type]
        repository = SqlAlchemyCatalogueRepository(create_database_engine(settings.database_url))
        report = SynchronizeCatalogue(repository).execute(gateway, title_types, arguments.pages)
        index = SemanticTitleIndexer(
            OllamaEmbeddingClient(settings.ollama_base_url, settings.ollama_embedding_model),
            QdrantClient(
                settings.require_qdrant_url(),
                settings.require_qdrant_api_key(),
                settings.qdrant_collection,
            ),
        )
        indexed = IndexCatalogue(repository, index).execute()
        print(
            json.dumps({"created": report.created, "updated": report.updated, "indexed": indexed})
        )
