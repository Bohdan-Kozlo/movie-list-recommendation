"""Exclude a title from a user's interest list and watchlist."""

from uuid import UUID

from app.modules.interactions.ports import InteractionRepository
from app.modules.interactions.use_cases._titles import require_title


class AddNotInterested:
    def __init__(self, repository: InteractionRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, title_id: UUID) -> None:
        require_title(self._repository, title_id)
        self._repository.mark_not_interested(user_id, title_id)
