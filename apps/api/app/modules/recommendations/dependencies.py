"""Composition root for semantic recommendations."""

from app.adapters.ollama.client import OllamaEmbeddingClient
from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.postgres.recommendation_repository import (
    SqlAlchemyPersonalRecommendationRepository,
)
from app.adapters.qdrant.client import QdrantClient
from app.adapters.semantic import SemanticTitleIndexer
from app.core.config import Settings
from app.core.database import create_database_engine
from app.modules.recommendations.use_cases import GetPersonalRecommendations, GetSimilarTitles


def get_similar_titles_use_case() -> GetSimilarTitles:
    settings = Settings.from_environment()
    catalogue = SqlAlchemyCatalogueRepository(create_database_engine(settings.database_url))
    return GetSimilarTitles(catalogue, semantic_index(settings))


def get_personal_recommendations_use_case() -> GetPersonalRecommendations:
    settings = Settings.from_environment()
    repository = SqlAlchemyPersonalRecommendationRepository(
        create_database_engine(settings.database_url)
    )
    return GetPersonalRecommendations(repository, semantic_index(settings))


def semantic_index(settings: Settings) -> SemanticTitleIndexer:
    return SemanticTitleIndexer(
        OllamaEmbeddingClient(settings.ollama_base_url, settings.ollama_embedding_model),
        QdrantClient(
            settings.require_qdrant_url(),
            settings.require_qdrant_api_key(),
            settings.qdrant_collection,
        ),
    )
