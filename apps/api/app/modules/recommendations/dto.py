"""HTTP response mapping for recommendation results."""

from pydantic import BaseModel, ConfigDict, Field

from app.modules.recommendations.domain import SimilarTitle


class SimilarTitleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    title_type: str = Field(serialization_alias="type")
    release_date: str | None = Field(serialization_alias="releaseDate")
    original_language: str = Field(serialization_alias="originalLanguage")
    poster_path: str | None = Field(serialization_alias="posterPath")
    popularity: float
    genres: list[str]
    reason: str


class SimilarTitlesResponse(BaseModel):
    items: list[SimilarTitleResponse]


def to_similar_titles_response(results: list[SimilarTitle]) -> SimilarTitlesResponse:
    return SimilarTitlesResponse(
        items=[
            SimilarTitleResponse(
                id=result.title.id,
                title=result.title.title,
                title_type=result.title.title_type,
                release_date=(
                    result.title.release_date.isoformat() if result.title.release_date else None
                ),
                original_language=result.title.original_language,
                poster_path=result.title.poster_path,
                popularity=result.title.popularity,
                genres=result.title.genres,
                reason=result.reason,
            )
            for result in results
        ]
    )
