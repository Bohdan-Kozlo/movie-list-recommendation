"""Validation and HTTP mapping for a temporary viewing request."""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.modules.recommendations.dto import SimilarTitleResponse, to_title_response
from app.modules.recommendations.tonight import TonightPreferences, TonightRecommendations


class TonightRequest(BaseModel):
    type: Literal["movie", "tv"] = "movie"
    genres: list[str] = Field(default_factory=list, max_length=30)
    max_minutes: int | None = Field(default=None, ge=1, le=1440)
    year_from: int | None = Field(default=None, ge=1800, le=2100)
    year_to: int | None = Field(default=None, ge=1800, le=2100)
    mode: Literal["familiar", "discover"] = "familiar"

    @model_validator(mode="after")
    def validate_preferences(self) -> Self:
        if (
            self.year_from is not None
            and self.year_to is not None
            and self.year_from > self.year_to
        ):
            raise ValueError("The start year must not be later than the end year.")
        if any(not genre.strip() or len(genre) > 100 for genre in self.genres):
            raise ValueError("Choose valid genre names.")
        return self


def to_tonight_preferences(request: TonightRequest) -> TonightPreferences:
    return TonightPreferences(
        title_type=request.type,
        genres=tuple(dict.fromkeys(genre.strip() for genre in request.genres)),
        max_minutes=request.max_minutes,
        year_from=request.year_from,
        year_to=request.year_to,
        mode=request.mode,
    )


class TonightResponse(BaseModel):
    items: list[SimilarTitleResponse]
    status: Literal["ready", "no_profile", "no_matches"]


def to_tonight_response(result: TonightRecommendations) -> TonightResponse:
    return TonightResponse(
        items=[to_title_response(item) for item in result.items], status=result.status
    )
