"""Ports required by taste-onboarding use cases."""

from typing import Protocol
from uuid import UUID

from app.modules.onboarding.domain import OnboardingTitle, TitleType


class OnboardingRepository(Protocol):
    def rating_count(self, user_id: UUID) -> int: ...

    def popular_unrated_titles(
        self, user_id: UUID, title_type: TitleType, limit: int
    ) -> list[OnboardingTitle]: ...

    def search_unrated_titles(
        self, user_id: UUID, query: str, title_type: TitleType | None, limit: int
    ) -> list[OnboardingTitle]: ...
