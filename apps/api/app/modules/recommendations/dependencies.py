"""Composition root for semantic recommendations."""

from app.adapters.postgres.catalogue_repository import SqlAlchemyCatalogueRepository
from app.adapters.postgres.recommendation_repository import (
    SqlAlchemyPersonalRecommendationRepository,
)
from app.adapters.semantic import create_semantic_index
from app.core.config import Settings
from app.core.database import get_database_engine
from app.modules.recommendations.use_cases import GetPersonalRecommendations, GetSimilarTitles
from app.modules.recommendations.use_cases.get_tonight_recommendations import (
    GetTonightRecommendations,
)


def get_tonight_recommendations_use_case() -> GetTonightRecommendations:
    settings = Settings.from_environment()
    repository = SqlAlchemyPersonalRecommendationRepository(
        get_database_engine(settings.database_url)
    )
    return GetTonightRecommendations(repository, create_semantic_index(settings))


def get_similar_titles_use_case() -> GetSimilarTitles:
    settings = Settings.from_environment()
    catalogue = SqlAlchemyCatalogueRepository(get_database_engine(settings.database_url))
    return GetSimilarTitles(catalogue, create_semantic_index(settings))


def get_personal_recommendations_use_case() -> GetPersonalRecommendations:
    settings = Settings.from_environment()
    repository = SqlAlchemyPersonalRecommendationRepository(
        get_database_engine(settings.database_url)
    )
    return GetPersonalRecommendations(repository, create_semantic_index(settings))
