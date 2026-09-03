"""Mappings from canonical title records to taste-onboarding values."""

from typing import cast

from app.modules.catalog.models import CatalogueTitle
from app.modules.onboarding.domain import OnboardingTitle, TitleType


def to_onboarding_title(title: CatalogueTitle) -> OnboardingTitle:
    return OnboardingTitle(
        id=str(title.id),
        title=title.title,
        title_type=cast(TitleType, title.title_type),
        release_date=title.release_date.isoformat() if title.release_date else None,
        original_language=title.original_language,
        poster_path=title.poster_path,
        popularity=title.popularity,
        genres=[genre.name for genre in title.genres],
    )
