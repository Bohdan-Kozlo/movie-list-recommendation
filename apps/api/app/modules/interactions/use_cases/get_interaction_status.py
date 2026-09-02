"""Read a user's current interaction state for one title."""

from uuid import UUID

from app.modules.interactions.domain import InteractionStatus
from app.modules.interactions.ports import InteractionRepository
from app.modules.interactions.use_cases._titles import require_title


class GetInteractionStatus:
    def __init__(self, repository: InteractionRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID, title_id: UUID) -> InteractionStatus:
        require_title(self._repository, title_id)
        return self._repository.status(user_id, title_id)
