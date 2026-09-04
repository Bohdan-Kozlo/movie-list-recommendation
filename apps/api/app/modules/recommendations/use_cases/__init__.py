"""Application actions owned by the recommendation module."""

from app.modules.recommendations.use_cases.get_personal_recommendations import (
    GetPersonalRecommendations,
)
from app.modules.recommendations.use_cases.get_similar_titles import GetSimilarTitles
from app.modules.recommendations.use_cases.index_catalogue import IndexCatalogue

__all__ = ["GetPersonalRecommendations", "GetSimilarTitles", "IndexCatalogue"]
